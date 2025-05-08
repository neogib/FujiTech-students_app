import logging
from typing import cast

from sqlmodel import select

from app.models.exam_results import Przedmiot, WynikE8, WynikEM
from app.models.schools import Szkola
from data_import.core.config import SubjectWeights
from data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class Scorer(DatabaseManagerBase):
    subjects_weights_map: dict[str, float]
    schools_ids: list[int]
    subjects: list[Przedmiot]
    years_num: int = 0
    table_type: type[WynikE8 | WynikEM]

    def __init__(
        self, subjects_weights_map: SubjectWeights, table_type: type[WynikE8 | WynikEM]
    ):
        super().__init__()
        self.subjects_weights_map = subjects_weights_map.value
        self.table_type = table_type
        self.schools_ids = []
        self.subjects = []

    def _get_school_ids(self):
        session = self._ensure_session()
        ids = cast(
            list[int], session.exec(select(self.table_type.szkola_id)).unique().all()
        )
        if not ids:
            raise ValueError("No school IDs found in the database.")
        self.schools_ids = ids

    def _get_subjects(self):
        session = self._ensure_session()
        subject_names = list(self.subjects_weights_map.keys())
        statement = select(Przedmiot).where(Przedmiot.nazwa.in_(subject_names))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
        self.subjects = list(session.exec(statement).all())
        if not self.subjects:
            raise ValueError("No subjects found in the database.")

    def _get_number_of_years(self):
        session = self._ensure_session()
        years = session.exec(select(self.table_type.rok)).unique().all()
        if not years:
            raise ValueError("No years found in the database.")
        self.years_num = len(years)

    def _get_subject_score(self, subject: Przedmiot, school_id: int) -> float:
        session = self._ensure_session()
        statement = select(self.table_type).where(
            self.table_type.szkola_id == school_id,
            self.table_type.przedmiot_id == subject.id,
        )
        subject_results = session.exec(statement).all()
        if not subject_results:
            logger.warning(
                f"⚠️ No results found for school: {school_id}, subject: {subject}. The score will be calculated with score 0 from this subject."
            )
            return 0
        # there should be the same amount of records as years
        if len(subject_results) != self.years_num:
            logger.warning(
                f"⚠️ Number of years does not match the number of results, school: {school_id}, subject: {subject}. The score will be calculated on the basis of results not from all years."
            )

        # calculate weighted median
        numerator = 0.0
        denominator = 0.0
        for result in subject_results:
            # For EM have to change it to sredni_wynik
            value = cast(float, result.mediana)
            if not value:  # if there is no median use sredni_wynik
                value = cast(
                    float,
                    result.wynik_sredni
                    if isinstance(result, WynikE8)
                    else result.sredni_wynik,
                )
            numerator += value * result.liczba_zdajacych
            denominator += result.liczba_zdajacych
        return numerator / denominator

    def initalize_required_data(self) -> bool:
        try:
            self._get_school_ids()
            self._get_subjects()
            return True
        except ValueError as e:
            logger.error(
                f"❌ Value Error during initialization: {e}. Skipping scoring schools..."
            )
            return False

    def calculate_scores(self):
        session = self._ensure_session()
        try:
            self._get_number_of_years()  # count all distinct years from the table with scores
        except ValueError as e:
            logger.error(
                f"❌ Error during counting years: {e}. Skipping calculating scores..."
            )
            return
        # then get all records for specific school and specific subject -> calculate score for this subject
        for id in self.schools_ids:
            final_score = 0.0  # final score for every school after calculating results from all subjects
            for subject in self.subjects:
                subject_score = self._get_subject_score(subject, id)
                final_score += subject_score * self.subjects_weights_map[subject.nazwa]
            school = self._select_where(Szkola, Szkola.id == id)
            if not school:
                logger.error(f"❌ School with id: {id} not found in the database.")
                continue
            school.score = final_score
            session.add(school)
            session.commit()
            session.refresh(school)
            logger.info(
                f"✅ School with RSPO: {school.numer_rspo} has been scored. Score: {school.score}"
            )
