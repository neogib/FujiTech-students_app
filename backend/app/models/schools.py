from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .locations import Miejscowosc, Ulica


class TypBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class Typ(TypBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="typ")


class TypPublic(TypBase):
    id: int


class StatusPublicznoprawnyBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class StatusPublicznoprawny(StatusPublicznoprawnyBase, table=True):
    __tablename__: str = "status_publicznoprawny"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="status_publicznoprawny")


class StatusPublicznoprawnyPublic(StatusPublicznoprawnyBase):
    id: int


# link table for connecting EtapyEdukacji and Szkoly
class SzkolaEtapLink(SQLModel, table=True):
    etap_id: int | None = Field(
        default=None, foreign_key="etap_edukacji.id", primary_key=True
    )
    szkola_id: int | None = Field(
        default=None, foreign_key="szkola.id", primary_key=True
    )


class EtapEdukacjiBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class EtapEdukacji(EtapEdukacjiBase, table=True):
    __tablename__: str = "etap_edukacji"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(
        back_populates="etapy_edukacji", link_model=SzkolaEtapLink
    )


class EtapEdukacjiPublic(EtapEdukacjiBase):
    id: int


class SzkolaBase(SQLModel):
    numer_rspo: int = Field(unique=True, index=True)
    nazwa: str = Field(index=True, max_length=150)


class SzkolaExtendedData(SzkolaBase):  # used in SzkolaAPIResponse
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


class SzkolaAllData(SzkolaExtendedData):
    geolokalizacja_latitude: float
    geolokalizacja_longitude: float
    # Foreign keys
    typ_id: int | None = Field(default=None, foreign_key="typ.id")
    status_publicznoprawny_id: int | None = Field(
        default=None, foreign_key="status_publicznoprawny.id"
    )
    miejscowosc_id: int | None = Field(default=None, foreign_key="miejscowosc.id")
    ulica_id: int | None = Field(default=None, foreign_key="ulica.id")


class SzkolaPublic(SzkolaAllData):
    id: int


class Szkola(SzkolaAllData, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Relationships - many-to-one
    typ: Typ = Relationship(back_populates="szkoly")
    status_publicznoprawny: StatusPublicznoprawny = Relationship(
        back_populates="szkoly"
    )
    miejscowosc: Miejscowosc = Relationship(back_populates="szkoly")
    ulica: Ulica | None = Relationship(back_populates="szkoly")

    # Relationships - many-to-many
    etapy_edukacji: list[EtapEdukacji] = Relationship(
        back_populates="szkoly", link_model=SzkolaEtapLink
    )
