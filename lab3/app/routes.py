from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime

from models import Movie, MovieCreate, MovieUpdate, MovieFilter
from database import get_database

router = APIRouter(prefix="/movies", tags=["movies"])

@router.post("/", response_model=Movie, status_code=201)
async def create_movie(movie: MovieCreate):
    """Создание нового фильма"""
    db = get_database()
    movies_collection = db["movies"]
    
    movie_dict = movie.model_dump()
    movie_dict["created_at"] = datetime.utcnow()
    movie_dict["updated_at"] = datetime.utcnow()
    
    result = await movies_collection.insert_one(movie_dict)
    
    created_movie = await movies_collection.find_one({"_id": result.inserted_id})
    created_movie["_id"] = str(created_movie["_id"])
    return Movie(**created_movie)

@router.get("/", response_model=List[Movie])
async def get_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    year_start: Optional[int] = Query(None, ge=1888, le=2030),
    year_end: Optional[int] = Query(None, ge=1888, le=2030),
    rating_min: Optional[float] = Query(None, ge=0, le=10),
    actor: Optional[str] = None,
    director: Optional[str] = None,
    genre: Optional[str] = None,
    status: Optional[bool] = None
):
    """Получение списка фильмов с фильтрацией"""
    db = get_database()
    movies_collection = db["movies"]
    
    # Создаём фильтр
    movie_filter = MovieFilter(
        year_start=year_start,
        year_end=year_end,
        rating_min=rating_min,
        actor=actor,
        director=director,
        genre=genre,
        status=status
    )
    
    query = movie_filter.to_query()
    
    cursor = movies_collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
    movies = await cursor.to_list(length=limit)
    
    # Преобразуем ObjectId в строку
    for movie in movies:
        movie["_id"] = str(movie["_id"])
    
    return [Movie(**movie) for movie in movies]

@router.get("/count", response_model=Dict[str, int])
async def count_movies(
    year_start: Optional[int] = Query(None, ge=1888, le=2030),
    year_end: Optional[int] = Query(None, ge=1888, le=2030),
    rating_min: Optional[float] = Query(None, ge=0, le=10),
    actor: Optional[str] = None,
    director: Optional[str] = None,
    genre: Optional[str] = None,
    status: Optional[bool] = None
):
    """Подсчёт количества фильмов по критериям"""
    db = get_database()
    movies_collection = db["movies"]
    
    movie_filter = MovieFilter(
        year_start=year_start,
        year_end=year_end,
        rating_min=rating_min,
        actor=actor,
        director=director,
        genre=genre,
        status=status
    )
    
    query = movie_filter.to_query()
    count = await movies_collection.count_documents(query)
    
    return {"count": count}

@router.get("/{movie_id}", response_model=Movie)
async def get_movie(movie_id: str):
    """Получение фильма по ID"""
    db = get_database()
    movies_collection = db["movies"]
    
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=400, detail="Invalid movie ID")
    
    movie = await movies_collection.find_one({"_id": ObjectId(movie_id)})
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie["_id"] = str(movie["_id"])
    return Movie(**movie)

@router.put("/{movie_id}", response_model=Movie)
async def update_movie(movie_id: str, movie_update: MovieUpdate):
    """Обновление фильма"""
    db = get_database()
    movies_collection = db["movies"]
    
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=400, detail="Invalid movie ID")
    
    # Проверяем существование фильма
    existing_movie = await movies_collection.find_one({"_id": ObjectId(movie_id)})
    if not existing_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # Подготавливаем данные для обновления
    update_data = movie_update.model_dump(exclude_unset=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    await movies_collection.update_one(
        {"_id": ObjectId(movie_id)},
        {"$set": update_data}
    )
    
    updated_movie = await movies_collection.find_one({"_id": ObjectId(movie_id)})
    updated_movie["_id"] = str(updated_movie["_id"])
    return Movie(**updated_movie)

@router.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: str):
    """Удаление фильма"""
    db = get_database()
    movies_collection = db["movies"]
    
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=400, detail="Invalid movie ID")
    
    result = await movies_collection.delete_one({"_id": ObjectId(movie_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    return None

@router.get("/stats/actors/{actor_name}", response_model=Dict[str, Any])
async def get_actor_stats(actor_name: str):
    """Статистика по актёру"""
    db = get_database()
    movies_collection = db["movies"]
    
    # Количество фильмов с актёром
    count = await movies_collection.count_documents({"actors": {"$in": [actor_name]}})
    
    # Средняя оценка фильмов с актёром
    pipeline = [
        {"$match": {"actors": {"$in": [actor_name]}}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
    ]
    
    result = await movies_collection.aggregate(pipeline).to_list(length=1)
    avg_rating = result[0]["avg_rating"] if result else 0
    
    return {
        "actor": actor_name,
        "movies_count": count,
        "average_rating": round(avg_rating, 2)
    }

@router.get("/stats/director/{director_name}", response_model=Dict[str, Any])
async def get_director_stats(director_name: str):
    """Статистика по режиссёру"""
    db = get_database()
    movies_collection = db["movies"]
    
    count = await movies_collection.count_documents({"director": director_name})
    
    pipeline = [
        {"$match": {"director": director_name}},
        {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
    ]
    
    result = await movies_collection.aggregate(pipeline).to_list(length=1)
    avg_rating = result[0]["avg_rating"] if result else 0
    
    return {
        "director": director_name,
        "movies_count": count,
        "average_rating": round(avg_rating, 2)
    }