import logging
from collections.abc import Iterator
from pathlib import Path

import pandas as pd

from data_import.core.config import ExamType, ExcelFile

logger = logging.getLogger(__name__)


class ExcelReader:
    base_data_path: Path = Path(__file__).parent

    def __init__(self, base_data_path: Path | None = None):
        """
        Initializes the ExcelReader.

        Args:
            base_data_path: The base path where E8_data and EM_data directories reside.
                            Defaults to the script's directory if None.
        """
        if base_data_path is not None:
            self.base_data_path = base_data_path

    def read_files_from_dir(
        self, directory_path: Path
    ) -> Iterator[tuple[int, pd.DataFrame]]:
        for file_path in directory_path.glob("*.xlsx"):
            file_name = file_path.name
            logger.info(f"Reading file: {file_name}")
            df = pd.read_excel(  # pyright: ignore[reportUnknownMemberType]
                file_path,
                sheet_name=ExcelFile.SHEET_NAME,
                header=ExcelFile.HEADER,
            )
            file_number = int(file_name.split(".")[0])
            yield file_number, df

    def load_files(
        self, directory_type: ExamType
    ) -> Iterator[tuple[int, pd.DataFrame]]:
        """
        Loads Excel files from E8 or EM directories
        """
        target_dir = directory_type.value
        path = self.base_data_path / target_dir
        logger.info(f"Loading data from {path}")
        yield from self.read_files_from_dir(path)

        logger.info(f"Finished reading files from {path}")
