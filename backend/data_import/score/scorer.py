from typing import cast

from sqlmodel import select

from app.models.exam_results import Przedmiot
from app.models.schools import Szkola
from data_import.utils.db.session import DatabaseManagerBase


class Scorer(DatabaseManagerBase):
    subject_weights_map: dict[str, float]
    szkoly_ids: list[int]
    subjects: list[Przedmiot]

    def __init__(self, subjects_weights_map: dict[str, float]):
        super().__init__()
        self.subject_weights_map = subjects_weights_map
        self.szkoly_ids = []
        self.subjects = []

    def _get_school_ids(self):
        session = self._ensure_session()
        ids_sequence = cast(list[int], session.exec(select(Szkola.id)).all())
        if not ids_sequence:
            raise ValueError("No school IDs found in the database.")
        self.szkoly_ids = ids_sequence

    def _get_subjects(self):
        session = self._ensure_session()
        subject_names = list(self.subject_weights_map.keys())
        statement = select(Przedmiot).where(Przedmiot.nazwa.in_(subject_names))  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownArgumentType]
        self.subjects = list(session.exec(statement).all())

    def initalize_required_data(self):
        self._get_school_ids()
        self._get_subjects()
