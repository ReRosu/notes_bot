from pydantic import BaseModel

class UserInDB(BaseModel):
    id: int
    tg_id: str
    friends: list[int]


class NoteInDB(BaseModel):
    id: int
    note: str
    creator_id: int


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