from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .locations import Miejscowosci, Ulice


class TypySzkolBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nazwa: str = Field(index=True)


class TypySzkol(TypySzkolBase, table=True):
    __tablename__: str = "typy_szkol"  # type: ignore

    szkoly: list["Szkoly"] = Relationship(back_populates="typ")


class StatusPublicznoprawnyBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nazwa: str = Field(index=True)


class StatusPublicznoprawny(StatusPublicznoprawnyBase, table=True):
    __tablename__: str = "status_publicznoprawny"  # type: ignore

    szkoly: list["Szkoly"] = Relationship(back_populates="status")


# link table for connecting EtapyEdukacji and Szkoly
class SzkolyEtapyLink(SQLModel, table=True):
    etap_id: int | None = Field(
        default=None, foreign_key="etapy_edukacji.id", primary_key=True
    )
    szkola_id: int | None = Field(
        default=None, foreign_key="szkoly.id", primary_key=True
    )


class EtapyEdukacjiBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    nazwa: str = Field(index=True)


class EtapyEdukacji(EtapyEdukacjiBase, table=True):
    __tablename__: str = "etapy_edukacji"  # type: ignore

    szkoly: list["Szkoly"] = Relationship(
        back_populates="etapy", link_model=SzkolyEtapyLink
    )


class SzkolyBase(SQLModel):
    numer_rspo: int = Field(unique=True, index=True)
    nip: str | None = Field(default=None, max_length=10)
    regon: str | None = Field(default=None, max_length=9)
    liczba_uczniow: int | None = Field(default=None)
    nazwa: str = Field(index=True, max_length=150)
    dyrektor_imie: str | None = Field(default=None, max_length=50)
    dyrektor_nazwisko: str | None = Field(default=None, max_length=50)
    geolokalizacja_latitude: float
    geolokalizacja_longitude: float
    kod_pocztowy: str | None = Field(default=None, max_length=6)
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

    # Foreign keys
    typ_id: int | None = Field(default=None, foreign_key="typy_szkol.id")
    status_id: int | None = Field(default=None, foreign_key="status_publicznoprawny.id")
    miejscowosc_id: int | None = Field(default=None, foreign_key="miejscowosci.id")
    ulica_id: int | None = Field(default=None, foreign_key="ulice.id")


class Szkoly(SzkolyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    # Relationships - many-to-one
    typ: TypySzkol | None = Relationship(back_populates="szkoly")
    status: StatusPublicznoprawny | None = Relationship(back_populates="szkoly")
    miejscowosc: Miejscowosci | None = Relationship(back_populates="szkoly")
    ulica: Ulice | None = Relationship(back_populates="szkoly")

    # Relationships - many-to-many
    etapy: list[EtapyEdukacji] = Relationship(
        back_populates="szkoly", link_model=SzkolyEtapyLink
    )
