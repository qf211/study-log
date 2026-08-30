# 学习日志管理器 (Study Log Manager)

基于 Python + SQLite/MySQL 的命令行学习记录管理工具。

## ✨ 功能
- 添加/查看/删除学习记录
- 按日期、主题查询
- 按主题统计学习时长
- 数据去重补录
- 导出为 CSV

## 🛠️ 技术栈
- Python 3
- SQLite / MySQL
- pymysql
- Git

## 🚀 使用方法
```bash
pip install pymysql
python db.py           # SQLite 版
python db_mysql.py     # MySQL 版（需先建 config.py 填密码）
