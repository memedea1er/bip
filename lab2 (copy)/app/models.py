from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

# Redis models
class RedisKeyOperation(BaseModel):
    key: str
    value: Any

class RedisHashOperation(BaseModel):
    key: str
    field: str
    value: Any

class RedisListOperation(BaseModel):
    key: str
    value: Any
    index: Optional[int] = None

class RedisExpireOperation(BaseModel):
    key: str
    seconds: int

class RedisIncrementOperation(BaseModel):
    key: str
    amount: int = 1

# Note models
class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteMetadata(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    last_read_at: Optional[datetime] = None

class NoteWithContent(NoteMetadata):
    content: str

class NoteInDB(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True