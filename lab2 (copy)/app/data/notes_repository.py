from datetime import datetime
from typing import Optional, List
from db import Database
from models import NoteInDB

class NotesRepository:
    def __init__(self, database: Database):
        self.db = database
    
    async def create(self, title: str, content: str) -> NoteInDB:
        now = datetime.utcnow()
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                'INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)',
                (title, content, now, now)
            )
            await conn.commit()
            note_id = cursor.lastrowid
            
            return await self.get_by_id(note_id)
    
    async def get_by_id(self, note_id: int) -> Optional[NoteInDB]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                'SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?',
                (note_id,)
            )
            row = await cursor.fetchone()
            if row:
                return NoteInDB(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
            return None
    
    async def update(self, note_id: int, title: Optional[str], content: Optional[str]) -> Optional[NoteInDB]:
        updates = []
        params = []
        
        if title is not None:
            updates.append('title = ?')
            params.append(title)
        
        if content is not None:
            updates.append('content = ?')
            params.append(content)
        
        if not updates:
            return await self.get_by_id(note_id)
        
        updates.append('updated_at = ?')
        params.append(datetime.utcnow())
        params.append(note_id)
        
        async with self.db.get_connection() as conn:
            await conn.execute(
                f'UPDATE notes SET {", ".join(updates)} WHERE id = ?',
                params
            )
            await conn.commit()
            
            return await self.get_by_id(note_id)
    
    async def delete(self, note_id: int) -> bool:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            await conn.commit()
            return cursor.rowcount > 0
    
    async def get_all(self) -> List[NoteInDB]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute('SELECT id, title, content, created_at, updated_at FROM notes')
            rows = await cursor.fetchall()
            return [
                NoteInDB(
                    id=row['id'],
                    title=row['title'],
                    content=row['content'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                for row in rows
            ]