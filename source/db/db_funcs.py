import logging
import psycopg2
import psycopg2.extras
from source.db.models import *
from typing import Any
import json


class DBFuncs:
    conn: Any

    @classmethod
    async def user_exists_by_tg_id(cls, tg_id: int) -> bool:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select exists(select * from users u where u.tg_id = %(tg_id)s);
        """
        cursor.execute(query, dict(tg_id=tg_id))
        result = cursor.fetchall()
        return result[0]['exists']
    
    @classmethod
    async def get_user_by_tg_id(cls, tg_id: int) -> UserInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from users u where u.tg_id = %(tg_id)s;
        """
        cursor.execute(query, dict(tg_id=tg_id))
        result = cursor.fetchall()
        return UserInDB.parse_obj(result[0])

    @classmethod
    async def get_user_by_id(cls, id: int) -> UserInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from users u where u.id = %(id)s;
        """
        cursor.execute(query, dict(id=id))
        result = cursor.fetchall()
        return UserInDB.parse_obj(result[0])

    @classmethod
    async def get_friend_requests_to_user(cls, user: UserInDB) -> list[FriendRequestInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from friends_requests fr where to_user_id = %(id)s
        """
        cursor.execute(query, dict(id=user.id))
        result = cursor.fetchall()
        return [FriendRequestInDB.parse_obj(x) for x in result]

    @classmethod
    async def get_friend_request_by_ids(cls, from_tg_id: int, to_tg_id: int) -> FriendRequestInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from friends_requests fr where to_user_id = %(to_id)s and from_user_id = %(from_id)s
        """
        to_user = cls.get_user_by_tg_id(to_tg_id)
        from_user = cls.get_user_by_tg_id(from_tg_id)
        cursor.execute(query, dict(to_id=to_user.id, from_id=from_user.id))
        result = cursor.fetchall()
        return FriendRequestInDB.parse_obj(result[0])

    @classmethod
    async def accept_friend_request(
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
    async def delete_friend_request(cls, request: FriendRequestInDB) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        delete from friends_requests where from_user_id=%(from_user_id)s and to_user_id=%(to_user_id)s
        """
        data = request.dict()
        data.pop('id')
        cursor.execute(query, data)  

    @classmethod
    async def insert_new_friend_request(cls, to_user_id: int, from_user_id: int) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        insert into friends_requests (to_user_id, from_user_id) values(%(to_user_id)s, %(from_user_id)s)
        """
        data =dict(to_user_id=to_user_id, from_user_id=from_user_id)
        cursor.execute(query, data)  

    @classmethod
    async def insert_new_user(cls, tg_id: int, tg_fullname: str = '') -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        insert into users (tg_id, friends, tg_fullname) values(%(tg_id)s, \'{}\', %(tg_fulllname)s) returning id, tg_id, friends, tg_fullname;
        """
        data =dict(tg_id=tg_id, tg_fullname=tg_fullname)
        cursor.execute(query, data)  
        result = cursor.fetchall()
        return UserInDB.parse_obj(result[0])

    @classmethod
    async def get_user_notes(cls, user: UserInDB) -> list[NoteInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes nt where nt.creator_id = %(id)s
        """
        cursor.execute(query, dict(id=user.id))
        result = cursor.fetchall()
        return [NoteInDB.parse_obj(x) for x in result]
    
    @classmethod
    async def get_user_notes_watching(cls, user: UserInDB) -> list[NoteInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes nt join notes_watchers nw on nw.note_id=nt.id where nw.user_id=%(user_id)s;
        """
        cursor.execute(query, dict(user_id=user.id))
        result = cursor.fetchall()
        return [NoteInDB.parse_obj(x) for x in result]

    @classmethod
    async def get_note_by_id(cls, note_id: int, user: UserInDB) -> NoteInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes nt
            join notes_watchers nw on nw.note_id = nt.id
            where nt.id = %(note_id)s and (nt.creator_id = %(user_id)s or nw.user_id = %(user_id)s);
        """
        cursor.execute(query, dict(note_id=note_id, user_id=user.id))
        result = cursor.fetchall()
        return NoteInDB.parse_obj(result[0])

    @classmethod
    async def get_note_watchers_by_note_id(cls, note_id: int) -> list[NoteWatcherInDB]:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select * from notes_watchers ntw where ntw.note_id = %(id)s;
        """
        cursor.execute(query, dict(id=note_id))
        result = cursor.fetchall()
        return [NoteWatcherInDB.parse_obj(x) for x in result]

    @classmethod
    async def delete_note_watcher(cls, note_watcher: NoteWatcherInDB) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        delete from notes_watchers where from_user_id=%(from_user_id)s and to_user_id=%(to_user_id)s
        """
        data = note_watcher.dict()
        cursor.execute(query, data)  
    
    @classmethod
    async def update_user(cls, upd_user: UserInDB) -> None:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        update users set friends=%(friends)s where id=%(id)s and tg_id=%(tg_id)s
        """
        data = upd_user.dict()
        cursor.execute(query, data)  
    
    @classmethod
    async def insert_new_note_watcher(cls, new_note_watcher: NoteWatcherInDB) -> NoteWatcherInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        insert into notes_watchers (user_id, note_id, permission_type) values(%(user_id)s, %(note_id)s, %(permission_type)s)
        """
        data = new_note_watcher.dict()
        cursor.execute(query, data)  

    @classmethod
    async def insert_new_note(cls, note: str, creator_id: int) -> NoteInDB:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        insert into notes (note, creator_id, title) values(%(note)s, %(creator_id)s, %(title)s) returning id, note, creator_id, title, created_at, is_done;
        """
        data = dict(note=note, creator_id=creator_id, title=' '.join(note.split()[:2]))
        cursor.execute(query, data) 
        result = cursor.fetchall()
        return NoteInDB.parse_obj(result[0])

    @classmethod
    async def update_note(cls, upd_note: NoteInDB):
        ...

    @classmethod
    async def get_permission_title(cls, id: int) -> str:
        cursor = cls.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        query = """
        select p.title from permissions p where p.id = %(id)s;
        """
        cursor.execute(query, dict(id=id))
        result = cursor.fetchall()
        return result['title']
