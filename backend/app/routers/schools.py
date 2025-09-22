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


@router.get("/", response_model=list[SzkolaPublicShort])
async def read_schools(
    session: SessionDep,
    bounding_box: Annotated[BoundingBox, Query()],
):
    # SQL query to filter schools within bounding box boundaries
    statement = select(Szkola).where(
        (Szkola.geolokalizacja_latitude >= bounding_box.south)
        & (Szkola.geolokalizacja_latitude <= bounding_box.north)
        & (Szkola.geolokalizacja_longitude >= bounding_box.west)
        & (Szkola.geolokalizacja_longitude <= bounding_box.east)
    )
    schools = session.exec(statement).all()
    print("Found schools:", len(schools))
    return schools
