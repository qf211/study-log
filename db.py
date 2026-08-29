import sqlite3
conn = sqlite3.connect('data/study.bd')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS study_log (id INTEGER PRIMARY KEY, date EXTE, topic EXTE, minutes INTEGER, done EXTE)''')
cur.execute("INSERT INTO study_log (date, topic, minutes, done) VALUES (?, ?, ?, ?)", 
            ('2026-8-29', 'python复习', 30, 'yes'))
conn.commit()
cur.execute("SELECT * FROM study_log")
for row in cur.fetchall():
    print(row)
conn.close()