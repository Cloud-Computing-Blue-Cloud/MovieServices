# main.py
from __future__ import annotations

import os
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from models.movie import (
    MovieCreate,
    MovieRead,
    Genre,
)

port = int(os.environ.get("FASTAPIPORT", 8001))

app = FastAPI(
    title="Movie Service",
    version="0.1.0",
    description=(
        "Central catalog for all movie information. "
        "Manages name, genres, rating, language, runtime, and release date. "
        "This service does NOT know showtimes or locations."
    ),
)

# In-memory store
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


# ----------------------- MOVIES (list; unchanged) -----------------------
@app.get("/movies", response_model=List[MovieRead], summary="List all available movies")
def list_movies(
    name: Optional[str] = Query(None, description="Case-insensitive substring match on name"),
    genre: Optional[Genre] = Query(None, description="Filter by a single genre"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
) -> List[MovieRead]:
    vals = list(movies.values())

    if name is not None:
        n = name.lower()
        vals = [m for m in vals if n in m.name.lower()]
    if genre is not None:
        vals = [m for m in vals if genre in m.genres]
    if language is not None:
        vals = [m for m in vals if m.language == language]
    if is_active is not None:
        vals = [m for m in vals if m.is_active == is_active]

    return vals


# ----------------------- MOVIES (paginated envelope) -----------------------
@app.get(
    "/movies/page",
    response_model=MoviesPage,
    summary="List movies with pagination (envelope response)",
)
def list_movies_page(
    # Filters mirror /movies
    name: Optional[str] = Query(None, description="Case-insensitive substring match on name"),
    genre: Optional[Genre] = Query(None, description="Filter by a single genre"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    # Pagination
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
) -> MoviesPage:
    # 1) Start with all movies
    vals = list(movies.values())

    # 2) Apply filters (same logic as /movies)
    if name is not None:
        n = name.lower()
        vals = [m for m in vals if n in m.name.lower()]
    if genre is not None:
        vals = [m for m in vals if genre in m.genres]
    if language is not None:
        vals = [m for m in vals if m.language == language]
    if is_active is not None:
        vals = [m for m in vals if m.is_active == is_active]

    # 3) Deterministic sort before slicing
    # Prefer release_date if present; else fall back to name; tie-break with movie_id
    def sort_key(m: MovieRead):
        if hasattr(m, "release_date") and isinstance(getattr(m, "release_date"), datetime):
            primary = m.release_date.isoformat()
        else:
            primary = m.name.lower()
        # New schema uses movie_id (not id)
        return (primary, str(m.movie_id))

    vals.sort(key=sort_key)

    # 4) Pagination math
    total = len(vals)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size

    # 5) Slice (empty list if out of range)
    items = vals[start:end] if start < total else []

    # 6) Envelope meta
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
@app.post(
    "/movies",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED,
    summary="(Admin) Add a movie",
)
def create_movie(body: MovieCreate) -> MovieRead:
    movie = MovieRead(**body.model_dump())
    # NOTE: new schema uses movie.movie_id as the primary key
    if movie.movie_id in movies:
        raise HTTPException(status_code=400, detail="Movie with this ID already exists")
    movies[movie.movie_id] = movie
    return movie


# ------------------------ Root & Runner ------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Movie Service. See /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
