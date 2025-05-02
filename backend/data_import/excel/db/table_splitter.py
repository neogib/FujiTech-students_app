# pyright: reportExplicitAny=false, reportAny=false
import logging
from collections.abc import Hashable
from typing import Any

import pandas as pd
from pydantic import ValidationError
from sqlalchemy import Engine
from sqlmodel import Session

from app.models.exam_results import Przedmiot, WynikBase, WynikE8, WynikEM, WynikEMExtra
from app.models.schools import Szkola
from data_import.core.config import ExamType
from data_import.utils.clean_column_names import clean_column_name
from data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class TableSplitter(DatabaseManagerBase):
    engine: Engine
    session: Session | None
    exam_data: pd.DataFrame
    rspo_col_name: tuple[str, str] = ("", "")
    unique_subjects: set[str]
    exam_type: ExamType
    przedmioty_cache: dict[str, Przedmiot]
    processed_count: int = 0
    skipped_schools: int = 0
    added_results: int = 0

    def __init__(self, exam_data: pd.DataFrame, exam_type: ExamType):
        super().__init__()
        self.exam_data = exam_data
        self.exam_type = exam_type
        self.unique_subjects = set()
        self.przedmioty_cache = {}

    def initialize(self) -> bool:
        """Perform initialization and validation steps.
        Returns True if successful, False otherwise."""
        try:
            self._get_rspo_col_name()
            self._get_subjects_names()
            return True
        except ValueError as e:
            logger.error(f"❌ Error during initialization: {e}. Skipping this file...")
            return False

    def _get_rspo_col_name(self):
        rspo_cols = [
            col
            for col in self.exam_data.columns
            if isinstance(col, tuple) and "RSPO" in col
        ]
        if len(rspo_cols) != 1:
            raise ValueError("Exactly one column with 'RSPO' in its name is expected.")
        self.rspo_col_name = rspo_cols[0]

    def _get_subjects_names(self):
        """
        Extracts unique subject names from the multi-level column index,
        prunes exam data to include only subjects of interest.
        Assumes subject names are in the first level.
        """

        # Iterate through columns to find subjects (assuming they are level 0 of multi-index)
        for col in self.exam_data.columns:
            # Check if it's a tuple (multi-index) and not unnamed/metadata column which can be skipped
            if (
                isinstance(col, tuple)
                and len(col) > 1
                and not str(col[0]).startswith("Unnamed")
            ):
                self.unique_subjects.add(str(col[0]))

        logger.info(f"ℹ️ Identified subjects: {self.unique_subjects}")  # noqa: RUF001
        cols_to_keep = [*self.unique_subjects, self.rspo_col_name[0]]

        # slicing of self.exam_data to get only exam results + rspo column
        self.exam_data = self.exam_data.loc[:, cols_to_keep]

    def get_subject(self, subject_name: str) -> Przedmiot:
        """Gets a Przedmiot record in the database. If it does not exist, creates it."""
        if subject_name in self.przedmioty_cache:
            return self.przedmioty_cache[subject_name]

        przedmiot = self._select_where(Przedmiot, Przedmiot.nazwa == subject_name)
        if przedmiot:
            self.przedmioty_cache[subject_name] = przedmiot
            return przedmiot

        # no record found
        self.create_subject(subject_name)
        return self.przedmioty_cache[subject_name]

    def create_subject(self, subject_name: str):
        """Creates a Przedmiot record in the database."""
        logger.info(f"➕ Creating new Przedmiot: {subject_name}")  # noqa: RUF001
        przedmiot = Przedmiot(nazwa=subject_name)
        self.przedmioty_cache[subject_name] = przedmiot

    def create_all_subjects(self):
        """Creates Przedmiot records for all unique subjects."""
        for subject_name in self.unique_subjects:
            self.create_subject(clean_column_name(subject_name))

    def get_school_rspo_number(
        self, school_exam_data: pd.Series[Any], index: Hashable
    ) -> int | None:
        # Extract RSPO number from the current row
        rspo = school_exam_data.loc[self.rspo_col_name]

        if pd.isna(rspo):
            self.skip_school(f"⚠️ RSPO number not found in row {index}.")
            return None
        return int(rspo)

    def get_school(self, rspo: int) -> Szkola | None:
        szkola = self._select_where(Szkola, Szkola.numer_rspo == rspo)
        if not szkola:
            self.skip_school(f"⚠️ School with RSPO {rspo} not found in database.")
        return szkola

    def skip_school(self, message: str):
        logger.warning(f"{message} Skipping results for this row.")
        self.skipped_schools += 1

    def create_result_record(
        self,
        subject_exam_result: dict[str, int | float],
        szkola: Szkola,
        przedmiot: Przedmiot,
        base: type[WynikBase | WynikEMExtra],
        table: type[WynikE8 | WynikEM],
    ) -> WynikE8 | WynikEM | None:
        session = self._ensure_session()
        try:
            wynik_base = base.model_validate(subject_exam_result)
        except ValidationError as e:
            logger.error(
                f"❌ Invalid subject data: {e}, School data: {subject_exam_result}"
            )
            return None
        wynik = table(
            szkola=szkola,
            przedmiot=przedmiot,
            **wynik_base.model_dump(),
        )
        session.add(wynik)
        self.added_results += 1
        return wynik

    def create_results(
        self, school_exam_data: pd.Series[Any], szkola: Szkola, rspo: int
    ):
        session = self._ensure_session()
        for subject_name in self.unique_subjects:
            przedmiot = self.get_subject(clean_column_name(subject_name))

            subject_exam_result: dict[str, int | float] = (
                school_exam_data.loc[subject_name]
            ).to_dict()
            subject_exam_result = {
                clean_column_name(k): v for k, v in subject_exam_result.items()
            }

            match self.exam_type:
                case ExamType.E8:
                    wynik = self.create_result_record(
                        subject_exam_result, szkola, przedmiot, WynikBase, WynikE8
                    )
                    if not wynik:
                        continue
                case ExamType.EM:
                    wynik = self.create_result_record(
                        subject_exam_result, szkola, przedmiot, WynikEMExtra, WynikEM
                    )
                    if not wynik:
                        continue
            session.commit()
            session.refresh(wynik)
            logger.info(f"💾 Added new exam result: {wynik.przedmiot} (RSPO: {rspo})")

    def split_exam_results(self):
        """
        Iterates through exam data, finds corresponding schools and subjects,
        creates WynikE8/WynikEM records, and adds them to the DB session.
        """
        self.create_all_subjects()
        logger.info(
            f"📊 Starting processing of {self.exam_type} results for {len(self.exam_data)} schools..."
        )

        for index, school_exam_data in self.exam_data.iterrows():  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            school_exam_data: pd.Series[Any]
            try:
                # Find School by RSPO
                rspo = self.get_school_rspo_number(school_exam_data, index)
                if not rspo:
                    continue

                szkola = self.get_school(rspo)
                if not szkola:
                    continue

                # Process results for each subject for this school
                self.create_results(school_exam_data, szkola, rspo)

                self.processed_count += 1
                if self.processed_count % 100 == 0:  # Log progress periodically
                    logger.info(
                        f"⏳ Processed {self.processed_count} schools... Added {self.added_results} results so far."
                    )

            except Exception as e:
                logger.exception(f"📛 Unexpected error processing row {index}: {e}")
                self.skipped_schools += (
                    1  # Count as skipped if major error occurs for the row
                )

        logger.info(f"✅ Successfully processed {self.processed_count} schools.")
        logger.info(f"ℹ️ Added {self.added_results} new exam results to the session.")  # noqa: RUF001
        logger.info(
            f"ℹ️ Skipped {self.skipped_schools} schools due to missing/invalid RSPO, school not found in DB, or row processing error."  # noqa: RUF001
        )
