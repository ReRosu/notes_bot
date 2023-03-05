from aiogram.dispatcher.filters.state import StatesGroup, State

class CreateNoteState(StatesGroup):
    write_note = State()
    # add_friends_state = State()

class NoteState(StatesGroup):
    watch_note = State()
    # update_note = State()

class SendFriendRequest(StatesGroup):
    write_user_id = State()

class AcceptFriendRequest(StatesGroup):
    write_user_id = State()
