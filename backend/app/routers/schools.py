from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.bounding_box import BoundingBox
from app.models.schools import Szkola, SzkolaPublic, SzkolaPublicShort

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/schools",
    tags=["schools"],
)


@router.get("/{school_id}", response_model=SzkolaPublic)
async def read_school(school_id: int, session: SessionDep) -> Szkola:
    school = session.get(Szkola, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school


class FilterParams(BoundingBox):
    type: int | None = None


@router.get("/", response_model=list[SzkolaPublicShort])
async def read_schools(
    session: SessionDep,
    filter_query: Annotated[FilterParams, Query()],
):
    # SQL query to filter schools within bounding box boundaries
    statement = select(Szkola).where(
        (Szkola.geolokalizacja_latitude >= filter_query.south)
        & (Szkola.geolokalizacja_latitude <= filter_query.north)
        & (Szkola.geolokalizacja_longitude >= filter_query.west)
        & (Szkola.geolokalizacja_longitude <= filter_query.east)
    )

    # Add type filter if type parameter is provided
    if filter_query.type is not None:
        statement = statement.where(Szkola.typ_id == filter_query.type)

    schools = session.exec(statement).all()
    print("Found schools:", len(schools))
    return schools
