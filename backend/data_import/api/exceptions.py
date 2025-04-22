class APIException(Exception):
    """Base exception for API-related errors."""

    message: str

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class APIRequestException(APIException):
    """Exception raised when an API request fails."""

    attempts: int

    def __init__(self, message: str, attempts: int = 0):
        self.attempts = attempts
        super().__init__(f"{message} (after {attempts} attempts)")


class SchoolsDataException(APIException):
    """Exception raised when there's an issue with schools data."""

    page: int | None

    def __init__(self, message: str, page: int | None = None):
        self.page = page
        page_info = f"on page {page}" if page is not None else ""
        super().__init__(f"Schools data error {page_info}: {message}")
