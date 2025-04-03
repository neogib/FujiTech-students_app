import requests
from pydantic import ConfigDict, EmailStr
from pydantic.alias_generators import to_camel
from sqlmodel import Field, Relationship, SQLModel

from .locations import Miejscowosci, Ulice


class GeolocationAPIResponse(SQLModel):
    latitude: float
    longitude: float


class TypySzkolBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class TypySzkol(TypySzkolBase, table=True):
    __tablename__: str = "typy_szkol"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkoly"] = Relationship(back_populates="typ")


class TypySzkolPublic(TypySzkolBase):
    id: int


class StatusPublicznoprawnyBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class StatusPublicznoprawny(StatusPublicznoprawnyBase, table=True):
    __tablename__: str = "status_publicznoprawny"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkoly"] = Relationship(back_populates="status")


class StatusPublicznoprawnyPublic(StatusPublicznoprawnyBase):
    id: int


# link table for connecting EtapyEdukacji and Szkoly
class SzkolyEtapyLink(SQLModel, table=True):
    etap_id: int | None = Field(
        default=None, foreign_key="etapy_edukacji.id", primary_key=True
    )
    szkola_id: int | None = Field(
        default=None, foreign_key="szkoly.id", primary_key=True
    )


class EtapyEdukacjiBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class EtapyEdukacji(EtapyEdukacjiBase, table=True):
    __tablename__: str = "etapy_edukacji"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkoly"] = Relationship(
        back_populates="etapy", link_model=SzkolyEtapyLink
    )


class EtapyEdukacjiPublic(EtapyEdukacjiBase):
    id: int


class SzkolyBase(SQLModel):
    numer_rspo: int = Field(unique=True, index=True)
    nazwa: str = Field(index=True, max_length=150)


class SzkolyExtendedData(SzkolyBase):
    nip: str | None = Field(default=None, max_length=10)
    regon: str = Field(max_length=9, unique=True)
    liczba_uczniow: int | None = Field(default=None, ge=0)
    dyrektor_imie: str | None = Field(default=None, max_length=50)
    dyrektor_nazwisko: str | None = Field(default=None, max_length=50)
    kod_pocztowy: str = Field(max_length=6)
    numer_budynku: str | None = Field(default=None, max_length=10)
    numer_lokalu: str | None = Field(default=None, max_length=10)
    telefon: str | None = Field(
        default=None,
        max_length=15,  # E.164 standard allows up to 15 digits
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=254,  # RFC 3696 official limit
    )
    strona_internetowa: str | None = Field(default=None, max_length=254)


def custom_camel(string: str) -> str:
    # First use the original to_camel function
    result = to_camel(string)

    # Then handle the special TERYT case
    if "Teryt" in result:
        result = result.replace("Teryt", "TERYT")

    return result


class SzkolyAPIResponse(SzkolyExtendedData):
    model_config: ConfigDict = ConfigDict(alias_generator=custom_camel)  # pyright: ignore[reportIncompatibleVariableOverride]
    geolokalizacja: GeolocationAPIResponse
    typ: TypySzkolBase
    status_publiczno_prawny: StatusPublicznoprawnyBase
    etapy_edukacji: list[EtapyEdukacjiBase]
    wojewodztwo: str
    wojewodztwo_kod_TERYT: str
    powiat: str
    powiat_kod_TERYT: str
    gmina: str
    gmina_kod_TERYT: str
    miejscowosc: str
    miejscowosc_kod_TERYT: str
    ulica: str
    ulica_kod_TERYT: str


class SzkolyWithKeys(SzkolyExtendedData):
    # Foreign keys
    typ_id: int | None = Field(default=None, foreign_key="typy_szkol.id")
    status_id: int | None = Field(default=None, foreign_key="status_publicznoprawny.id")
    miejscowosc_id: int | None = Field(default=None, foreign_key="miejscowosci.id")
    ulica_id: int | None = Field(default=None, foreign_key="ulice.id")


class SzkolyPublic(SzkolyWithKeys):
    id: int


class Szkoly(SzkolyWithKeys, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Relationships - many-to-one
    typ: TypySzkol = Relationship(back_populates="szkoly")
    status: StatusPublicznoprawny = Relationship(back_populates="szkoly")
    miejscowosc: Miejscowosci = Relationship(back_populates="szkoly")
    ulica: Ulice | None = Relationship(back_populates="szkoly")

    # Relationships - many-to-many
    etapy: list[EtapyEdukacji] = Relationship(
        back_populates="szkoly", link_model=SzkolyEtapyLink
    )
