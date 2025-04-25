import logging
from pathlib import Path

import pandas as pd

from .core.config import ExcelDirectory

logger = logging.getLogger(__name__)


class ExcelReader:
    base_data_path: Path = Path(__file__).parent
    e8_path: Path
    em_path: Path

    def __init__(self, base_data_path: Path | None = None):
        """
        Initializes the ExcelReader.

        Args:
            base_data_path: The base path where E8_data and EM_data directories reside.
                            Defaults to the script's directory if None.
        """
        if base_data_path is not None:
            self.base_data_path = base_data_path
        self.e8_path = self.base_data_path / ExcelDirectory.E8
        self.em_path = self.base_data_path / ExcelDirectory.EM

    def read_files_from_dir(self, directory_path: Path):
        for file_path in directory_path.glob("*.xlsx"):
            logger.info(f"Reading file: {file_path.name}")
            df = pd.read_excel(file_path)  # pyright: ignore[reportUnknownMemberType]
            logger.info(f"First 5 rows:\n{df.head()}")

    def load_excel_files(self):
        """
        Loads Excel files from E8 and EM directories
        """
        logger.info(f"E8 Data ({self.e8_path})")
        self.read_files_from_dir(self.e8_path)

        logger.info(f"EM Data ({self.em_path})")
        self.read_files_from_dir(self.em_path)

        logger.info("Finished reading all files")
