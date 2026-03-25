import aiosqlite
from datetime import datetime
from contextlib import asynccontextmanager

class Database:
    def __init__(self, db_url: str):
        self.db_url = db_url.replace('sqlite+aiosqlite:///', '')
        
    async def init_db(self):
        async with aiosqlite.connect(self.db_url) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
            await db.commit()
    
    @asynccontextmanager
    async def get_connection(self):
        async with aiosqlite.connect(self.db_url) as conn:
            conn.row_factory = aiosqlite.Row
            yield conn