import logging
import psycopg2
import psycopg2.extras
from source.db.models import *
from typing import Any


class DBFuncs:
    conn: Any

    @classmethod
    def user_exists_by_tg_id(cls, tg_id: str) -> bool:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select exists(select * from users u where u.tg_id = %(tg_id)s) 
        """
        cursor.execute(query, dict(tg_id=tg_id))
        result = cursor.fetchall()
        return result[0]['exists']

    @classmethod
    def get_friends_requests_to_user(cls, user: UserInDB) -> list[FriendRequestInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from friends_requests fr where to_user_id = %(id)s
        """
        cursor.execute(query, dict(id=user.id))
        result = cursor.fetchall()
        return [FriendRequestInDB.parse_obj(x) for x in result]

    @classmethod
    def accept_friend_request(
        cls, 
        request: FriendRequestInDB, 
        user: UserInDB
        ) -> None:
        user.frineds.append(request.from_user_id)
        cls.update_user(upd_user=user)
        cls.delete_friend_request(
            request=request
            )    

    @classmethod
    def delete_friend_request(cls, request: FriendRequestInDB) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        delete from friends_requests where from_user_id=%(from_user_id)s and to_user_id=%(to_user_id)s
        """
        data = request.dict()
        data.pop('id')
        cursor.execute(query, data)  

    @classmethod
    def insert_new_friend_request(cls, to_user_id: int, from_user_id: int) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        insert into friends_requests (to_user_id, from_user_id) values(%(to_user_id)s, %(from_user_id)s)
        """
        data =dict(to_user_id=to_user_id, from_user_id=from_user_id)
        cursor.execute(query, data)  

    @classmethod
    def insert_new_user(cls, tg_id: str) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        insert into users (tg_id, friends) values(%(tg_id)s, %(friends)s)
        """
        data =dict(tg_id=tg_id, friends=[])
        cursor.execute(query, data)  

    @classmethod
    def get_user_notes(cls, user: UserInDB) -> list[NoteInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes nt where nt.creator_id = %(id)s
        """
        cursor.execute(query, dict(id=user.id))
        result = cursor.fetchall()
        return [NoteInDB.parse_obj(x) for x in result]

    @classmethod
    def get_note_by_id(cls, note_id: int) -> NoteInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes nt where nt.id = %(id)s;
        """
        cursor.execute(query, dict(id=note_id))
        result = cursor.fetchall()
        return NoteInDB.parse_obj(result[0])

    @classmethod
    def get_note_watchers_by_note_id(cls, note_id: int) -> list[NoteWatcherInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes_watchers ntw where ntw.note_id = %(id)s;
        """
        cursor.execute(query, dict(id=note_id))
        result = cursor.fetchall()
        return [NoteWatcherInDB.parse_obj(x) for x in result]

    @classmethod
    def delete_note_watcher(cls, note_watcher: NoteWatcherInDB) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        delete from notes_watchers where from_user_id=%(from_user_id)s and to_user_id=%(to_user_id)s
        """
        data = note_watcher.dict()
        cursor.execute(query, data)  
    
    @classmethod
    def update_user(cls, upd_user: UserInDB) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        update users set friends=%(friends)s where id=%(id)s and tg_id=%(tg_id)s
        """
        data = upd_user.dict()
        cursor.execute(query, data)  
    
    @classmethod
    def insert_new_note_watcher(cls, new_note_watcher: NoteWatcherInDB):
        ...

    @classmethod
    def insert_new_note(cls, new_note: NoteInDB):
        ...

    @classmethod
    def update_note(cls, upd_note: NoteInDB):
        ...

    @classmethod
    def get_permission_title(cls, id: int):
        ...
