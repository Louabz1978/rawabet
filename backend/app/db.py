import re
from collections.abc import Sequence

from sqlalchemy import create_engine, text

from .config import DATABASE_URL

_PLACEHOLDER_RE = re.compile(r"(?<!%)%s(?:::(?P<cast>[a-zA-Z0-9_\[\]]+))?")


def _sqlalchemy_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+pg8000://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+pg8000://", 1)
    return url


engine = create_engine(
    _sqlalchemy_url(DATABASE_URL),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    future=True,
)


def _normalize_params(params: tuple | list | None) -> tuple:
    if params is None:
        return ()
    if isinstance(params, tuple):
        return params
    if isinstance(params, list):
        return tuple(params)
    return (params,)


def _prepare(sql: str, params: tuple | list | None = None) -> tuple[str, dict]:
    values = _normalize_params(params)
    index = 0

    def replace(match: re.Match) -> str:
        nonlocal index
        name = f"p{index}"
        index += 1
        cast = match.group("cast")
        return f"CAST(:{name} AS {cast})" if cast else f":{name}"

    prepared_sql = _PLACEHOLDER_RE.sub(replace, sql)
    if index != len(values):
        raise ValueError(f"SQL parameter count mismatch: expected {index}, received {len(values)}")
    return prepared_sql.replace("%%", "%"), {f"p{i}": value for i, value in enumerate(values)}


def _row_to_dict(row):
    return dict(row._mapping) if row is not None else None


def _rows_to_dicts(rows: Sequence):
    return [dict(row._mapping) for row in rows]


def fetch_one(sql: str, params: tuple | list = ()):
    prepared_sql, prepared_params = _prepare(sql, params)
    with engine.connect() as conn:
        result = conn.execute(text(prepared_sql), prepared_params)
        return _row_to_dict(result.fetchone())


def fetch_all(sql: str, params: tuple | list = ()):
    prepared_sql, prepared_params = _prepare(sql, params)
    with engine.connect() as conn:
        result = conn.execute(text(prepared_sql), prepared_params)
        return _rows_to_dicts(result.fetchall())


def execute(sql: str, params: tuple | list = ()):
    prepared_sql, prepared_params = _prepare(sql, params)
    with engine.begin() as conn:
        result = conn.execute(text(prepared_sql), prepared_params)
        return _row_to_dict(result.fetchone()) if result.returns_rows else None
