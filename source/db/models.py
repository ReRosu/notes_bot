from pydantic import BaseModel
from datetime import datetime

class UserInDB(BaseModel):
    id: int
    tg_id: int
    friends: list[int]
    tg_fullname: str


class NoteInDB(BaseModel):
    id: int
    note: str
    creator_id: int
    title: str
    created_at: datetime
    is_done: bool


class NoteWatcherInDB(BaseModel):
    user_id: int
    note_id: int
    permission_type: int


class PermissionsInDB(BaseModel):
    id: int
    title: str


class FriendRequestInDB(BaseModel):
    id: int
    to_user_id: int
    from_user_id: int