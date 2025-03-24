from geoalchemy2 import Geometry
from pydantic import EmailStr
from sqlmodel import Column, Field, SQLModel


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


class Szkoly(SzkolyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
