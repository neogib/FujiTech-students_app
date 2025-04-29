import logging
from collections.abc import Generator
from pathlib import Path

import pandas as pd

from data_import.core.config import ExcelDirectory, ExcelFile

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

    def read_files_from_dir(self, directory_path: Path) -> Generator[pd.DataFrame]:
        for file_path in directory_path.glob("*.xlsx"):
            logger.info(f"Reading file: {file_path.name}")
            df = pd.read_excel(  # pyright: ignore[reportUnknownMemberType]
                file_path,
                sheet_name=ExcelFile.SHEET_NAME,
                header=ExcelFile.HEADER,
            )
            logger.info(f"First 5 rows:\n{df.head()}")
            yield df

    def load_files(self, directory_type: ExcelDirectory) -> Generator[pd.DataFrame]:
        """
        Loads Excel files from E8 or EM directories
        """
        target_dir = directory_type.value
        path = self.base_data_path / target_dir
        logger.info(f"Loading data from {path}")
        yield from self.read_files_from_dir(path)

        logger.info(f"Finished reading files from {path}")
