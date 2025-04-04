class APISettings:
    API_SCHOOLS_URL: str = "https://api-rspo.men.gov.pl/api/placowki/"
    HEADERS: dict[str, str] = {"accept": "application/ld+json"}
    START_PAGE: int = 1
    PAGE_LIMIT: int | None = (
        1  # the last page to fetch, later this can be changed or set to None
    )
    MAX_SCHOOLS_SEGMENT: int = 1000


class RetrySettings:
    INITIAL_DELAY: int = 1
    MAX_DELAY: int = 30
    MAX_RETRIES: int = 5
