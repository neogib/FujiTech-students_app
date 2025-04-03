from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .schools import Szkoly


class WojewodztwaBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)


class Wojewodztwa(WojewodztwaBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    powiaty: list["Powiaty"] = Relationship(back_populates="wojewodztwo")


class WojewodztwaPublic(WojewodztwaBase):
    id: int


class PowiatyBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)
    wojewodztwo_id: int | None = Field(default=None, foreign_key="wojewodztwa.id")


class Powiaty(PowiatyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    wojewodztwo: Wojewodztwa = Relationship(back_populates="powiaty")
    gminy: list["Gminy"] = Relationship(back_populates="powiat")


class PowiatyPublic(PowiatyBase):
    id: int


class GminyBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)
    powiat_id: int | None = Field(default=None, foreign_key="powiaty.id")


class Gminy(GminyBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    powiat: Powiaty = Relationship(back_populates="gminy")
    miejscowosci: list["Miejscowosci"] = Relationship(back_populates="gmina")


class GminyPublic(GminyBase):
    id: int


class MiejscowosciBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)
    gmina_id: int | None = Field(default=None, foreign_key="gminy.id")


class Miejscowosci(MiejscowosciBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    szkoly: list["Szkoly"] = Relationship(back_populates="miejscowosc")
    gmina: Gminy = Relationship(back_populates="miejscowosci")


class MiejscowosciPublic(MiejscowosciBase):
    id: int


class UliceBase(SQLModel):
    nazwa: str = Field(index=True)
    teryt: str = Field(index=True, unique=True)


class Ulice(UliceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    szkoly: list["Szkoly"] = Relationship(back_populates="ulica")


class UlicePublic(UliceBase):
    id: int
