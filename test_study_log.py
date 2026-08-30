import sqlite3
import pytest
import 记录学习日志脚本 as log 

@pytest.fixture()
def db():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.execute("CREATE TABLE study_log (id INTEGER PRIMARY KEY, date TEXT, topic TEXT, minutes INTEGER, done TEXT)")
    cur.execute("CREATE TABLE shell_topic (topic TEXT PRIMARY KEY)")
    conn.commit()
    yield conn
    conn.close()

def test_add_record(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    rows = cur.execute("SELECT * FROM study_log").fetchall()
    assert len(rows) == 1
    assert rows[0][2] == 'pytest入门'

def test_add_duplicate_topic(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 40, 'yes')
    rows = cur.execute("SELECT * FROM study_log").fetchall()
    assert len(rows) == 2

def test_topic_no_duplicate(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 40, 'yes')
    rows = cur.execute("SELECT * FROM shell_topic ").fetchall()
    assert len(rows) == 1

def test_delete_record(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'ce', 30, 'yes')
    rows = cur.execute("SELECT * FROM study_log ").fetchall()
    assert len(rows) == 1
    log.delete_record(db, cur, 1)
    row = log.get_record_by_id(cur, 1)
    assert row is None

def test_delete_wrong_id(db):
    cur = db.cursor()
    log.delete_record(db, cur, 888)
    
def test_update_record(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    log.update_record(db, cur,1 , '2026-08-30', 'pytest', 80, 'yes')
    rows = log.get_record_by_id(cur, 1)
    assert rows[2] == 'pytest'
    assert rows[3] == 80

def test_update_no_record(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    log.update_record(db, cur,888 , '2026-08-30', 'pytest', 80, 'yes')
    rows = log.get_record_by_id(cur, 1)
    assert rows[0] == 1
    assert rows[2] == 'pytest入门'

def test_get_record_by_id_found(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    rows = log.get_record_by_id(cur, 1)
    assert rows is not None

def test_get_record_by_id_miss(db):
    cur = db.cursor()
    rows = log.get_record_by_id(cur, 999)
    assert rows is None

def test_total_minutes(db):
    cur = db.cursor()
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 30, 'yes')
    log.add_record(db, cur, '2026-08-30', 'pytest入门', 40, 'yes')
    total = log.get_total_minutes(cur)
    assert total == 70

def test_total_minutes_empty(db):
    cur = db.cursor()
    total = log.get_total_minutes(cur)
    assert total == 0

@pytest.mark.parametrize("minutes_list, expected", [
    ([30], 30), 
    ([30, 40], 70), 
    ([30, 40, 50], 120), 
    ([0], 0), 
    ([1, 2, 3, 4, 5], 15), 
])
def test_total_minutes_multi(db, minutes_list, expected):
    cur = db.cursor()
    for i, m in enumerate(minutes_list):
        log.add_record(db, cur, '2026-08-30', f'主题{i}', m , 'yes')
    total = log.get_total_minutes(cur)
    assert total == expected

@pytest.mark.parametrize("bad_id",[999, -1, 1000, 0])
def test_get_by_id_miss_multi(db, bad_id):
    cur = db.cursor()
    row = log.get_record_by_id(cur, bad_id)
    assert row is None