# -*- coding: utf-8 -*-
# 学习日志管理器 - MySQL 完整版 v4 (可测试性重构版, 只能在云服务器上跑!)
# 运行: python3 db_mysql.py
# 与本地 SQLite 版功能 1:1 对齐: 11 个干活函数 + 薄菜单层 + __main__ 守卫
# 密码在 config.py 里, config.py 已被 .gitignore 挡住, 不会上传 GitHub

import csv
import os
import pymysql
from config import DB_PASSWORD  # 密码从 config.py 读, 不写死在代码里

# ========== 数据库连接 (启动时执行一次) ==========
# host='127.0.0.1' = 只连服务器本机, 密码不出服务器
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password=DB_PASSWORD,
    database='study'
)
cur = conn.cursor()

# ========== 建表 ==========
# MySQL 差异1: 自增主键必须显式写 AUTO_INCREMENT
cur.execute("""CREATE TABLE IF NOT EXISTS study_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TEXT, topic TEXT,
    minutes INT, done TEXT
)""")
# MySQL 差异2: TEXT 不能做主键, 用 VARCHAR(100)
cur.execute("CREATE TABLE IF NOT EXISTS shell_topic (topic VARCHAR(100) PRIMARY KEY)")
conn.commit()


def add_record(conn, cur, date, topic, minutes, done):
    """添加一条学习记录, 同时把主题登记进字典表"""
    cur.execute("INSERT INTO study_log (date, topic, minutes, done) VALUES (%s, %s, %s, %s)",
                (date, topic, minutes, done))
    # MySQL 差异3: 去重写 INSERT IGNORE (SQLite 是 INSERT OR IGNORE, 词序不同!)
    cur.execute("INSERT IGNORE INTO shell_topic (topic) VALUES (%s)", (topic,))
    conn.commit()

def get_all_records(cur):
    """查询所有学习记录, 返回列表 [(id, date, topic, minutes, done), ...]"""
    cur.execute("SELECT * FROM study_log")
    return cur.fetchall()

def get_total_minutes(cur):
    """统计总学习时长; 空库时 SUM 返回 None, 处理成 0"""
    cur.execute("SELECT SUM(minutes) FROM study_log")
    total = cur.fetchone()[0]
    return total if total else 0

def get_minutes_by_date(cur, d):
    """查询某一天的学习时长, 没有记录时返回空列表 []"""
    cur.execute("SELECT date, SUM(minutes) FROM study_log WHERE date = %s", (d,))
    return cur.fetchall()

def sync_topics(conn, cur):
    """把日志里出现过的主题补录进字典表(自动去重), 返回全部主题"""
    cur.execute("SELECT DISTINCT topic FROM study_log")
    topics = cur.fetchall()
    for t in topics:
        cur.execute("INSERT IGNORE INTO shell_topic (topic) VALUES (%s)", (t[0],))
    conn.commit()
    cur.execute("SELECT * FROM shell_topic ORDER BY topic")
    return cur.fetchall()

def get_topic_minutes(cur):
    """统计每个主题的总时长, 返回 [(topic, 分钟), ...] 按主题排序"""
    cur.execute("SELECT topic, SUM(minutes) FROM study_log GROUP BY topic ORDER BY topic")
    return cur.fetchall()

def get_day_records(cur, d):
    """查询某一天的全部记录, 按 id 倒序"""
    cur.execute("SELECT * FROM study_log WHERE date = %s ORDER BY id DESC", (d,))
    return cur.fetchall()

def get_record_by_id(cur, i):
    """按 id 查一条记录, 找不到返回 None"""
    cur.execute("SELECT * FROM study_log WHERE id = %s", (i,))
    return cur.fetchone()

def update_record(conn, cur, i, date, topic, minutes, done):
    """按 id 修改一条记录的四个字段"""
    cur.execute("UPDATE study_log SET date=%s, topic=%s, minutes=%s, done=%s WHERE id=%s",
                (date, topic, minutes, done, i))
    conn.commit()

