from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .schools import Szkoly


class WojewodztwaBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True)


class Wojewodztwa(WojewodztwaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    szkola: list["Szkoly"] = Relationship(back_populates="wojewodztwo")
    powiaty: list["Powiaty"] = Relationship(back_populates="wojewodztwo")


class PowiatyBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True)
    wojewodztwo_id: int = Field(foreign_key="wojewodztwa.id")


class Powiaty(PowiatyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    szkola: list["Szkoly"] = Relationship(back_populates="powiat")
    wojewodztwo: Wojewodztwa = Relationship(back_populates="powiaty")
    gminy: list["Gminy"] = Relationship(back_populates="powiat")


class GminyBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True)
    powiat_id: int = Field(foreign_key="powiaty.id")


class Gminy(GminyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    szkola: list["Szkoly"] = Relationship(back_populates="gmina")
    powiat: Powiaty = Relationship(back_populates="gminy")


class MiejscowosciBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True)
    kod_pocztowy: str


class Miejscowosci(MiejscowosciBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="miejscowosc")


class UliceBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True)


class Ulice(UliceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="ulica")
