from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import connect_to_mongo, close_mongo_connection
from routes import router as movies_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Movie Tracking API",
    description="API для учёта просмотренных фильмов",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router)

@app.get("/")
async def root():
    return {
        "message": "Movie Tracking API",
        "version": "1.0.0",
        "endpoints": {
            "movies": "/movies",
            "create_movie": "POST /movies",
            "get_movies": "GET /movies",
            "count_movies": "GET /movies/count",
            "get_movie": "GET /movies/{id}",
            "update_movie": "PUT /movies/{id}",
            "delete_movie": "DELETE /movies/{id}"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}