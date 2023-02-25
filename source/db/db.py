import psycopg2
import logging
import sys
from source.db.db_funcs import DBFuncs


class DB:
    def __init__(self, dbname, user, password, host, port) -> None:
        try:
            self._conn = psycopg2.connect(
                dbname=dbname, 
                user=user, 
                password=password, 
                host=host, 
                port=port
                )
            self._conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            self.funcs = DBFuncs
            self.funcs.conn = self._conn
        except:
            err = sys.exc_info()
            logging.error(f"psycopg2 connect error {err}")

    @property
    def connection(self):
        return self._conn