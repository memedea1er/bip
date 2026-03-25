from fastapi import APIRouter, HTTPException
from typing import List
from services.notes_service import NotesService
from models import NoteCreate, NoteUpdate, NoteMetadata, NoteWithContent

class NotesController:
    def __init__(self, notes_service: NotesService):
        self.service = notes_service
        self.router = APIRouter(prefix="/notes", tags=["notes"])
        self._register_routes()
    
    def _register_routes(self):
        self.router.post("/", response_model=NoteMetadata)(self.create_note)
        self.router.get("/{note_id}", response_model=NoteWithContent)(self.get_note)
        self.router.put("/{note_id}", response_model=NoteMetadata)(self.update_note)
        self.router.delete("/{note_id}")(self.delete_note)
        self.router.get("/{note_id}/metadata", response_model=NoteMetadata)(self.get_note_metadata)
    
    async def create_note(self, note: NoteCreate):
        return await self.service.create_note(note)
    
    async def get_note(self, note_id: int):
        note = await self.service.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    
    async def update_note(self, note_id: int, note_update: NoteUpdate):
        note = await self.service.update_note(note_id, note_update)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note
    
    async def delete_note(self, note_id: int):
        success = await self.service.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        return {"success": True, "message": f"Note {note_id} deleted"}
    
    async def get_note_metadata(self, note_id: int):
        metadata = await self.service.get_note_metadata(note_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Note not found")
        return metadata