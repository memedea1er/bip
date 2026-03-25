from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return str(v)

class Movie(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str = Field(..., min_length=1, max_length=200, description="Название фильма")
    studio: str = Field(..., min_length=1, max_length=100, description="Студия")
    year: int = Field(..., ge=1888, le=2030, description="Год съёмки фильма")
    rating: float = Field(..., ge=0, le=10, description="Оценка (0-10)")
    status: bool = Field(..., description="Статус: True - просмотрено, False - нет")
    actors: List[str] = Field(..., min_length=1, description="Список актёров")
    director: str = Field(..., min_length=1, max_length=100, description="Режиссёр")
    genre: str = Field(..., min_length=1, max_length=50, description="Жанр")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class MovieCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    studio: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1888, le=2030)
    rating: float = Field(..., ge=0, le=10)
    status: bool = ...
    actors: List[str] = Field(..., min_length=1)
    director: str = Field(..., min_length=1, max_length=100)
    genre: str = Field(..., min_length=1, max_length=50)

    @field_validator('actors')
    def validate_actors(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one actor is required')
        return v

class MovieUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    studio: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1888, le=2030)
    rating: Optional[float] = Field(None, ge=0, le=10)
    status: Optional[bool] = None
    actors: Optional[List[str]] = Field(None, min_length=1)
    director: Optional[str] = Field(None, min_length=1, max_length=100)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)

class MovieFilter(BaseModel):
    year_start: Optional[int] = Field(None, ge=1888, le=2030)
    year_end: Optional[int] = Field(None, ge=1888, le=2030)
    rating_min: Optional[float] = Field(None, ge=0, le=10)
    actor: Optional[str] = None
    director: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[bool] = None

    def to_query(self):
        query = {}
        
        if self.year_start or self.year_end:
            year_filter = {}
            if self.year_start:
                year_filter["$gte"] = self.year_start
            if self.year_end:
                year_filter["$lte"] = self.year_end
            query["year"] = year_filter
        
        if self.rating_min is not None:
            query["rating"] = {"$gte": self.rating_min}
        
        if self.actor:
            query["actors"] = {"$in": [self.actor]}
        
        if self.director:
            query["director"] = self.director
        
        if self.genre:
            query["genre"] = self.genre
        
        if self.status is not None:
            query["status"] = self.status
        
        return query