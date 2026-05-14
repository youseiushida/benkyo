"""Helper to obtain a DB connection from within a CLI command."""

import sqlite3

import click

from benkyo.db import connect
from benkyo.paths import resolve_db_path


def get_conn(ctx: click.Context) -> sqlite3.Connection:
    db_path_override = ctx.obj.get("db_path_override") if ctx.obj else None
    return connect(resolve_db_path(db_path_override))
