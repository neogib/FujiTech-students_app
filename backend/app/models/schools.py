from geoalchemy2 import Geometry
from pydantic import EmailStr
from sqlmodel import Column, Field, Relationship, SQLModel

from .locations import Gminy, Miejscowosci, Powiaty, Ulice, Wojewodztwa


class SzkolyBase(SQLModel):
    numer_rspo: int = Field(unique=True, index=True)
    nip: str
    regon: str
    liczba_uczniow: int
    nazwa: str = Field(index=True, max_length=150)
    dyrektor_imie: str | None = Field(default=None, max_length=50)
    dyrektor_nazwisko: str | None = Field(default=None, max_length=50)
    geolokalizacja: Geometry = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326))
    )
    numer_budynku: int
    telefon: str | None = Field(
        default=None,
        max_length=15,  # E.164 standard allows up to 15 digits
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=254,  # RFC 3696 official limit
    )
    strona_internetowa: str | None = Field(default=None, max_length=254)

    # Foreign keys
    wojewodztwo_id: int | None = Field(default=None, foreign_key="wojewodztwa.id")
    powiat_id: int | None = Field(default=None, foreign_key="powiaty.id")
    gmina_id: int | None = Field(default=None, foreign_key="gminy.id")
    miejscowosc_id: int | None = Field(default=None, foreign_key="miejscowosci.id")
    ulica_id: int | None = Field(default=None, foreign_key="ulice.id")


class Szkoly(SzkolyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Relationships
    wojewodztwo: Wojewodztwa | None = Relationship(back_populates="szkola")
    powiat: Powiaty | None = Relationship(back_populates="szkola")
    gmina: Gminy | None = Relationship(back_populates="szkola")
    miejscowosc: Miejscowosci | None = Relationship(back_populates="szkola")
    ulica: Ulice | None = Relationship(back_populates="szkola")
