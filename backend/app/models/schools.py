from geoalchemy2 import Geometry
from sqlmodel import Column, Field, SQLModel


class Szkoly(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    numer_rspo: int = Field(unique=True, index=True)
    nip: str
    regon: str
    liczba_uczniow: int
    nazwa: str = Field(index=True)
    nazwa_skrocona: str = Field(index=True)
    dyrektor_imie: str | None = None
    dyrektor_nazwisko: str | None = None
    geolokalizacja: Geometry = Field(
        sa_column=Column(Geometry(geometry_type="POINT", srid=4326))
    )
    numer_budynku: int
    telefon: str | None = None
    email: str | None = None
    strona_internetowa: str | None = None