def delete_record(conn, cur, i):
    """按 id 删除一条记录"""
    cur.execute("DELETE FROM study_log WHERE id = %s", (i,))
    conn.commit()

def export_csv(cur):
    """导出全部记录到 data/export.csv (utf-8-sig 防止 Excel 中文乱码)"""
    os.makedirs('data', exist_ok=True)  # 服务器上可能没有 data 目录, 先确保存在
    cur.execute("SELECT * FROM study_log")
    with open('data/export.csv', 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'date', 'topic', 'minutes', 'done'])
        writer.writerows(cur.fetchall())

# ========== 菜单区 ==========

def main():
    while True:
        print('\n===== 学习日志管理器 (MySQL版) =====')
        print('1. 添加记录')
        print('2. 查看所有日志')
        print('3. 统计学习时长')
        print('4. 按日期查询学习时长')
        print('5. 查看主题字典')
        print('6. 统计主题学习时长')
        print('7. 查看某一天的按序日志记录')
        print('8. 修改记录')
        print('9. 删除记录')
        print('e. 导出csv')
        print('0. 退出')
        choice = input('请选择(1/2/3/4/5/6/7/8/9/e/0): ')

        if choice == '1':
            date = input('日期(如2026-08-30): ')
            topic = input('学习的内容: ')
            minutes = int(input('学习了多少分钟: '))
            done = input('学习情况(yes/no): ')
            add_record(conn, cur, date, topic, minutes, done)
            print('已添加')

        elif choice == '2':
            for row in get_all_records(cur):
                print(row)

        elif choice == '3':
            print(f'总学习时长: {get_total_minutes(cur)} 分钟')

        elif choice == '4':
            d = input('请输入日期(如2026-08-30): ')
            rows = get_minutes_by_date(cur, d)
            if rows:
                print(rows)
            else:
                print('这一天没有记录')

        elif choice == '5':
            rows = sync_topics(conn, cur)
            print(f'已补录, 共 {len(rows)} 个主题')
            for row in rows:
                print(f'主题 {row[0]}')

        elif choice == '6':
            for row in get_topic_minutes(cur):
                print(f'主题 {row[0]}, 共 {row[1]} 分钟')

        elif choice == '7':
            d = input('请输入日期: ')
            for row in get_day_records(cur, d):
                print(row)

        elif choice == '8':
            i = input('要修改的日志id: ')
            old = get_record_by_id(cur, i)
            if not old:
                print('没有找到这条日志')
            else:
                print(f'原日志: {old}')
                new_date = input(f'新 date (回车不改, 原 {old[1]}): ') or old[1]
                new_topic = input(f'新 topic (回车不改, 原 {old[2]}): ') or old[2]
                new_minutes = input(f'新 minutes (回车不改, 原 {old[3]}): ') or old[3]
                new_done = input(f'新 done (回车不改, 原 {old[4]}): ') or old[4]
                sure = input(f'确认改为: [{new_date}, {new_topic}, {new_minutes}, {new_done}] ? y/n: ')
                if sure == 'y':
                    update_record(conn, cur, i, new_date, new_topic, new_minutes, new_done)
                    print('已修改')
                else:
                    print('已取消')

        elif choice == '9':
            i = input('要删除的日志id: ')
            old = get_record_by_id(cur, i)
            if not old:
                print('没有找到这条日志')
            else:
                print(f'将删除: {old}')
                sure = input('确认删除? 删了就没啦 (y/n): ')
                if sure == 'y':
                    delete_record(conn, cur, i)
                    print('已删除')
                else:
                    print('已取消')

        elif choice == 'e':
            export_csv(cur)
            print('已导出到 data/export.csv, Excel 可随时查看')

        elif choice == '0':
            break

    conn.close()
    print('请继续加油学习哦！')

if __name__ == '__main__':
    main()
