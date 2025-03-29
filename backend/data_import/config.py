class APISettings:
    API_SCHOOLS_URL: str = "https://api-rspo.men.gov.pl/api/placowki/"
    HEADERS: dict[str, str] = {"accept": "application/ld+json"}
    PAGE_LIMIT: int | None = (
        100  # the last page to fetch, later this can be changed or set to None
    )


class RetrySettings:
    INITIAL_DELAY: int = 1
    MAX_DELAY: int = 30
    MAX_RETRIES: int = 5
