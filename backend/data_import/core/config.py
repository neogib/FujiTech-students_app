from enum import Enum
from typing import ClassVar, final


class APISettings:
    API_SCHOOLS_URL: str = "https://api-rspo.men.gov.pl/api/placowki/"
    HEADERS: ClassVar[dict[str, str]] = {"accept": "application/ld+json"}
    START_PAGE: int = 1
    PAGE_LIMIT: int | None = None  # the last page to fetch, if None there is no limit
    MAX_SCHOOLS_SEGMENT: int = 1000


class RetrySettings:
    INITIAL_DELAY: int = 1
    MAX_DELAY: int = 30
    MAX_RETRIES: int = 20


class TIMEOUT:
    CONNECT: int = 30
    READ: int = 60


@final
class ExamType(Enum):
    E8 = "E8_data"
    EM = "EM_data"


@final
class ExcelFile:
    SHEET_NAME = "SAS"
    HEADER: ClassVar[list[int]] = [0, 1]
