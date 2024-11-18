from fastapi import APIRouter

from notes.schemas import CreateNote
from notes import crud

router = APIRouter(prefix="/notes")


@router.post("/")
def create_note(note: CreateNote):
    return crud.create_note(note)


@router.get("/")
def list_notes():
    return [
        "Note1",
        "Note2",
    ]


@router.get("/{note_id}")
def get_note_by_id(note_id: int):
    return {
        "note": {
            "id": note_id
        }
    }