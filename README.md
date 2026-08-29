# 学习日志管理器 (Study Log Manager)

基于 Python + SQLite/MySQL 的命令行学习记录管理工具，用于记录每日学习内容、统计学习时长、管理主题分类。

## ✨ 功能

- 添加 / 查看学习记录
- 统计总学习时长
- 按日期查询学习时长
- 主题字典管理（自动去重补录）
- 按主题统计学习时长
- 导出为 CSV（Excel 可直接打开）

## 🛠️ 技术栈

- Python 3
- SQLite / MySQL
- pymysql
- Git

## 🚀 使用方法

```bash
# SQLite 版（零配置，直接跑）
python 记录学习日志脚本.py

# MySQL 版（需先在本机建 config.py 配置密码）
pip install pymysql
python db_mysql.py
```

> 提示：MySQL 版从 `config.py` 读取数据库密码，`config.py` 已被 `.gitignore` 排除，不会提交到仓库。

## 📝 项目背景

2027 届求职准备期间的学习记录工具，用于实践 Python、SQLite、MySQL 和 Git 的综合运用。
