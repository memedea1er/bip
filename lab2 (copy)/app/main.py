from fastapi import FastAPI
from contextlib import asynccontextmanager
from containers import Container
from controllers.redis_controller import RedisController
from controllers.notes_controller import NotesController

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    container = app.container
    await container.database().init_db()
    
    # Test Redis connection
    redis_client = container.redis_client()
    if await redis_client.ping():
        print("Redis connected successfully")
    else:
        print("Warning: Redis connection failed")
    
    yield
    
    # Shutdown
    await redis_client.close()

def create_app() -> FastAPI:
    # Create container
    container = Container()
    
    # Load configuration
    container.config.redis.host.from_env("REDIS_HOST", "localhost")
    container.config.redis.port.from_env("REDIS_PORT", 6379)
    container.config.database.url.from_env("DATABASE_URL", "sqlite+aiosqlite:///./notes.db")
    
    # Create FastAPI app
    app = FastAPI(
        title="Redis Notes API",
        description="HTTP API for Redis operations and note management with caching",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Set container
    app.container = container
    
    # Register controllers
    redis_controller = container.redis_controller()
    notes_controller = container.notes_controller()
    
    app.include_router(redis_controller.router)
    app.include_router(notes_controller.router)
    
    @app.get("/")
    async def root():
        return {
            "message": "Redis Notes API",
            "endpoints": {
                "redis": "/redis",
                "notes": "/notes"
            }
        }
    
    return app

app = create_app()