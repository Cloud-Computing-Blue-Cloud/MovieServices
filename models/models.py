"""SQLAlchemy ORM models for MovieServices."""

from sqlalchemy import Column, Integer, String, SmallInteger, Date, DateTime, DECIMAL, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base, db


class Movie(Base):
    __tablename__ = "movies"

    movie_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    runtime_minutes = Column(SmallInteger, nullable=False)
    release_date = Column(Date, nullable=True)
    rating = Column(DECIMAL(2, 1), nullable=True)
    language = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    genres = relationship("Genre", secondary="movie_genre_mapping", back_populates="movies")


class Genre(Base):
    __tablename__ = "genres"

    genre_id = Column(Integer, primary_key=True, autoincrement=True)
    genre_name = Column(String(100), nullable=False, unique=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    movies = relationship("Movie", secondary="movie_genre_mapping", back_populates="genres")


class MovieGenreMapping(Base):
    __tablename__ = "movie_genre_mapping"

    movie_id = Column(Integer, ForeignKey("movies.movie_id", ondelete="CASCADE"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genres.genre_id", ondelete="CASCADE"), primary_key=True)
