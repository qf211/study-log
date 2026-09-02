from fastapi import FastAPI, HTTPException
import config
from pathlib import Path
from pydantic import BaseModel

# 数据库类型判断：本地 sqlite，服务器 mysql
if config.DATABASE_TYPE == 'mysql':
    import pymysql
else:
    import sqlite3
from fastapi import Form
from fastapi.responses import HTMLResponse

DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'study.db'


def _sql(s):
    """SQL 占位符适配：sqlite 用 ?，mysql 用 %s"""
    if config.DATABASE_TYPE == 'mysql':
        return s.replace('?', '%s')
    return s


def get_conn():
    if config.DATABASE_TYPE == 'mysql':
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password=config.DB_PASSWORD,
            database='study',
            cursorclass=pymysql.cursors.DictCursor,
        )
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
    return conn


app = FastAPI()

@app.get("/")
def index():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>学习日志</title></head>
    <body>
        <h1>学习日志管理器</h1>
        <form action="/records-form" method="post">
            <p>日期: <input type="date" name="date"></p>
            <p>内容: <input type="text" name="topic"></p>
            <p>时长(分钟): <input type="number" name="minutes"></p>
            <button type="submit">添加记录</button>
        </form>
    </body>
    </html>
    """)


@app.post("/records-form")
def add_record_form(date: str = Form(...), topic: str = Form(...), minutes: int = Form(...)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("INSERT INTO study_log (date, topic, minutes, done) VALUES (?, ?, ?, ?)"),
                (date, topic, minutes, False))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return HTMLResponse(f"添加成功! 新纪录 id={new_id}, <a href='/'>返回表单</a>")


@app.get('/records')
def get_records():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT id, date, topic, minutes, done FROM study_log"))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get('/records/by_date')
def get_records_by_date(date: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM study_log WHERE date = ?"), (date,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get('/records/{records_id}')
def get_record(records_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT id, date, topic, minutes, done FROM study_log WHERE id = ?"),
                (records_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail='没有这条记录')
    return dict(row)


@app.get('/stats')
def get_stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT COUNT(*) AS total_count, SUM(minutes) AS total_minutes FROM study_log"))
    row = cur.fetchone()
    conn.close()
    return dict(row)


class NewRecord(BaseModel):
    date: str
    topic: str
    minutes: int
    done: bool = False


class UpdateRecord(BaseModel):
    date: str
    topic: str
    minutes: int
    done: bool = False


@app.post('/records')
def add_record(record: NewRecord):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("INSERT INTO study_log (date, topic, minutes, done) VALUES (?, ?, ?, ?)"),
                (record.date, record.topic, record.minutes, record.done))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {'id': new_id, 'status': 'ok'}


@app.put('/records/{record_id}')
def update_records(record_id: int, record: UpdateRecord):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM study_log WHERE id = ?"), (record_id,))
    old = cur.fetchone()
    if old is None:
        conn.close()
        raise HTTPException(status_code=404, detail='记录不存在')
    cur.execute(_sql("UPDATE study_log SET date = ?,topic = ?, minutes = ?, done = ? WHERE id = ?"),
                (record.date, record.topic, record.minutes, record.done, record_id))
    conn.commit()
    conn.close()
    return {'status': 'ok', 'id': record_id}


@app.get('/edit/{record_id}')
def edit_page(record_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM study_log WHERE id = ?"), (record_id,))
    old = cur.fetchone()
    if old is None:
        conn.close()
        raise HTTPException(status_code=404, detail='记录不存在')
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset='utf-8'><title>编辑记录</title></head>
    <body>
        <h1>编辑第 {record_id} 条记录</h1>
        <form action="/records/{record_id}/update" method="post">
        <p>日期: <input type='date' name='date' value='{old['date']}'></p>
        <p>内容: <input type='text' name='topic' value='{old['topic']}'></p>
        <p>时间: <input type='number' name='minutes' value='{old['minutes']}'></p>
        <button type='submit'>保存修改</button>
        </form>
    </body>
    </html>
    """)


@app.post('/records/{record_id}/update')
def update_record_form(record_id: int, date: str = Form(...), topic: str = Form(...), minutes: int = Form(...)):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM study_log WHERE id = ?"), (record_id,))
    old = cur.fetchone()
    if old is None:
        conn.close()
        raise HTTPException(status_code=404, detail='记录不存在')
    cur.execute(_sql("UPDATE study_log SET date = ?,topic = ?, minutes = ? WHERE id = ?"),
                (date, topic, minutes, record_id))
    conn.commit()
    conn.close()
    return HTMLResponse("修改成功! <a href='/list'>返回列表</a>")


@app.get('/list')
def list_page():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM study_log ORDER BY id"))
    rows = cur.fetchall()
    conn.close()
    record_lines = []
    for row in rows:
        line = (
            f"<p>{row['date']} - {row['topic']}"
            f"({row['minutes']}分钟)"
            f"<a href='/edit/{row['id']}'>编辑</a></p>"
            f"<button type='button' onclick='delRecord({row['id']})'>删除</button>"
        )
        record_lines.append(line)
    records_html = "\n".join(record_lines)
    script = """
    <script>
    function delRecord(id) {
        fetch('/records/' + id, {method: 'DELETE'})
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('删除失败')
            }
        });
    }
    </script>
    """

    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>所有记录</title></head>
    <body>
        <h1>所有学习记录</h1>
        {records_html}
        <p><a href='/'>← 返回新增页</a></p>
        {script}
    </body>
    </html>
    """)


@app.delete('/records/{record_id}')
def delete_records(record_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(_sql("SELECT * FROM study_log WHERE id = ?"), (record_id,))
    old = cur.fetchone()
    if old is None:
        conn.close()
        raise HTTPException(status_code=404, detail='记录不存在')
    cur.execute(_sql("DELETE FROM study_log WHERE id = ?"), (record_id,))
    conn.commit()
    conn.close()
    return {'status': 'ok', 'id': record_id}
