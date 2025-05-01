import re

from unidecode import unidecode


def clean_column_name(name: str) -> str:
    # Remove polish letters
    name = unidecode(name)

    # Remove percentage signs and parentheses
    name = re.sub(r"[%()]", "", name)

    # Remove leading and trailing whitespace
    name = name.strip()

    # Replace whitespace with underscores
    name = re.sub(r"\s+", "_", name)

    # Convert to lowercase
    name = name.lower()

    return name
