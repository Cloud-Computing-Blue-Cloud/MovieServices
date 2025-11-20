# main.py
from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, status

from models.movie import (
    MovieCreate,
    MovieRead,
    Genre,
    ParentalRating,
)

from pydantic import BaseModel, Field


app = FastAPI(
    title="Movie Service",
    version="0.1.0",
    description=(
        "Central catalog for all movie information. "
        "Manages title, synopsis, cast, director, genres, and parental ratings. "
        "This service does NOT know showtimes or locations."
    ),
)

# In-memory store (same pattern as your Books & Authors code)
movies: Dict[UUID, MovieRead] = {}


# ========= Pagination Envelope Models =========
class PageMeta(BaseModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=1)
    has_prev: bool
    has_next: bool


class MoviesPage(BaseModel):
    items: List[MovieRead]
    meta: PageMeta


# ----------------------- MOVIES (legacy: list only) -----------------------
@app.get("/movies", response_model=List[MovieRead], summary="List all available movies (no pagination)")
def list_movies(
    title: Optional[str] = Query(None, description="Case-insensitive substring match on title"),
    director: Optional[str] = Query(None, description="Exact director name"),
    genre: Optional[Genre] = Query(None, description="Filter by a single genre"),
    parental_rating: Optional[ParentalRating] = Query(None, description="Filter by parental rating"),
) -> List[MovieRead]:
    vals = list(movies.values())

    if title is not None:
        t = title.lower()
        vals = [m for m in vals if t in m.title.lower()]
    if director is not None:
        vals = [m for m in vals if m.director == director]
    if genre is not None:
        vals = [m for m in vals if genre in m.genres]
    if parental_rating is not None:
        vals = [m for m in vals if m.parental_rating == parental_rating]

    return vals


# ----------------------- MOVIES (paginated envelope) -----------------------
@app.get(
    "/movies/page",
    response_model=MoviesPage,
    summary="List movies with pagination (envelope response)"
)
def list_movies_page(
    # Filters (same as legacy endpoint)
    title: Optional[str] = Query(None, description="Case-insensitive substring match on title"),
    director: Optional[str] = Query(None, description="Exact director name"),
    genre: Optional[Genre] = Query(None, description="Filter by a single genre"),
    parental_rating: Optional[ParentalRating] = Query(None, description="Filter by parental rating"),
    # Pagination params
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
) -> MoviesPage:
    # 1) Start with all movies
    vals = list(movies.values())

    # 2) Apply filters
    if title is not None:
        t = title.lower()
        vals = [m for m in vals if t in m.title.lower()]
    if director is not None:
        vals = [m for m in vals if m.director == director]
    if genre is not None:
        vals = [m for m in vals if genre in m.genres]
    if parental_rating is not None:
        vals = [m for m in vals if m.parental_rating == parental_rating]

    # 3) Deterministic sort BEFORE slicing
    # Prefer release_date if available; otherwise fall back to title then id
    def sort_key(m: MovieRead):
        # If your MovieRead has a release_date: datetime field, use it.
        # If not, this safely falls back to title.
        if hasattr(m, "release_date") and isinstance(getattr(m, "release_date"), datetime):
            primary = m.release_date.isoformat()
        else:
            primary = m.title.lower()
        return (primary, str(m.id))

    vals.sort(key=sort_key)

    # 4) Compute pagination indexes
    total = len(vals)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size

    # 5) Slice (empty list when page is out of range)
    items = vals[start:end] if start < total else []

    # 6) Build meta
    meta = PageMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_prev=page > 1,
        has_next=page < total_pages,
    )

    return MoviesPage(items=items, meta=meta)


# ----------------------- MOVIE DETAIL -----------------------
@app.get("/movies/{movie_id}", response_model=MovieRead, summary="Get detailed movie info")
def get_movie(movie_id: UUID) -> MovieRead:
    if movie_id not in movies:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movies[movie_id]


# ----------------------- MOVIE CREATE -----------------------
@app.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED, summary="(Admin) Add a movie")
def create_movie(body: MovieCreate) -> MovieRead:
    movie = MovieRead(**body.model_dump())
    # Prevent accidental overwrite if client reuses an ID (shouldn't happen, but safe)
    if movie.id in movies:
        raise HTTPException(status_code=400, detail="Movie with this ID already exists")
    movies[movie.id] = movie
    return movie


# ------------------------ Root ------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Movie Service. See /docs for Swagger UI."}
