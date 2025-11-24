# main.py
from __future__ import annotations
from dotenv import load_dotenv

import os
from typing import Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

from models.movie import (
    MovieCreate,
    MovieRead,
    MovieUpdate,
    Genre,
)
from routers import movies as movies_router
from routers import genres as genres_router

load_dotenv()

port = int(os.environ.get("FASTAPIPORT", 8050))

app = FastAPI(
    title="Movie Service",
    version="0.1.0",
    description=(
        "Central catalog for all movie information. "
        "Manages name, genres, rating, language, runtime, and release date. "
        "This service does NOT know showtimes or locations."
    ),
)

app.include_router(movies_router.router)
app.include_router(genres_router.router)


# ------------------------ Root & Runner ------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the Movie Service. See /docs for Swagger UI."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
