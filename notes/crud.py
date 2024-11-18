from notes.schemas import CreateNote


def create_note(note: CreateNote) -> dict:
    note = note.model_dump()
    return {
        "success": True,
        "note": note,
    }
