import logging
import sys
import time

import requests

from .config import APISettings, RetrySettings

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

    def api_request(self, params: dict[str, int]) -> dict | None:
        """
        Helper to make API requests
        """
        delay = RetrySettings.INITIAL_DELAY
        max_retries = RetrySettings.MAX_RETRIES
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(
                    self.base_url, headers=self.headers, params=params
                )
                response.raise_for_status()  # Raises HTTPError for bad status codes
                return response.json()
            except requests.exceptions.RequestException as err:
                logger.error(
                    f"❌ API Request failed (attempt {attempt + 1}/{max_retries}): {err}"
                )
                if attempt < max_retries:
                    logger.info(f"⏱️⏱️ Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay = min(
                        delay * 2, RetrySettings.MAX_DELAY
                    )  # exponential backoff
                else:
                    raise  # Re-raise the exception after all retries

    def fetch_schools(self, page: int = 1) -> HydraResponse:
        """
        Fetch schools data from one page
        """
        params = {"page": page}

        try:
            data = self.api_request(params)
            hydra_response = HydraResponse(data)
            return hydra_response
        except requests.exceptions.RequestException:
            logging.critical(
                "🚫 Fatal error fetching schools data. Terminating program..."
            )
            sys.exit(1)  # Terminate the program with error code if an error occurs

    def fetch_all_schools(self) -> list[dict]:
        """
        Fetch all schools data by paginating through the API
        """
        page = 1
        all_schools = []

        while page:
            response = self.fetch_schools(page=page)

            # extract schools from reponse
            if response.items:
                schools = response.items
                all_schools.extend(schools)
                logger.info(f"📋 Fetched {len(schools)} schools from page {page}")
            else:
                logging.info(f"ℹ️ No schools found on page {page}")

            # check if page limit is reached
            if APISettings.PAGE_LIMIT and page >= APISettings.PAGE_LIMIT:
                break

            # check if there are more pages
            if not response or response.next_page_url:
                page += 1
            else:  # no more pages
                page = None

        logger.info(f"🏁 Finished fetching schools. Total: {len(all_schools)}")
        return all_schools
