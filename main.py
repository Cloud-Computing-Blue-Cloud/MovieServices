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
)

app = FastAPI(
    title="Movie Service",
    version="0.1.0",
    description=(
        "Central catalog for all movie information. "
        "Manages name, genres, rating, language, runtime, and release date. "
        "This service does NOT know showtimes or locations."
    ),
)

# In-memory store (same pattern as your Books & Authors code)
movies: Dict[UUID, MovieRead] = {}


# ----------------------- MOVIES -----------------------
@app.get("/movies", response_model=List[MovieRead], summary="List all available movies")
def list_movies(
    name: Optional[str] = Query(
        None, description="Case-insensitive substring match on name"
    ),
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


@app.get(
    "/movies/{movie_id}", response_model=MovieRead, summary="Get detailed movie info"
)
def get_movie(movie_id: UUID) -> MovieRead:
    if movie_id not in movies:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movies[movie_id]


@app.post(
    "/movies",
    response_model=MovieRead,
    status_code=status.HTTP_201_CREATED,
    summary="(Admin) Add a movie",
)
def create_movie(body: MovieCreate) -> MovieRead:
    movie = MovieRead(**body.model_dump())
    # Prevent accidental overwrite if client reuses an ID (shouldn't happen, but safe)
    if movie.movie_id in movies:
        raise HTTPException(status_code=400, detail="Movie with this ID already exists")
    movies[movie.movie_id] = movie
    return movie


# ------------------------ Root ------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Movie Service. See /docs for Swagger UI."}
