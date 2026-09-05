import pytest
import sqlite3
import main 
from fastapi.testclient import TestClient

TEST_CONN = sqlite3.connect(':memory:', check_same_thread=False)
TEST_CONN.row_factory = sqlite3.Row

def override_get_conn():
    return TEST_CONN

main.app.dependency_overrides[main.get_conn] = override_get_conn

@pytest.fixture()

def client():
    cur = TEST_CONN.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS study_log (id INTEGER PRIMARY KEY, date TEXT, topic TEXT, minutes INTEGER, done TEXT)")
    cur.execute("DELETE FROM study_log")
    TEST_CONN.commit()
    return TestClient(main.app)

def test_records_empty(client):
    resp = client.get('/records')
    assert resp.status_code == 200
    assert resp.json() == []

def test_records(client):
    resp = client.post('/records', json={
        'date': '2026-09-03',
        'topic': 'web测试',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 200

    resp = client.get('/records')
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]['minutes'] == 30
    assert data[0]['topic'] == 'web测试'

def test_update(client):
    resp = client.post('/records', json={
        'date': '2026-09-03',
        'topic': 'web测试',
        'minutes': 30,
        'done': False
    })
    new_id = resp.json()['id']
    assert resp.status_code == 200

    resp = client.put(f'/records/{new_id}', json={
        'date': '2026-09-03',
        'topic': 'fastAPI',
        'minutes': 30,
        'done': True
    })
    assert resp.status_code == 200
    resp = client.get('/records')
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]['topic'] == 'fastAPI'

def test_delete(client):
    resp = client.post('/records', json={
        'date': '2026-09-03',
        'topic': 'web测试',
        'minutes': 30,
        'done': False        
    })
    new_id = resp.json()['id']
    assert resp.status_code == 200
    resp = client.delete(f'/records/{new_id}')
    resp = client.get('/records')
    assert resp.json() == []

def test_404(client):
    resp = client.get('/records/999')
    assert resp.status_code == 404
    resp = client.delete('/records/999')
    assert resp.status_code == 404

