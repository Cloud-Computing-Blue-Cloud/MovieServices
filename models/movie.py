# models/movie.py
from __future__ import annotations

from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import date, datetime
from pydantic import BaseModel, Field, HttpUrl


# ----------------------- Enums -----------------------
class ParentalRating(str, Enum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"
    UNRATED = "UNRATED"


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
    title: str = Field(..., description="Movie title", json_schema_extra={"example": "Oppenheimer"})
    synopsis: Optional[str] = Field(
        None,
        description="Short plot summary",
        json_schema_extra={"example": "The story of J. Robert Oppenheimer and the atomic bomb."},
    )
    director: str = Field(..., description="Director", json_schema_extra={"example": "Christopher Nolan"})
    cast: List[CastMember] = Field(default_factory=list, description="Cast entries")
    genres: List[Genre] = Field(default_factory=list, description="One or more genres")
    parental_rating: ParentalRating = Field(
        default=ParentalRating.UNRATED,
        description="Parental rating",
        json_schema_extra={"example": "R"},
    )
    runtime_minutes: Optional[int] = Field(None, ge=1, description="Runtime in minutes", json_schema_extra={"example": 180})
    release_date: Optional[date] = Field(None, description="Release date", json_schema_extra={"example": "2023-07-21"})
    poster_url: Optional[HttpUrl] = Field(None, description="Poster URL")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Oppenheimer",
                    "synopsis": "The story of J. Robert Oppenheimer and the atomic bomb.",
                    "director": "Christopher Nolan",
                    "cast": [
                        {"name": "Cillian Murphy", "role": "J. Robert Oppenheimer"},
                        {"name": "Emily Blunt", "role": "Katherine Oppenheimer"}
                    ],
                    "genres": ["Drama", "History"],
                    "parental_rating": "R",
                    "runtime_minutes": 180,
                    "release_date": "2023-07-21",
                    "poster_url": "https://example.com/posters/oppenheimer.jpg"
                }
            ]
        }
    }


class MovieCreate(MovieBase):
    """Creation payload (matches your AuthorCreate/BookCreate style)."""
    pass


class MovieUpdate(BaseModel):
    """Partial update (if you add PUT/PATCH later)."""
    title: Optional[str] = None
    synopsis: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[List[CastMember]] = None
    genres: Optional[List[Genre]] = None
    parental_rating: Optional[ParentalRating] = None
    runtime_minutes: Optional[int] = Field(None, ge=1)
    release_date: Optional[date] = None
    poster_url: Optional[HttpUrl] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"runtime_minutes": 185},
                {"genres": ["Drama"]},
                {"title": "Oppenheimer (Director's Cut)"},
            ]
        }
    }


class MovieRead(MovieBase):
    id: UUID = Field(default_factory=uuid4, description="Server-generated Movie ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time (UTC)")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time (UTC)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "6ac3f6f5-3f32-4b81-8f9b-7f1d9f88a001",
                    "title": "Oppenheimer",
                    "synopsis": "The story of J. Robert Oppenheimer and the atomic bomb.",
                    "director": "Christopher Nolan",
                    "cast": [
                        {"name": "Cillian Murphy", "role": "J. Robert Oppenheimer"},
                        {"name": "Emily Blunt", "role": "Katherine Oppenheimer"}
                    ],
                    "genres": ["Drama", "History"],
                    "parental_rating": "R",
                    "runtime_minutes": 180,
                    "release_date": "2023-07-21",
                    "created_at": "2025-01-15T10:20:30Z",
                    "updated_at": "2025-01-16T12:00:00Z"
                }
            ]
        }
    }
