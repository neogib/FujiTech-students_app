from enum import Enum
from typing import ClassVar, final


@final
class ExcelDirectory(Enum):
    E8 = "E8_data"
    EM = "EM_data"


@final
class ExcelFile:
    SHEET_NAME = "SAS"
    HEADER: ClassVar[list[int]] = [0, 1]
