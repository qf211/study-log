import sqlite3
conn = sqlite3.connect('data/study.db')
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS study_log (id INTGER PRIMARY KEY, date TEXT, topic TEXT, minutes INTGER, done TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS shell_topic (topic TEXT PRIMARY KEY)")
conn.commit()

while True:
    print('\n===== 学习日志管理器 =====')
    print('1. 添加记录')
    print('2. 查看所有日志')
    print('3. 统计学习时长')
    print('4. 按日期查询学习时长')
    print('5. 查看主题字典')
    print('6. 统计主题学习时长')
    print('7. 查看某一天的按序日志记录')
    print('8. 退出')
    choice = input('请选择(1/2/3/4/5/6/7/8): ')

    if choice == '1':
        date = input('日期(如2026-08-28): ')
        topic = input('学习的内容: ')
        minutes = int(input('学习了多少分钟: '))
        done = input('学习情况(yes/no): ')
        cur.execute("INSERT INTO study_log (date, topic, minutes, done) VALUES (?, ?, ?, ?)", 
                    (date, topic, minutes, done))
        cur.execute("INSERT OR IGNORE INTO shell_topic (topic) VALUES (?)", (topic,))
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
        d = input('请输入日期(如2026-08-28): ')
        cur.execute("SELECT date, SUM(minutes) FROM study_log WHERE data = ?", (d,))
        row = cur.fetchall()
        if row:
            print(row)
        else:
            print('这一天没有记录')

    elif choice == '5':
        cur.execute("SELECT DISTINCT topic FROM study_log")
        topics = cur.fetchall()
        for t in topics:
            cur.execute("INSERT OR IGNORE INTO shell_topic (topic) VALUES (?)", (t[0],))
        conn.commit()
        print(f'已补录, 共 {len(topics)} 个主题')
        cur.execute("SELECT * FROM shell_topic ORDER BY topic")
        for row in cur.fetchall():
            print(f'主题 {row[0]}')

    elif choice == '6':
        cur.execute("SELECT topic, SUM(minutes) FROM study_log GROUP BY topic ORDER BY topic")
        for row in cur.fetchall():
            print(f'主题 {row[0]}, 共 {row[1]} 分钟')
    elif choice == '7':
        d = input("请输入日期: ")
        cur.execute("SELECT * FROM study_log WHERE date = ? ORDER BY date DESC", (d,))
        for row in cur.fetchall():
            print(row)

    elif choice == '8':
        break

conn.close()
print('请继续加油学习哦！')