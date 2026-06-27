from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from .config import DATABASE_URL


@contextmanager
def get_conn():
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn


def fetch_one(sql: str, params: tuple | list = ()):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def fetch_all(sql: str, params: tuple | list = ()):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def execute(sql: str, params: tuple | list = ()):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            try:
                return cur.fetchone()
            except psycopg.ProgrammingError:
                return None
