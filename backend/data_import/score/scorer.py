import logging
from typing import cast

from sqlmodel import select

from app.models.exam_results import Przedmiot, WynikE8
from data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class Scorer(DatabaseManagerBase):
    subjects_weights_map: dict[str, float]
    schools_ids: list[int]
    subjects: list[Przedmiot]
    years_num: int = 0

    def __init__(self, subjects_weights_map: dict[str, float]):
        super().__init__()
        self.subjects_weights_map = subjects_weights_map
        self.schools_ids = []
        self.subjects = []

    def _get_school_ids(self):
        session = self._ensure_session()
        ids_sequence = cast(
            list[int], session.exec(select(WynikE8.szkola_id)).unique().all()
        )
        if not ids_sequence:
            raise ValueError("No school IDs found in the database.")
        self.schools_ids = ids_sequence

    def _get_subjects(self):
        session = self._ensure_session()
        subject_names = list(self.subjects_weights_map.keys())
        statement = select(Przedmiot).where(Przedmiot.nazwa.in_(subject_names))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
        self.subjects = list(session.exec(statement).all())
        if not self.subjects:
            raise ValueError("No subjects found in the database.")

    def _get_number_of_years(self):
        session = self._ensure_session()
        years = session.exec(select(WynikE8.rok)).unique().all()
        if not years:
            raise ValueError("No years found in the database.")
        self.years_num = len(years)

    def _get_subject_score(self, subject: Przedmiot, school_id: int) -> float:
        session = self._ensure_session()
        # TO DO - calculate it based on chatgpt example
        statement = select(WynikE8).where(
            WynikE8.szkola_id == school_id, WynikE8.przedmiot_id == subject.id
        )
        subject_results = session.exec(statement).all()
        if not subject_results:
            logger.warning(
                f"""⚠️ No results found for school: {school_id}, subject: {subject}. 
                The score will be calculated with score 0 from this subject."""
            )
            return 0
        if len(subject_results) != self.years_num:
            logger.warning(
                f"""⚠️ Number of years does not match the number of results, school: {school_id}, subject: {subject}.
                The score will be calculated on the basis of results not from all years."""
            )

        numerator = 0.0
        denominator = 0.0
        for result in subject_results:
            # For EM have to change it to sredni_wynik
            value = cast(
                float, result.mediana if result.mediana else result.wynik_sredni
            )
            numerator += value * result.liczba_zdajacych
            denominator += result.liczba_zdajacych
        return numerator / denominator

    def calculate_scores(self):
        # first get all distinct years from the table, count them
        try:
            self._get_number_of_years()
        except ValueError as e:
            logger.error(
                f"❌ Error during initialization: {e}. Skipping calculating scores..."
            )
            return
        # then get all records for specific school and specific subject -> calculate score for this subject
        for id in self.schools_ids:
            final_score = 0.0
            for subject in self.subjects:
                # calculate score
                subject_score = self._get_subject_score(subject, id)
                final_score += subject_score * self.subjects_weights_map[subject.nazwa]

        # add this to the main score for the school
        # then do the same thing for the next subject
        # at the end update school column

    def initalize_required_data(self):
        try:
            self._get_school_ids()
            self._get_subjects()
        except ValueError as e:
            logger.error(
                f"❌ Error during initialization: {e}. Skipping scoring schools..."
            )
            return
