import sqlite3
conn = sqlite3.connect('data/study.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS study_log (id INTEGER PRIMARY KEY, date TEXT, topic TEXT, minutes INTEGER, done TEXT)")
cur.execute("INSERT INTO study_log (date, topic, minutes, done) VALUES (?, ?, ?, ?)", 
            ('2026-08-29', '利用python创建SQL数据库', 30, 'yes'))
conn.commit()
cur.execute("SELECT * FROM study_log")
for row in cur.fetchall():
    print(row)

conn.close()