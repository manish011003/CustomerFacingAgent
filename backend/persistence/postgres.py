from __future__ import annotations

import os
import threading
from typing import Any

_local = threading.local()

DDL = (
    """
    CREATE TABLE IF NOT EXISTS passengers (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        body JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS accounts (
        email TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES passengers(id) ON DELETE CASCADE,
        password_hash TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES passengers(id) ON DELETE CASCADE,
        body JSONB NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS documents (
        collection TEXT NOT NULL,
        id TEXT NOT NULL,
        customer_id TEXT,
        body JSONB NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        PRIMARY KEY (collection, id)
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS documents_collection_customer_idx
        ON documents (collection, customer_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS auth_tokens (
        token TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL REFERENCES passengers(id) ON DELETE CASCADE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """,
)


def database_url() -> str | None:
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        return None
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


def connect() -> Any:
    """Thread-local psycopg connection. Schema is applied once per connection."""
    import psycopg

    url = database_url()
    if not url:
        raise ConnectionError("DATABASE_URL is not set")
    conn = getattr(_local, "conn", None)
    if conn is not None and not conn.closed:
        return conn
    conn = psycopg.connect(url, autocommit=True, connect_timeout=5)
    for statement in DDL:
        conn.execute(statement)
    _local.conn = conn
    return conn


def reset() -> None:
    conn = getattr(_local, "conn", None)
    if conn is not None and not conn.closed:
        conn.close()
    _local.conn = None
