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

@pytest.mark.parametrize("m, expected", [
    (0, False), (1, True), (2, True),      
    (599, True), (600, True), (601, False), 
    (-1, False), (-100, False),             
])
def test_is_valid_minutes(m, expected):
    assert log.is_valid_minutes(m) == expected

@pytest.mark.parametrize("text, integer", [
    ('abc', None), ('30', 30), ('2', 2),      
    ('十五', None), ('12a', None), ('', None), 
    ('3.5', None), ('100', 100),
])
def test_parse_minutes(text, integer):
    assert log.parse_minutes(text) == integer

def check_login(user_ok, pwd_ok):
    if not user_ok:
        return '用户名错误'
    elif not pwd_ok:
        return '密码错误'
    return '成功登录'

@pytest.mark.parametrize('user_ok, pwd_ok, expected', [
    (True, True, '成功登录'),
    (True, False, '密码错误'),
    (False, True, '用户名错误'),
    (False, False, '用户名错误'),
])
def test_login(user_ok, pwd_ok, expected):
    assert check_login(user_ok, pwd_ok) == expected

def _check_add_record_helper(date_text, topic, minutes_text):
    if log.parse_date(date_text) is None:
        return '日期错误'
    elif not topic:
        return '内容错误'
    elif not minutes_text:
        return '时间错误'           # ← 空串: None/'' 都拦下来
    elif log.parse_minutes(minutes_text) is None:
        return '时间格式错误'        # ← 'abc' '3.5' 这种:转不成数字
    elif not log.is_valid_minutes(int(minutes_text)):
        return '时间范围错误'        # ← 0/601/-1 这种:数字但超界
    return '成功'

@pytest.mark.parametrize('date_text, topic, minutes_text, expected', [
    ('2026-08-31', 'python', '30', '成功'),
    ('2026-13-32', 'python', '30', '日期错误'),
    ('2026-08-dd', 'python', '30', '日期错误'),
    ('2026-08-31', '', '30', '内容错误'),
    ('2026-08-31', 'python', '0', '时间范围错误'),
    ('2026/08/31', 'python', '30', '日期错误'),
    ('2026-08-31', 'python', 'abc', '时间格式错误'),
    ('2026-08-', '', '', '日期错误'),
])
def test_check_add_record(date_text, topic, minutes_text, expected):
    assert _check_add_record_helper(date_text, topic, minutes_text) == expected