import sqlite3
conn = sqlite3.connect('data/study.db')
cur = conn.cursor()
# 故意查一个不存在的日期，看两个函数分别返回什么
cur.execute("SELECT * FROM study_log WHERE date = '9999-01-01'")
print('fetchone 返回：', cur.fetchone())
print('fetchall 返回：', cur.fetchall())
conn.close()
