import os
import pytest
from database.connection import init_db

@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    db = tmp_path / "test_marketing_ops.db"
    monkeypatch.setenv("MARKETING_OPS_DB", str(db))
    init_db()
    yield db
