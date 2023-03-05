from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from source.core.misc import db
from source.db.models import *
from source.bot.states import * 
from source.bot.consts import bot


async def start(msg: Message, state: FSMContext):
    await state.finish()
    user_tg_id = msg.from_user.id
    user_name = msg.from_user.full_name
    if await db.funcs.user_exists_by_tg_id(user_tg_id):
        user = await db.funcs.get_user_by_tg_id(user_tg_id)
        await msg.reply(f"Приветствую {msg.from_user.full_name}!")
    else:
        user: UserInDB = await db.funcs.insert_new_user(user_tg_id)
        await msg.reply(f"Приветствую {msg.from_user.full_name}! Регистрация прошла.")


async def user_notes(msg: Message, state: FSMContext):
    user = await db.funcs.get_user_by_tg_id(msg.from_user.id)
    notes = await db.funcs.get_user_notes(user)
    step = 5
    await msg.reply('Заметки:')
    for i in range(0,len(notes)//step+1):
        if len(notes[i*step:(i+1)*step])>0:
            await msg.answer('\n'.join([f"id:{x.id}, {(x.created_at.strftime('%d-%m-%Y %H:%M'))} - {x.title}" for x in notes[i*step:(i+1)*step]]))
        else:
            break
    await msg.answer('Напишите id заметки которую хотите посмотреть.')
    await state.set_state(NoteState.watch_note.state)

async def user_notes_watching(msg: Message, state: FSMContext):
    user = await db.funcs.get_user_by_tg_id(msg.from_user.id)
    notes = await db.funcs.get_user_notes_watching(user)
    step = 10
    await msg.reply('Заметки:')
    for i in range(0,len(notes)//step, step):
        await msg.answer('\n'.join([f"id:{x.id}, {(x.created_at.strftime('%d-%m-%Y %H:%M'))} - {x.title} созданная @{(await db.funcs.get_user_by_id(x.creator_id)).tg_fullname}" for x in notes[i*step:(i+1)*step]]))

    await msg.answer('Напишите id заметки которую хотите посмотреть.')
    await state.set_state(NoteState.watch_note.state)

async def watch_note(callback: CallbackQuery, state: FSMContext):
    print('in')
    msg = callback.message
    user = await db.funcs.get_user_by_tg_id(msg.from_user.id)
    note_id = int(msg.text)
    note = await db.funcs.get_note_by_id(note_id, user)
    await msg.reply(note.note)
    await callback.answer(note.note)
    await state.finish()


async def new_user_note(msg: Message, state: FSMContext):
    await msg.reply(f"{msg.from_user.full_name}, в следующем сообщении напишите текст заметки.")
    await state.set_state(CreateNoteState.write_note.state)


async def write_text(callback: CallbackQuery, state: FSMContext):
    msg = callback.message
    creator_id = msg.from_user.id
    user = await db.funcs.get_user_by_tg_id(creator_id)
    note = msg.text
    new_note = await db.funcs.insert_new_note(note, user.id)
    note_watchers = [NoteWatcherInDB(user_id=f_id, note_id=new_note.id, permission_type=1) for f_id in user.friends]
    for nw in note_watchers:
        await db.funcs.insert_new_note_watcher(nw)
        nw_user = await db.funcs.get_user_by_id(nw.user_id)
        await bot.send_message(nw_user.tg_id, f"Вы можете просматривать заметку {new_note.title}, созданную {user.tg_fullname}.")
    await msg.reply(f"Заметка создана")
    await state.finish()


async def send_friend_request(msg: Message):
    await msg.reply(f"Отправьте tg id пользователя")
    await SendFriendRequest.write_user_id.set()
    

async def write_user_id_to_friend_request(callback: CallbackQuery, state: FSMContext):
    msg = callback.message
    creator_id = msg.from_user.id
    user = await db.funcs.get_user_by_tg_id(creator_id)
    fr_id = int(msg.text)
    if fr_id == creator_id:
        await msg.reply('Вы не можете отправить запрос в друзья самому себе.')


async def friend_requests(msg: Message):
    user_id = msg.from_user.id
    user = await db.funcs.get_user_by_tg_id(user_id)
    reqs: list[FriendRequestInDB] = await db.funcs.get_friend_requests_to_user(user)
    await msg.reply('Заявки в друзья:\n'+'\n'.join([f"{(await db.funcs.get_user_by_id(fr.from_user_id).tg_fullname)} - tg_id:{(await db.funcs.get_user_by_id(fr.from_user_id).tg_id)}" for fr in reqs]))
    await msg.reply('Напишите tg id человека которого добавите в друзья')
    await AcceptFriendRequest.write_user_id.set()


async def accept_friend_request(callback: CallbackQuery, state: FSMContext):
    msg = callback.message
    user_id = msg.from_user.id
    user = await db.funcs.get_user_by_tg_id(user_id)
    from_user_id = int(msg.text)
    fr = await db.funcs.get_friend_request_by_ids(
        from_tg_id=from_user_id,
        to_tg_id=user_id
    )
    await db.funcs.accept_friend_request(fr, user)


async def close(msg: Message, state: FSMContext):
    await state.finish()
    await msg.reply('Вы вышли в главное меню.')


async def tg_id(msg: Message):
    await msg.reply(f"{msg.from_id}")


def register_users_handlers(dp: Dispatcher):    
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(tg_id, commands=["tg_id"])
    dp.register_message_handler(user_notes, commands=["notes_by_myself"])
    dp.register_message_handler(user_notes_watching, commands=["notes_watching"])
    dp.register_callback_query_handler(watch_note, state=NoteState.watch_note)
    dp.register_message_handler(new_user_note, commands=["new_note"])
    dp.register_callback_query_handler(write_text, state=CreateNoteState.write_note)
    dp.register_message_handler(close, commands=['close'], state='*')