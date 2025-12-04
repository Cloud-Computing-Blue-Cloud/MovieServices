from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from models.models import Movie, Genre, MovieGenreMapping
from models.movie import MovieCreate, MovieRead, MovieUpdate

router = APIRouter(prefix="/movies", tags=["movies"])


class PageMeta(BaseModel):
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=1)
    has_prev: bool
    has_next: bool


class MoviesPage(BaseModel):
    items: List[MovieRead]
    meta: Optional[PageMeta] = None


@router.post("", response_model=List[MovieRead], status_code=status.HTTP_201_CREATED, summary="(Admin) Add one or more movies")
def create_movie(payload: List[MovieCreate], db: Session = Depends(get_db)) -> List[MovieRead]:
    if not payload:
        raise HTTPException(status_code=400, detail="Payload must be a non-empty list of movies")

    created_movies = []
    # cache for genre name -> Genre object to avoid duplicate queries/inserts inside this request
    genre_cache: dict[str, Genre] = {}

    for item in payload:
        movie = Movie(
            name=item.name,
            runtime_minutes=item.runtime_minutes if item.runtime_minutes is not None else 1,
            release_date=item.release_date,
            rating=item.rating,
            language=item.language,
            is_active=item.is_active,
            created_by=1,
        )

        # attach genres (create if missing) using cache
        genre_objs = []
        for gname in item.genres:
            if gname in genre_cache:
                g = genre_cache[gname]
            else:
                g = db.query(Genre).filter(Genre.genre_name == gname, Genre.is_deleted == False).first()
                if not g:
                    g = Genre(genre_name=gname)
                    db.add(g)
                    db.flush()
                genre_cache[gname] = g
            genre_objs.append(g)

        movie.genres = genre_objs
        db.add(movie)
        created_movies.append(movie)

    # commit once for the batch
    db.commit()

    # refresh instances to populate IDs and timestamps
    for m in created_movies:
        db.refresh(m)

    # build response
    out: List[MovieRead] = []
    for m in created_movies:
        out.append(
            MovieRead(
                movie_id=m.movie_id,
                name=m.name,
                genres=[g.genre_name for g in m.genres],
                runtime_minutes=m.runtime_minutes,
                release_date=m.release_date,
                rating=float(m.rating) if m.rating is not None else None,
                language=m.language,
                is_active=m.is_active,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
        )

    return out


@router.get("", response_model=MoviesPage, summary="List movies with optional filters and pagination")
def list_movies(
    name: Optional[str] = Query(None, description="Case-insensitive substring match on name"),
    genre: Optional[str] = Query(None, description="Filter by a single genre name"),
    language: Optional[str] = Query(None, description="Filter by language"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    # Optional pagination
    page: int = Query(1, ge=1, description="1-based page number (optional)"),
    page_size: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Items per page (max 100). If not provided, returns all results without pagination",
    ),
    db: Session = Depends(get_db),
) -> MoviesPage:
    # Base query (exclude soft-deleted)
    q = db.query(Movie).filter(Movie.is_deleted == False)

    # Apply simple filters
    if name is not None:
        q = q.filter(Movie.name.ilike(f"%{name}%"))

    if language is not None:
        q = q.filter(Movie.language == language)

    if is_active is not None:
        q = q.filter(Movie.is_active == is_active)

    if genre is not None:
        # join to genres and filter by exact genre name
        q = q.join(Movie.genres).filter(Genre.genre_name == genre, Genre.is_deleted == False)

    rows = q.all()

    # Map to MovieRead objects
    vals: List[MovieRead] = []
    for m in rows:
        vals.append(
            MovieRead(
                movie_id=m.movie_id,
                name=m.name,
                genres=[g.genre_name for g in m.genres],
                runtime_minutes=m.runtime_minutes,
                release_date=m.release_date,
                rating=float(m.rating) if m.rating is not None else None,
                language=m.language,
                is_active=m.is_active,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
        )

    # If no pagination requested, return all
    if page_size is None:
        return MoviesPage(items=vals, meta=None)

    # Deterministic sort before slicing (same logic as main pagination)
    def sort_key(m: MovieRead):
        if m.release_date is not None:
            primary = m.release_date.isoformat()
        else:
            primary = m.name.lower()
        return (primary, m.movie_id)

    vals.sort(key=sort_key)

    total = len(vals)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size
    items = vals[start:end] if start < total else []

    meta = PageMeta(
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
        has_prev=page > 1,
        has_next=page < total_pages,
    )

    return MoviesPage(items=items, meta=meta)


@router.get("/{movie_id}", response_model=MovieRead, summary="Get detailed movie info")
def get_movie(movie_id: int, db: Session = Depends(get_db)) -> MovieRead:
    m = db.query(Movie).filter(Movie.movie_id == movie_id, Movie.is_deleted == False).first()
    if not m:
        raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found")
    return MovieRead(
        movie_id=m.movie_id,
        name=m.name,
        genres=[g.genre_name for g in m.genres],
        runtime_minutes=m.runtime_minutes,
        release_date=m.release_date,
        rating=float(m.rating) if m.rating is not None else None,
        language=m.language,
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.put("/{movie_id}", response_model=MovieRead, summary="(Admin) Update a movie")
def update_movie(movie_id: int, payload: MovieUpdate, db: Session = Depends(get_db)) -> MovieRead:
    m = db.query(Movie).filter(Movie.movie_id == movie_id, Movie.is_deleted == False).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movie not found")

    data = payload.model_dump(exclude_unset=True)
    # update scalar fields
    for k, v in data.items():
        if k == "genres":
            # replace genre mapping
            genre_objs = []
            for gname in v:
                g = db.query(Genre).filter(Genre.genre_name == gname, Genre.is_deleted == False).first()
                if not g:
                    g = Genre(genre_name=gname)
                    db.add(g)
                    db.flush()
                genre_objs.append(g)
            m.genres = genre_objs
        else:
            if hasattr(m, k):
                setattr(m, k, v)

    db.commit()
    db.refresh(m)
    return get_movie(movie_id, db)


@router.delete("/{movie_id}", summary="(Admin) Delete a movie")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    m = db.query(Movie).filter(Movie.movie_id == movie_id, Movie.is_deleted == False).first()
    if not m:
        raise HTTPException(status_code=404, detail="Movie not found")
    m.is_deleted = True
    db.commit()
    return {"status": "deleted", "id": movie_id}


@router.post("/{movie_id}/genres/{genre_id}", summary="Add existing genre to movie")
def add_genre(movie_id: int, genre_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.movie_id == movie_id, Movie.is_deleted == False).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    genre = db.query(Genre).filter(Genre.genre_id == genre_id, Genre.is_deleted == False).first()
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    # check existing mapping
    mapping = db.query(MovieGenreMapping).filter(MovieGenreMapping.movie_id == movie_id, MovieGenreMapping.genre_id == genre_id).first()
    if mapping:
        return {"status": "exists"}
    m = MovieGenreMapping(movie_id=movie_id, genre_id=genre_id)
    db.add(m)
    db.commit()
    return {"status": "added"}


@router.delete("/{movie_id}/genres/{genre_id}", summary="Remove genre mapping from movie")
def remove_genre(movie_id: int, genre_id: int, db: Session = Depends(get_db)):
    mapping = db.query(MovieGenreMapping).filter(MovieGenreMapping.movie_id == movie_id, MovieGenreMapping.genre_id == genre_id).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    db.delete(mapping)
    db.commit()
    return {"status": "removed"}
