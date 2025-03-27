from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .schools import Szkoly


class WojewodztwaBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: int = Field(index=True)


class Wojewodztwa(WojewodztwaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="wojewodztwo")


class PowiatyBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: int = Field(index=True)


class Powiaty(PowiatyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="powiat")


class GminyBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: int = Field(index=True)


class Gminy(GminyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="gmina")


class MiejscowosciBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: int = Field(index=True)
    kod_pocztowy: str


class Miejscowosci(MiejscowosciBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="miejscowosc")


class UliceBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: int = Field(index=True)


class Ulice(UliceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkola: list["Szkoly"] = Relationship(back_populates="ulica")
