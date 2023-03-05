from source.db.models import *


async def note_to_text(note: NoteInDB, created_by: UserInDB, watchers: list[NoteWatcherInDB]):
    return f"Название: {note.title}\nТекст: {note.note}\nСоздатель:"