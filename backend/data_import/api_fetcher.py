import logging
import sys

import requests

from .config import APISettings

logger = logging.getLogger(__name__)


class HydraResponse:
    """
    Facilitate working with Hydra Web API responses
    """

    def __init__(self, response_json):
        self.raw = response_json

    @property
    def items(self):
        return self.raw.get("hydra:member", [])

    @property
    def next_page_url(self):
        view = self.raw.get("hydra:view", {})
        return view.get("hydra:next")


class SchoolsAPIFetcher:
    def __init__(
        self,
        base_url: str = APISettings.API_SCHOOLS_URL,
        headers: dict[str, str] = APISettings.HEADERS,
    ):
        self.base_url = base_url
        self.headers = headers

    def api_request(self, params: dict[str, int]) -> dict:
        """
        Helper to make API requests
        """
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()  # Raises HTTPError for bad status codes
            return response.json()
        except requests.exceptions.RequestException as err:
            logging.error(f"API Request failed: {err}")
            raise  # Re-raise the exception

    def fetch_schools(self, page: int = 1) -> HydraResponse | None:
        """
        Fetch schools data from one page
        """
        params = {"page": page}

        try:
            data = self.api_request(params)
            hydra_response = HydraResponse(data)
            if hydra_response.items:
                return hydra_response
            return None
        except requests.exceptions.RequestException:
            logging.critical(
                "Fatal error fetching schools data. Terminating program..."
            )
            sys.exit(1)  # Terminate the program with error code if an error occurs

    def fetch_all_schools(self) -> list[dict]:
        """
        Fetch all schools data by paginating through the API
        """
        page = 1
        all_schools = []

        while page:
            reponse = self.fetch_schools(page=page)
            if not reponse:  # no schools on this page
                continue

            # extract schools from reponse
            schools = reponse.items
            all_schools.extend(schools)
            logger.info(f"Fetched {len(schools)} schools from page {page}")

            # check if there are more pages
            if reponse.next_page_url:
                page += 1
            else:
                page = None
                break

            # check if page limit is reached
            if APISettings.PAGE_LIMIT and page > APISettings.PAGE_LIMIT:
                break

        logger.info(f"Finished fetching schools. Total: {len(all_schools)}")
        return all_schools
