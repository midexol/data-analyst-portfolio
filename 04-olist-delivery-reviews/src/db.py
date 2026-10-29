"""MySQL helpers: connect, load a CSV into a table, and run a .sql file.

Connection settings come from environment variables, with local defaults:
    MYSQL_HOST (localhost), MYSQL_PORT (3306), MYSQL_USER (root), MYSQL_PASSWORD (empty)
The database name is set by each project.
"""
from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pymysql
from sqlalchemy import create_engine


def _settings() -> dict:
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
    }


def connect(database: str) -> pymysql.connections.Connection:
    """Creates the database if needed and returns a connection to it."""
    s = _settings()
    with pymysql.connect(**s) as c, c.cursor() as cur:
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4")
    return pymysql.connect(**s, database=database, charset="utf8mb4", autocommit=True)


def load_csv(database: str, table: str, path: Path, **read_csv_args) -> int:
    """Reads a CSV with pandas and writes it to a MySQL table (replacing it). Returns the row count."""
    connect(database).close()  # makes sure the database exists
    s = _settings()
    url = f"mysql+pymysql://{s['user']}:{s['password']}@{s['host']}:{s['port']}/{database}?charset=utf8mb4"
    df = pd.read_csv(path, **read_csv_args)
    engine = create_engine(url)
    df.to_sql(table, engine, if_exists="replace", index=False, chunksize=2000, method="multi")
    engine.dispose()
    return len(df)


def statements(sql: str) -> list[str]:
    """Splits a .sql file into statements on semicolons, ignoring ones inside quotes or comments."""
    out, buf, quote, i = [], [], None, 0
    while i < len(sql):
        ch = sql[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                if i + 1 < len(sql) and sql[i + 1] == quote:  # escaped quote, like 'can''t'
                    buf.append(sql[i + 1])
                    i += 1
                else:
                    quote = None
        elif ch in ("'", '"', "`"):
            quote = ch
            buf.append(ch)
        elif sql.startswith("--", i):
            while i < len(sql) and sql[i] != "\n":
                i += 1
            buf.append("\n")
        elif ch == ";":
            if "".join(buf).strip():
                out.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    if "".join(buf).strip():
        out.append("".join(buf).strip())
    return out


def query(con: pymysql.connections.Connection, sql: str) -> pd.DataFrame:
    with con.cursor() as cur:
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = [[float(v) if isinstance(v, Decimal) else v for v in r] for r in cur.fetchall()]
    return pd.DataFrame(rows, columns=cols)


def run_file(con: pymysql.connections.Connection, path: Path) -> pd.DataFrame | None:
    """Runs every statement in a .sql file. Returns the result of the last one if it's a query."""
    parts = statements(path.read_text())
    with con.cursor() as cur:
        for s in parts[:-1]:
            cur.execute(s)
    last = parts[-1]
    if last.lstrip().upper().startswith(("SELECT", "WITH", "(")):
        return query(con, last)
    with con.cursor() as cur:
        cur.execute(last)
    return None
