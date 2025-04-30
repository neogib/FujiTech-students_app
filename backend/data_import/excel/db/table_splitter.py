import logging

import pandas as pd

logger = logging.getLogger(__name__)


class TableSplitter:
    exam_data: pd.DataFrame
    rspo_index: int
    subjects_list: list[str]

    def __init__(self, exam_data: pd.DataFrame):
        self.exam_data = exam_data
        self.subjects_list = []
        self.get_required_info()

    def get_required_info(self):
        "This loop assumes that rspo number is before results"
        first_subject_index = 0
        for index, col in enumerate(self.exam_data.columns):
            if col[1] == "RSPO":
                self.rspo_index = index
            if not col[0].startswith("Unnamed"):
                if not first_subject_index:
                    first_subject_index = index
                self.subjects_list.append(col[0])
        # transform exam data to get only exam results
        self.exam_data = self.exam_data.iloc[:, first_subject_index:]

    def split_exam_results(self):
        for _, school_exam_data in self.exam_data.iterrows():  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            try:
                rspo = school_exam_data.iloc[self.rspo_index]  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType] # noqa [F841]
            except Exception as e:
                logger.error(f"📛 Error getting RSPO number: {e}")
