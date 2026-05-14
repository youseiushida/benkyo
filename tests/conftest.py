"""pytest 共有 fixtures."""

import pytest

from benkyo.db import connect


@pytest.fixture
def db_path(tmp_path):
    """テスト用 DB ファイルのパス."""
    return tmp_path / "test.db"


@pytest.fixture
def conn(db_path):
    """テスト用 DB 接続 (スキーマ初期化済み)."""
    c = connect(db_path)
    yield c
    c.close()
