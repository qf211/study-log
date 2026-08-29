import sqlite3
conn = sqlite3.connect('data/study.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS study_log (id INTGER PRIMARY KEY, date TEXT, topic TEXT, minutes INTGER, done TEXT)")
conn.commit()

while True:
    print('\n===== 学习日志管理器 =====')
    print('1. 添加记录')
    print('2. 查看所有日志')
    print('3. 统计学习时长')
    print('4. 退出')
    choice = input('请选择(1/2/3/4): ')

    if choice == '1':
        date = input('日期(如2026-08-28): ')
        topic = input('学习的内容: ')
        minutes = int(input('学习了多少分钟: '))
        done = input('学习情况(yes/no): ')
        cur.execute("INSERT INTO study_log (date, topic, minutes, done) VALUES (?, ?, ?, ?)", 
                    (date, topic, minutes, done))
        conn.commit()

    elif choice == '2':
        cur.execute("SELECT * FROM study_log")
        for row in cur.fetchall():
            print(row)

    elif choice == '3':
        cur.execute("SELECT SUM(minutes) FROM study_log")
        total = cur.fetchone()[0]
        print(f'总学习时长: {total} 分钟')

    elif choice == '4':
        break

conn.close()
print('请继续加油学习哦！')
    