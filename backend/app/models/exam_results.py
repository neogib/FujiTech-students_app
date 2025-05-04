from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.schools import Szkola


class PrzedmiotBase(SQLModel):
    nazwa: str = Field(index=True, unique=True)


class Przedmiot(PrzedmiotBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    wyniki_e8: list["WynikE8"] = Relationship(back_populates="przedmiot")  # pyright: ignore[reportAny]
    wyniki_em: list["WynikEM"] = Relationship(back_populates="przedmiot")  # pyright: ignore[reportAny]


class WynikBase(SQLModel):
    liczba_zdajacych: int | None
    wynik_sredni: float | None
    mediana: float | None


class WynikEMExtra(WynikBase):
    zdawalnosc: float | None
    liczba_laueratow_finalistow: int | None


class WynikCommon(WynikBase):
    szkola_id: int = Field(index=True, foreign_key="szkola.id")
    przedmiot_id: int = Field(index=True, foreign_key="przedmiot.id")
    rok: int = Field(index=True)


class WynikE8(WynikCommon, table=True):
    __tablename__: str = "wyniki_e8"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    przedmiot: Przedmiot = Relationship(back_populates="wyniki_e8")  # pyright: ignore[reportAny]
    szkola: "Szkola" = Relationship(back_populates="wyniki_e8")  # pyright: ignore[reportAny]


class WynikEM(WynikCommon, WynikEMExtra, table=True):
    __tablename__: str = "wyniki_em"  # pyright: ignore[reportIncompatibleVariableOverride]
    id: int | None = Field(default=None, primary_key=True)
    przedmiot: Przedmiot = Relationship(back_populates="wyniki_em")  # pyright: ignore[reportAny]
    szkola: "Szkola" = Relationship(back_populates="wyniki_em")  # pyright: ignore[reportAny]
