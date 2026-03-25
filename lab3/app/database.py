import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING

class Database:
    client: AsyncIOMotorClient = None
    db = None

db = Database()

async def connect_to_mongo():
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://admin:password123@localhost:27017/")
    database_name = os.getenv("DATABASE_NAME", "movie_db")
    
    db.client = AsyncIOMotorClient(mongodb_url)
    db.db = db.client[database_name]
    
    # Создание индексов для оптимизации запросов
    await create_indexes()
    
    print("Connected to MongoDB")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

async def create_indexes():
    movies_collection = db.db["movies"]
    
    # Создание индексов для часто используемых полей
    indexes = [
        IndexModel([("year", ASCENDING)]),
        IndexModel([("rating", DESCENDING)]),
        IndexModel([("director", ASCENDING)]),
        IndexModel([("genre", ASCENDING)]),
        IndexModel([("status", ASCENDING)]),
        IndexModel([("actors", ASCENDING)]),
        IndexModel([("title", ASCENDING)]),
    ]
    
    try:
        await movies_collection.create_indexes(indexes)
        print("Indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")

def get_database():
    return db.db