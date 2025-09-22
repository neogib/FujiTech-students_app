from typing import Self

from pydantic import BaseModel, Field, model_validator


class BoundingBox(BaseModel):
    north: float = Field(ge=-90, le=90)
    south: float = Field(ge=-90, le=90)
    west: float = Field(ge=-180, le=180)
    east: float = Field(ge=-180, le=180)

    @model_validator(mode="after")
    def check_lat_lng(self) -> Self:
        if self.north <= self.south:
            raise ValueError(
                "Top (north) latitude must be greater than bottom (south) latitude."
            )
        if self.west >= self.east:
            raise ValueError(
                "Top-left longitude must be less than bottom-right longitude."
            )

        return self
