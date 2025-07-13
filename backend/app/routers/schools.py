from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.core.database import get_session
from app.models.schools import Szkola

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(
    prefix="/schools",
    tags=["schools"],
)


@router.get("/{school_id}")
async def get_school(school_id: int, session: SessionDep):
    school = session.get(Szkola, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="School not found")
    return school
