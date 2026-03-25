from datetime import datetime
from typing import Optional, List
from data.notes_repository import NotesRepository
from data.redis_repository import RedisRepository
from models import NoteMetadata, NoteWithContent, NoteCreate, NoteUpdate

class NotesService:
    def __init__(self, notes_repo: NotesRepository, redis_repo: RedisRepository):
        self.notes_repo = notes_repo
        self.redis_repo = redis_repo
        self.cache_ttl = 3600  # 1 hour cache
    
    def _get_content_cache_key(self, note_id: int) -> str:
        return f"note:content:{note_id}"
    
    def _get_metadata_cache_key(self, note_id: int) -> str:
        return f"note:metadata:{note_id}"
    
    async def create_note(self, note_create: NoteCreate) -> NoteMetadata:
        # Create note in database
        note = await self.notes_repo.create(note_create.title, note_create.content)
        
        # Cache content and metadata
        content_key = self._get_content_cache_key(note.id)
        metadata_key = self._get_metadata_cache_key(note.id)
        
        await self.redis_repo.set_string(content_key, note.content)
        await self.redis_repo.expire(content_key, self.cache_ttl)
        
        # Store metadata in Redis hash
        metadata = {
            "id": str(note.id),
            "title": note.title,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
            "last_read_at": ""
        }
        
        for field, value in metadata.items():
            await self.redis_repo.hset(metadata_key, field, value)
        await self.redis_repo.expire(metadata_key, self.cache_ttl)
        
        return NoteMetadata(
            id=note.id,
            title=note.title,
            created_at=note.created_at,
            updated_at=note.updated_at,
            last_read_at=None
        )
    
    async def get_note(self, note_id: int) -> Optional[NoteWithContent]:
        # Try to get content from cache
        content_key = self._get_content_cache_key(note_id)
        cached_content = await self.redis_repo.get_string(content_key)
        
        # Get metadata from cache or database
        metadata_key = self._get_metadata_cache_key(note_id)
        cached_metadata = await self.redis_repo.hgetall(metadata_key)
        
        now = datetime.utcnow()
        
        if cached_metadata and cached_content:
            # Update last_read_at in cache
            await self.redis_repo.hset(metadata_key, "last_read_at", now.isoformat())
            
            return NoteWithContent(
                id=int(cached_metadata["id"]),
                title=cached_metadata["title"],
                content=cached_content,
                created_at=datetime.fromisoformat(cached_metadata["created_at"]),
                updated_at=datetime.fromisoformat(cached_metadata["updated_at"]),
                last_read_at=now
            )
        
        # Cache miss - get from database
        note = await self.notes_repo.get_by_id(note_id)
        if not note:
            return None
        
        # Update cache
        await self.redis_repo.set_string(content_key, note.content)
        await self.redis_repo.expire(content_key, self.cache_ttl)
        
        metadata = {
            "id": str(note.id),
            "title": note.title,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
            "last_read_at": now.isoformat()
        }
        
        for field, value in metadata.items():
            await self.redis_repo.hset(metadata_key, field, value)
        await self.redis_repo.expire(metadata_key, self.cache_ttl)
        
        return NoteWithContent(
            id=note.id,
            title=note.title,
            content=note.content,
            created_at=note.created_at,
            updated_at=note.updated_at,
            last_read_at=now
        )
    
    async def update_note(self, note_id: int, note_update: NoteUpdate) -> Optional[NoteMetadata]:
        # Update in database
        updated_note = await self.notes_repo.update(
            note_id, 
            note_update.title, 
            note_update.content
        )
        
        if not updated_note:
            return None
        
        # Invalidate and update cache
        content_key = self._get_content_cache_key(note_id)
        metadata_key = self._get_metadata_cache_key(note_id)
        
        # Update content cache if content was updated
        if note_update.content is not None:
            await self.redis_repo.set_string(content_key, updated_note.content)
            await self.redis_repo.expire(content_key, self.cache_ttl)
        
        # Update metadata cache
        if note_update.title is not None:
            await self.redis_repo.hset(metadata_key, "title", updated_note.title)
        
        await self.redis_repo.hset(metadata_key, "updated_at", updated_note.updated_at.isoformat())
        await self.redis_repo.expire(metadata_key, self.cache_ttl)
        
        # Get current metadata
        metadata = await self.redis_repo.hgetall(metadata_key)
        
        return NoteMetadata(
            id=note_id,
            title=metadata.get("title", updated_note.title),
            created_at=datetime.fromisoformat(metadata.get("created_at", updated_note.created_at.isoformat())),
            updated_at=updated_note.updated_at,
            last_read_at=datetime.fromisoformat(metadata["last_read_at"]) if metadata.get("last_read_at") else None
        )
    
    async def delete_note(self, note_id: int) -> bool:
        # Delete from database
        deleted = await self.notes_repo.delete(note_id)
        
        if deleted:
            # Clear cache
            content_key = self._get_content_cache_key(note_id)
            metadata_key = self._get_metadata_cache_key(note_id)
            
            await self.redis_repo.delete_key(content_key)
            await self.redis_repo.delete_key(metadata_key)
        
        return deleted
    
    async def get_note_metadata(self, note_id: int) -> Optional[NoteMetadata]:
        # Try to get metadata from cache
        metadata_key = self._get_metadata_cache_key(note_id)
        cached_metadata = await self.redis_repo.hgetall(metadata_key)
        
        if cached_metadata:
            return NoteMetadata(
                id=int(cached_metadata["id"]),
                title=cached_metadata["title"],
                created_at=datetime.fromisoformat(cached_metadata["created_at"]),
                updated_at=datetime.fromisoformat(cached_metadata["updated_at"]),
                last_read_at=datetime.fromisoformat(cached_metadata["last_read_at"]) if cached_metadata.get("last_read_at") else None
            )
        
        # Cache miss - get from database
        note = await self.notes_repo.get_by_id(note_id)
        if not note:
            return None
        
        # Create metadata without content
        return NoteMetadata(
            id=note.id,
            title=note.title,
            created_at=note.created_at,
            updated_at=note.updated_at,
            last_read_at=None
        )