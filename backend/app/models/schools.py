from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .locations import Miejscowosc, Ulica


class TypSzkolyBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class TypSzkoly(TypSzkolyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="typ")  # pyright: ignore [reportAny]


class TypSzkolyPublic(TypSzkolyBase):
    id: int


class StatusPublicznoprawnyBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class StatusPublicznoprawny(StatusPublicznoprawnyBase, table=True):
    __tablename__: str = "status_publicznoprawny"  # pyright: ignore[reportIncompatibleVariableOverride]

    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkola"] = Relationship(back_populates="status_publicznoprawny")  # pyright: ignore [reportAny]


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
    szkoly: list["Szkola"] = Relationship(  # pyright: ignore [reportAny]
        back_populates="etapy_edukacji", link_model=SzkolaEtapLink
    )


class EtapEdukacjiPublic(EtapEdukacjiBase):
    id: int


class SzkolaBase(SQLModel):
    numer_rspo: int = Field(unique=True, index=True)
    nazwa: str = Field(index=True)


class SzkolaExtendedData(SzkolaBase):  # used in SzkolaAPIResponse
    nip: str | None = Field(default=None)
    regon: str = Field(unique=True)
    liczba_uczniow: int | None = Field(default=None, ge=0)
    dyrektor_imie: str | None = Field(default=None)
    dyrektor_nazwisko: str | None = Field(default=None)
    kod_pocztowy: str
    numer_budynku: str | None = Field(default=None)
    numer_lokalu: str | None = Field(default=None)
    telefon: str | None = Field(
        default=None,
    )
    email: str | None = Field(
        default=None,
    )
    strona_internetowa: str | None = Field(default=None)


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
    typ: TypSzkoly = Relationship(back_populates="szkoly")  # pyright: ignore [reportAny]
    status_publicznoprawny: StatusPublicznoprawny = Relationship(  # pyright: ignore [reportAny]
        back_populates="szkoly"
    )
    miejscowosc: "Miejscowosc" = Relationship(back_populates="szkoly")  # pyright: ignore [reportAny]
    ulica: "Ulica | None" = Relationship(back_populates="szkoly")  # pyright: ignore [reportAny]

    # Relationships - many-to-many
    etapy_edukacji: list[EtapEdukacji] = Relationship(  # pyright: ignore [reportAny]
        back_populates="szkoly", link_model=SzkolaEtapLink
    )
