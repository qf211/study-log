# 学习日志管理器 (Study Log Manager)

基于 Python + SQLite/MySQL 的命令行学习记录管理工具，用于记录每日学习内容、统计学习时长、管理主题分类。

**同一套功能，两种数据库实现**（SQLite 本地版 / MySQL 云服务器版），并配有完整的 pytest 自动化测试。

## ✨ 功能

- 学习记录完整 CRUD：添加 / 查看 / **修改** / **删除**
- 输入校验：单次学习时长限制 **1~600 分钟**（需求定义，等价类 + 边界值分析设计用例）
- 统计总学习时长（空库边界已处理）
- 按日期查询学习时长、按主题统计学习时长
- 主题字典管理（自动去重补录）
- 导出为 CSV（utf-8-sig 编码，Excel 打开中文不乱码）
- ✅ **pytest 自动化测试 36 个用例**，全部通过

## 🧪 自动化测试（亮点）

```bash
pip install pytest
pytest test_study_log.py -v
```

36 passed in 0.06s，测试设计要点：

- **可测试性重构**：业务逻辑（12 个纯函数）与用户交互（菜单）分离，入口用 `if __name__ == '__main__'` 守卫，使模块可被安全 import
- **测试隔离**：使用 SQLite `:memory:` 内存数据库 + `@pytest.fixture` 管理每个用例的准备/清理，不触碰真实数据
- **参数化**：`@pytest.mark.parametrize` 覆盖多组数据与边界值（不存在的 id、空库等）
- **需求驱动测试**：时长校验用例按"边界三兄弟"法设计——边界内(1/599/600)、边界外(0/601/-1)，测试对错标准来自需求而非代码
- **回归看门狗**：包含历史缺陷（空库 `SUM()` 返回 `None`、字典表主键冲突未去重）的防复发用例

## 🛠️ 技术栈

- Python 3
- SQLite / MySQL 8.0
- pymysql
- pytest
- Git / GitHub
- Linux（阿里云 ECS 部署运行）

## 🚀 使用方法

```bash
# SQLite 版（零配置，直接跑）
python 记录学习日志脚本.py

# MySQL 版（需先在本机建 config.py 配置密码）
pip install pymysql
python db_mysql.py

# 运行测试
pip install pytest
pytest test_study_log.py -v
```

> 提示：MySQL 版从 `config.py` 读取数据库密码

## 📌 SQLite 与 MySQL 差异实践

项目同时实现两种数据库版本，实际踩过的差异点：

| 差异点 | SQLite | MySQL |
|--------|--------|-------|
| 自增主键 | `INTEGER PRIMARY KEY`（自动） | `INT AUTO_INCREMENT PRIMARY KEY`（必须显式） |
| 占位符 | `?` | `%s` |
| 文本主键 | `TEXT PRIMARY KEY` | `VARCHAR(100) PRIMARY KEY`（TEXT 不能做主键） |
| 去重插入 | `INSERT OR IGNORE` | `INSERT IGNORE` |

## 📝 项目背景

学习记录工具，用于实践 Python、SQLite、MySQL、pytest 和 Git 的综合运用。项目部署在阿里云 ECS（Alibaba Cloud Linux）上运行 MySQL 版。
