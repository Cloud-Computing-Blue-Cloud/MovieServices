from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from models.models import Genre

router = APIRouter(prefix="/genres", tags=["genres"])


class GenreCreate(BaseModel):
    genre_name: str = Field(..., description="Name of the genre", example="Comedy")


class GenreRead(BaseModel):
    genre_id: int
    genre_name: str


@router.post("", status_code=201, response_model=GenreRead, summary="Create a genre")
def create_genre(payload: GenreCreate, db: Session = Depends(get_db)):
    name = payload.genre_name
    existing = db.query(Genre).filter(Genre.genre_name == name, Genre.is_deleted == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="Genre already exists")
    g = Genre(genre_name=name)
    db.add(g)
    db.commit()
    db.refresh(g)
    return GenreRead(genre_id=g.genre_id, genre_name=g.genre_name)


@router.get("", response_model=List[GenreRead], summary="List genres")
def list_genres(db: Session = Depends(get_db)):
    gs = db.query(Genre).filter(Genre.is_deleted == False).all()
    return [GenreRead(genre_id=g.genre_id, genre_name=g.genre_name) for g in gs]


@router.get("/{genre_id}", response_model=GenreRead, summary="Get genre by id")
def get_genre(genre_id: int, db: Session = Depends(get_db)):
    g = db.query(Genre).filter(Genre.genre_id == genre_id, Genre.is_deleted == False).first()
    if not g:
        raise HTTPException(status_code=404, detail="Genre not found")
    return GenreRead(genre_id=g.genre_id, genre_name=g.genre_name)


@router.delete("/{genre_id}", summary="Delete (soft) a genre", status_code=status.HTTP_200_OK)
def delete_genre(genre_id: int, db: Session = Depends(get_db)):
    g = db.query(Genre).filter(Genre.genre_id == genre_id, Genre.is_deleted == False).first()
    if not g:
        raise HTTPException(status_code=404, detail="Genre not found")
    g.is_deleted = True
    db.commit()
    return {"status": "deleted", "id": genre_id}
