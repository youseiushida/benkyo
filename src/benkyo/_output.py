"""JSON output and error-handling helpers."""

import json
import sys
from functools import wraps
from typing import Any, Callable

import click

from benkyo.errors import BenkyoError

EXIT_CODES = {
    "not_found": 2,
    "conflict": 3,
    "invalid_arg": 1,
}


def output_ok(result: Any, count: int | None = None) -> None:
    payload: dict[str, Any] = {"ok": True, "result": result}
    if count is not None:
        payload["count"] = count
    click.echo(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def output_err(error: BenkyoError, exit_code: int | None = None) -> None:
    if exit_code is None:
        exit_code = EXIT_CODES.get(error.code, 1)
    payload = {"ok": False, "error": error.message, "code": error.code}
    click.echo(json.dumps(payload, ensure_ascii=False), err=True)
    sys.exit(exit_code)


def handle_errors(fn: Callable) -> Callable:
    """Decorator that catches BenkyoError and emits a JSON error to stderr."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except BenkyoError as e:
            output_err(e)

    return wrapper
