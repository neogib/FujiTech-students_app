from typing import TypedDict


class SchoolDataDict(TypedDict):
    """
    Type definition for school data from API.

    Some fields are required for successful processing, but the
    validation happens at runtime in DatabaseDecomposer._validate_required_school_data()
    """

    # Required fields
    numerRspo: int
    regon: str
    nazwa: str
    wojewodztwo: str
    wojewodztwoKodTERYT: str
    powiat: str
    powiatKodTERYT: str
    gmina: str
    gminaKodTERYT: str
    miejscowosc: str
    miejscowoscKodTERYT: str
    kodPocztowy: str
    geolokalizacja: dict[str, float]
    typ: dict[str, str | int]
    statusPublicznoPrawny: dict[str, str | int]
    etapyEdukacji: list[dict[str, str | int]]

    # Optional fields
    nip: str | None
    liczbaUczniow: int | None
    dyrektorImie: str | None
    dyrektorNazwisko: str | None
    numerBudynku: str | None
    numerLokalu: str | None
    telefon: str | None
    email: str | None
    stronaInternetowa: str | None
    ulica: str | None
    ulicaKodTERYT: str | None
