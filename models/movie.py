# models/movie.py
from __future__ import annotations

from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, HttpUrl


# ----------------------- Enums -----------------------
# class ParentalRating(str, Enum):
#     G = "G"
#     PG = "PG"
#     PG_13 = "PG-13"
#     R = "R"
#     NC_17 = "NC-17"
#     UNRATED = "UNRATED"


class Genre(str, Enum):
    ACTION = "Action"
    ADVENTURE = "Adventure"
    ANIMATION = "Animation"
    COMEDY = "Comedy"
    CRIME = "Crime"
    DOCUMENTARY = "Documentary"
    DRAMA = "Drama"
    FAMILY = "Family"
    FANTASY = "Fantasy"
    HISTORY = "History"
    HORROR = "Horror"
    MUSIC = "Music"
    MYSTERY = "Mystery"
    ROMANCE = "Romance"
    SCI_FI = "Sci-Fi"
    THRILLER = "Thriller"
    WAR = "War"
    WESTERN = "Western"


# -------------------- Subdocuments -------------------
class CastMember(BaseModel):
    name: str = Field(..., description="Performer name", json_schema_extra={"example": "Cillian Murphy"})
    role: Optional[str] = Field(
        None,
        description="Character/credited role",
        json_schema_extra={"example": "J. Robert Oppenheimer"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"name": "Emily Blunt", "role": "Katherine Oppenheimer"},
                {"name": "Robert Downey Jr.", "role": "Lewis Strauss"},
            ]
        }
    }


# ---------------------- Movie I/O ---------------------
class MovieBase(BaseModel):
    genres: List[Genre] = Field(default_factory=list, description="One or more genres")
    runtime_minutes: Optional[int] = Field(None, ge=1, description="Runtime in minutes", json_schema_extra={"example": 180})
    release_date: Optional[date] = Field(None, description="Release date", json_schema_extra={"example": "2023-07-21"})
    name : str = Field(..., description="Movie title", json_schema_extra={"example": "Oppenheimer"})
    rating: float = Field(..., ge=0.0, le=5.0, description="Movie rating", json_schema_extra={"example": 3.5})
    language: str = Field(..., description="Language of the movie", json_schema_extra={"example": "English"})
    is_active: bool = Field(..., description="Is the movie currently active", json_schema_extra={"example": True})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Oppenheimer",
                    "genres": ["Drama", "History"],
                    "runtime_minutes": 180,
                    "release_date": "2023-07-21",
                    "rating": 4.5,
                    "language": "English",
                    "is_active": True
                }
            ]
        }
    }


class MovieCreate(MovieBase):
    """Creation payload (matches your AuthorCreate/BookCreate style)."""
    pass


class MovieUpdate(BaseModel):
    """Partial update (if you add PUT/PATCH later)."""
    genres: Optional[List[Genre]] = Field(None, description="One or more genres")
    runtime_minutes: Optional[int] = Field(None, ge=1, description="Runtime in minutes", json_schema_extra={"example": 180})
    release_date: Optional[date] = Field(None, description="Release date", json_schema_extra={"example": "2023-07-21"})
    name : Optional[str] = Field(None, description="Movie title", json_schema_extra={"example": "Oppenheimer"})
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Movie rating", json_schema_extra={"example": 3.5})
    language: Optional[str] = Field(None, description="Language of the movie", json_schema_extra={"example": "English"})
    is_active: Optional[bool] = Field(None, description="Is the movie currently active", json_schema_extra={"example": True})


class MovieRead(MovieBase):
    movie_id: UUID = Field(default_factory=uuid4, description="Server-generated Movie ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time (UTC)")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time (UTC)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "movie_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "name": "Oppenheimer",
                    "genres": ["Drama", "History"],
                    "runtime_minutes": 180,
                    "release_date": "2023-07-21",
                    "rating": 4.5,
                    "language": "English",
                    "is_active": True,
                    "created_at": "2023-10-01T12:00:00Z",
                    "updated_at": "2023-10-01T12:00:00Z"
                }
            ]
        }
    }
