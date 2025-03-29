import logging

from ..app.core.database import create_db_and_tables
from .api_fetcher import SchoolsAPIFetcher
from .db_decomposer import DatabaseDecomposer

logger = logging.getLogger(__name__)


def configure_logging():
    file_handler = logging.FileHandler("data_import.log")
    stream_handler = logging.StreamHandler()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[file_handler, stream_handler],
    )


def main():
    configure_logging()
    logger.info("Creating database and tables...")
    create_db_and_tables()

    logger.info("Fetching schools data from API...")
    api_fetcher = SchoolsAPIFetcher()
    schools_data = api_fetcher.fetch_all_schools()

    logger.info(f"Seeding {len(schools_data)} schools from API...")
    with DatabaseDecomposer() as decomposer:
        decomposer.prune_and_decompose_schools(schools_data)
    logger.info("Successfully seeded schools")


if __name__ == "__main__":
    main()
