class APISettings:
    API_SCHOOLS_URL: str = "https://api-rspo.men.gov.pl/api/placowki/"
    HEADERS: dict[str, str] = {"accept": "application/ld+json"}
    PAGE_LIMIT: int | None = (
        10  # the last page to fetch, later this can be changed or set to None
    )
