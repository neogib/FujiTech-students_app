import logging
from typing import cast

from sqlmodel import select

from app.models.exam_results import Przedmiot, WynikE8
from app.models.schools import Szkola
from data_import.score.types import WynikTable
from data_import.utils.db.session import DatabaseManagerBase

logger = logging.getLogger(__name__)


class Scorer(DatabaseManagerBase):
    _subject_weights_map: dict[str, float]
    years_num: int = 0
    _table_type: type[WynikTable]
    _subjects: list[Przedmiot]

    def __init__(
        self,
        subject_weights_map: dict[str, float],
        table_type: type[WynikTable],
    ):
        super().__init__()
        self._subject_weights_map = subject_weights_map
        self._table_type = table_type
        self._subjects = []

    def _load_subjects(self):
        session = self._ensure_session()
        subject_names = list(self._subject_weights_map.keys())
        statement = select(Przedmiot).where(Przedmiot.nazwa.in_(subject_names))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
        self._subjects = list(session.exec(statement).all())
        if not self._subjects:
            raise ValueError("No subjects found in the database.")
        elif len(self._subjects) != len(subject_names):
            raise ValueError(
                f"Not all subjects found in the database. Found: {self._subjects}. Expected: {subject_names}"
            )

    def _load_all_results(self) -> dict[int, dict[int, list[WynikTable]]]:
        """Load all exam results at once and organize by school and subject"""
        session = self._ensure_session()

        # Get subject IDs for our weighted subjects
        self._load_subjects()
        subject_ids = [subject.id for subject in self._subjects]

        # Query all relevant results in one go
        statement = select(self._table_type).where(
            self._table_type.przedmiot_id.in_(subject_ids)  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
        )
        all_results = session.exec(statement).all()

        # Organize results by school_id and subject_id for easy access
        organized_results: dict[int, dict[int, list[WynikTable]]] = {}
        for result in all_results:
            school_id = result.szkola_id
            subject_id = result.przedmiot_id

            if school_id not in organized_results:
                organized_results[school_id] = {}

            if subject_id not in organized_results[school_id]:
                organized_results[school_id][subject_id] = []

            organized_results[school_id][subject_id].append(result)

        return organized_results

    def _calculate_subject_score(self, results: list[WynikTable]) -> float:
        # calculate weighted median
        numerator = 0.0
        denominator = 0.0
        for result in results:
            value = cast(float, result.mediana)
            if not value:  # if there is no median use sredni_wynik for WynikEM and wynik_sredni for WynikE8
                value = cast(
                    float,
                    result.wynik_sredni
                    if isinstance(result, WynikE8)
                    else result.sredni_wynik,
                )
            numerator += value * result.liczba_zdajacych
            denominator += result.liczba_zdajacych

        if denominator == 0:
            logger.warning("No valid denominator for calculating subject score")
            return 0.0

        return numerator / denominator

    def _calculate_school_score(
        self, school_results: dict[int, list[WynikTable]]
    ) -> float:
        """Calculate final score for a school based on subject results"""
        final_score = 0.0

        for subject in self._subjects:
            subject_results = school_results.get(cast(int, subject.id), [])
            if not subject_results:
                logger.warning(f"Subject {subject.nazwa} not found for this school")
                continue
            subject_score = self._calculate_subject_score(subject_results)
            weight = self._subject_weights_map[subject.nazwa]
            final_score += subject_score * weight

        return final_score

    def calculate_scores(self, batch_size: int = 100):
        session = self._ensure_session()

        try:
            results_by_school = self._load_all_results()
            logger.info(f"Loaded results for {len(results_by_school)} schools")
        except ValueError as e:
            logger.error(f"Failed to load results: {e}")
            return

        # Get all schools that have results to update their scores
        school_ids = list(results_by_school.keys())
        schools = session.exec(select(Szkola).where(Szkola.id.in_(school_ids))).all()  # pyright: ignore[reportOptionalMemberAccess, reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]

        school_map = {school.id: school for school in schools}

        success_count = 0
        error_count = 0

        # Process schools in batches
        for i in range(0, len(school_ids), batch_size):
            batch_school_ids = school_ids[i : i + batch_size]

            for school_id in batch_school_ids:
                try:
                    school = school_map[school_id]

                    school_results = results_by_school.get(school_id, {})
                    final_score = self._calculate_school_score(school_results)

                    if not final_score:
                        logger.warning(
                            f"⚠️ School {school.numer_rspo} has no results to score"
                        )
                        continue

                    school.score = final_score
                    session.add(school)
                    success_count += 1

                    logger.info(
                        f"💾 School {school.numer_rspo} scored {final_score:.2f}"
                    )
                except Exception as e:
                    logger.error(f"📛 Unexpected error scoring school {school_id}: {e}")
                    error_count += 1

            # Commit each batch
            session.commit()
            logger.info(f"✅ Schools from batch {i}-{i + batch_size}  has been scored.")
