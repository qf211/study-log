import pymysql
from config import DB_PASSWORD


conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='DB_PASSWORD',
    database='study'
)
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS study_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TEXT, topic TEXT,
    minutes INTEGER, done TEXT
)""")

cur.execute(
    "INSERT INTO study_log (date, topic, minutes, done) VALUES (%s, %s, %s, %s)",
    ('2026-08-29', 'Python连MySQL', 60, 'yes')
)
conn.commit()

cur.execute("SELECT * FROM study_log")
for row in cur.fetchall():
    print(row)

conn.close()
print('OK, done!')