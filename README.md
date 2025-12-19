# Movie Service - FastAPI

A microservice for managing movie catalog information, including movie details, genres, and metadata, built with **FastAPI**.

## 🚀 Features

- ✅ Movie CRUD operations
- ✅ Genre management
- ✅ Movie filtering (by name, genre)
- ✅ Rating and metadata management
- ✅ **Interactive API documentation** (Swagger UI)
- ✅ **Automatic request validation** (Pydantic)
- ✅ **Google Cloud SQL integration** (MySQL)

## 📋 Project Structure

```
MovieServices/
├── main.py                    # FastAPI application
├── database.py                # SQLAlchemy database setup
├── requirements.txt           # Python dependencies
├── models/
│   ├── movie.py              # Pydantic models and database models
│   └── models.py             # Shared models
└── routers/
    ├── movies.py             # Movie API endpoints
    └── genres.py             # Genre API endpoints
```

## 🛠️ Installation

### Quick Start

1. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Create .env file with database credentials
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name
FASTAPIPORT=5001
```

4. **Run the service:**
```bash
# Option 1: Direct
python main.py

# Option 2: With uvicorn
uvicorn main:app --reload --port 5001
```

The service will start on `http://localhost:5001`

## 📚 Interactive API Documentation

**Visit: http://localhost:5001/docs**

FastAPI provides automatic, interactive API documentation where you can:
- 📖 View all endpoints and schemas
- 🧪 Test APIs directly in your browser
- 📋 See request/response examples
- ✅ Validate data in real-time

Alternative documentation: http://localhost:5001/redoc

## 🔌 API Endpoints

All endpoints are documented interactively at `/docs`. Quick reference:

### Movies

```bash
# List all movies (with optional filters)
GET /movies?name=Oppenheimer&genre=Drama

# Get movie by ID
GET /movies/{movie_id}

# Create movies (201 Created - can create multiple)
POST /movies
[
  {
    "name": "Oppenheimer",
    "genres": ["Drama", "History"],
    "runtime_minutes": 180,
    "release_date": "2023-07-21",
    "rating": 4.5,
    "language": "English",
    "is_active": true
  }
]

# Update movie (partial)
PATCH /movies/{movie_id}
{
  "rating": 4.8,
  "is_active": false
}

# Delete movie (soft delete)
DELETE /movies/{movie_id}
```

### Genres

```bash
# List all genres
GET /genres

# Get genre by ID
GET /genres/{genre_id}

# Create genre (201 Created)
POST /genres
{
  "genre_name": "Sci-Fi"
}

# Delete genre (soft delete)
DELETE /genres/{genre_id}
```

## 🗄️ Database

Uses **Google Cloud SQL (MySQL)** with the following tables:

- **movies** - Movie catalog information
  - `movie_id` (primary key)
  - `name` (title)
  - `genres` (stored as JSON or relationship)
  - `runtime_minutes`
  - `release_date`
  - `rating` (0.0 to 5.0)
  - `language`
  - `is_active`
  - `created_at`, `updated_at`

- **genres** - Genre reference table
  - `genre_id` (primary key)
  - `genre_name` (unique)
  - `is_deleted` (soft deletion)

## ⚙️ Configuration

Environment variables:
```bash
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=3306
DB_NAME=your_db_name
FASTAPIPORT=5001
```

## 🧪 Testing

### Using Swagger UI (Easiest!)
1. Go to http://localhost:5001/docs
2. Click any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Using cURL

```bash
# Health check
curl http://localhost:5001/

# List movies
curl http://localhost:5001/movies

# Create genre (201 Created)
curl -i -X POST http://localhost:5001/genres \
  -H "Content-Type: application/json" \
  -d '{"genre_name": "Thriller"}'

# Create movies (201 Created)
curl -i -X POST http://localhost:5001/movies \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "Inception",
      "genres": ["Sci-Fi", "Action"],
      "runtime_minutes": 148,
      "release_date": "2010-07-16",
      "rating": 4.5,
      "language": "English",
      "is_active": true
    }
  ]'

# Get movie by ID
curl http://localhost:5001/movies/1

# Filter movies by name
curl "http://localhost:5001/movies?name=Inception"

# Filter movies by genre
curl "http://localhost:5001/movies?genre=Sci-Fi"
```

## 🚀 Deployment

### Local Development
```bash
# Auto-reload on code changes
uvicorn main:app --reload --port 5001
```

## 🎯 Key Features

### Automatic Validation
```python
# Pydantic automatically validates all requests
class MovieCreate(BaseModel):
    name: str
    rating: float = Field(..., ge=0.0, le=5.0)  # 0-5 rating
    runtime_minutes: int = Field(..., ge=1)  # Positive integer
    genres: List[str]
```

### Bulk Movie Creation
- `POST /movies` accepts an array of movies
- Returns array of created movies with IDs
- Useful for seeding initial movie data

### Soft Deletion
- Movies and genres are soft-deleted (`is_deleted` flag)
- Deleted items filtered out by default
- Can be restored if needed

### Filtering
- Filter movies by name (case-insensitive substring)
- Filter movies by genre
- Query parameters: `?name=...&genre=...`

## 🤝 Integration with Other Services

- **Frontend (Theatre_UI)**: Movie browsing and search
- **Theatre Service**: References movies for showtimes
- **Booking Service**: Movie information for bookings

## ⚠️ Important Notes

- This service does NOT manage showtimes or locations (handled by Theatre Service)
- Movie ratings are on a 0.0-5.0 scale
- Runtime is stored in minutes
- Genres can be associated with multiple movies

## 📝 Quick Commands

```bash
# Install
pip install -r requirements.txt

# Run
python main.py
# or
uvicorn main:app --reload --port 5001

# View docs
open http://localhost:5001/docs
```

---

**Built with FastAPI** 🚀 | **Version 0.1.0** | **Python 3.11+**

For questions, check the interactive documentation at http://localhost:5001/docs

