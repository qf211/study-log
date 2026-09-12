import sqlite3
import pytest
import main
from fastapi.testclient import TestClient
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # study-log/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture(scope="session")    
def conn():
    c = sqlite3.connect(':memory:', check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS study_log (id INTEGER PRIMARY KEY, date TEXT, topic TEXT, minutes INTEGER, done TEXT)")
    c.commit()
    return c

@pytest.fixture()
def client(conn):                    
    conn.execute("DELETE FROM study_log")
    conn.commit()
    main.app.dependency_overrides[main.get_conn] = lambda: conn
    return TestClient(main.app)