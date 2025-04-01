# Constants for the API response keys

from typing import final


@final
class SchoolKeys:
    # School data keys
    RSPO = "numerRspo"
    NAME = "nazwa"
    NIP = "nip"
    REGON = "regon"
    STUDENTS_COUNT = "liczbaUczniow"
    DIRECTOR_FIRST_NAME = "dyrektorImie"
    DIRECTOR_LAST_NAME = "dyrektorNazwisko"
    POSTAL_CODE = "kodPocztowy"
    BUILDING_NUMBER = "numerBudynku"
    APARTMENT_NUMBER = "numerLokalu"
    PHONE = "telefon"
    EMAIL = "email"
    WEBSITE = "stronaInternetowa"

    # Type, status, etapyEdukacji and goeolocation (which are later nested)
    GEOLOCATION = "geolokalizacja"
    TYPE = "typ"
    STATUS = "statusPublicznoPrawny"
    EDUCATION_STAGES = "etapyEdukacji"


@final
class LocationKeys:
    # Location keys
    VOIVODESHIP = "wojewodztwo"
    VOIVODESHIP_TERYT = "wojewodztwoKodTERYT"
    COUNTY = "powiat"
    COUNTY_TERYT = "powiatKodTERYT"
    COMMUNE = "gmina"
    COMMUNE_TERYT = "gminaKodTERYT"
    CITY = "miejscowosc"
    CITY_TERYT = "miejscowoscKodTERYT"
    STREET = "ulica"
    STREET_TERYT = "ulicaKodTERYT"


@final
class NestedKeys:
    # Nested object keys
    GEOLOCATION_LATITUDE = "latitude"
    GEOLOCATION_LONGITUDE = "longitude"
    TYPE_NAME = "nazwa"
    STATUS_NAME = "nazwa"
    EDUCATION_STAGE_NAME = "nazwa"
