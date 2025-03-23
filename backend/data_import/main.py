import logging

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
    logger.info("Starting data import")
    pass


if __name__ == "__main__":
    main()
