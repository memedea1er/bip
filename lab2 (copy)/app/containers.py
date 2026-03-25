from dependency_injector import containers, providers
from redis_client import RedisClient
from db import Database
from data.redis_repository import RedisRepository
from data.notes_repository import NotesRepository
from services.redis_service import RedisService
from services.notes_service import NotesService
from controllers.redis_controller import RedisController
from controllers.notes_controller import NotesController

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[
        "main"
    ])
    
    # Configuration
    config = providers.Configuration()
    
    # Clients
    redis_client = providers.Singleton(
        RedisClient,
        host=config.redis.host,
        port=config.redis.port
    )
    
    database = providers.Singleton(
        Database,
        db_url=config.database.url
    )
    
    # Repositories
    redis_repository = providers.Factory(
        RedisRepository,
        redis_client=redis_client
    )
    
    notes_repository = providers.Factory(
        NotesRepository,
        database=database
    )
    
    # Services
    redis_service = providers.Factory(
        RedisService,
        redis_repository=redis_repository
    )
    
    notes_service = providers.Factory(
        NotesService,
        notes_repo=notes_repository,
        redis_repo=redis_repository
    )
    
    # Controllers
    redis_controller = providers.Factory(
        RedisController,
        redis_service=redis_service
    )
    
    notes_controller = providers.Factory(
        NotesController,
        notes_service=notes_service
    )