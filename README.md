# 学习日志管理器 (Study Log Manager)

[![CI](https://github.com/qf211/study-log/actions/workflows/ci.yml/badge.svg)](https://github.com/qf211/study-log/actions/workflows/ci.yml)
<!-- CI 徽章：Actions 跑绿后显示 ✅ passing，就是简历上的可视化证据 -->

基于 Python + SQLite/MySQL 的命令行学习记录管理工具，用于记录每日学习内容、统计学习时长、管理主题分类。

**同一套功能，两种数据库实现**（SQLite 本地版 / MySQL 云服务器版），并配有完整的 pytest 自动化测试 + GitHub Actions 持续集成（CI）。

## ✨ 功能

- 学习记录完整 CRUD：添加 / 查看 / **修改** / **删除**
- 输入校验：单次学习时长限制 **1~600 分钟**（需求定义，等价类 + 边界值分析设计用例）
- 统计总学习时长（空库边界已处理）
- 按日期查询学习时长、按主题统计学习时长
- 主题字典管理（自动去重补录）
- 导出为 CSV（utf-8-sig 编码，Excel 打开中文不乱码）
- ✅ **pytest 自动化测试 106 个用例**，全部通过（业务层 49 + 接口层 57）
- ✅ **测试覆盖率**：`web/main.py` **95%**（pytest-cov 实测；未覆盖部分是 MySQL 环境分支与防御性代码）
- ✅ **GitHub Actions CI**：push 自动跑全部测试 + **覆盖率门禁** + 产出可下载的 HTML 报告

## 🌐 Web 接口层（FastAPI，部署在阿里云 ECS）

同一套业务规则另有一版 Web 实现：

| 类别 | 接口 |
|---|---|
| 页面 | `GET /`（新增表单）、`GET /list`（列表）、`GET /edit/{id}`（编辑） |
| 查询 | `GET /records`、`GET /records/by_date?date=`、`GET /records/{id}`、`GET /stats` |
| 新增 | `POST /records`（JSON）、`POST /records-form`（表单） |
| 更新 | `PUT /records/{id}`（JSON）、`POST /records/{id}/update`（表单） |
| 删除 | `DELETE /records/{id}` |

**入参校验（pydantic，失败统一返回 422）**：

- `minutes` → `Field(ge=1, le=600)`
- `date` → `field_validator` + `validators.parse_date`（必须 `YYYY-MM-DD`）
- `topic` → `field_validator` + `validators.is_valid_topic`（非空白、长度 1~200）
- **三种入口共用同一个 `RecordBase` 模型**：JSON 接口、表单接口走同一套规则（表单用 `Annotated[RecordForm, Form()]` 接入）

**为什么规则抽到 `validators.py`**：CLI 与 Web 是两条入口，规则只写一份。历史上 Web 接口曾完全绕过 CLI 里的时长校验（脏数据直接进库）——这正是把规则抽成公共模块要解决的问题。

## 🧪 测试体系

```
业务层  test_study_log.py      49 条   ← 纯函数 / CLI 逻辑
接口层  web/test_web.py        57 条   ← FastAPI 路由
                              ─────
                              106 条（全绿）
```

| 层面 | 覆盖内容 | 关键设计 |
|---|---|---|
| 业务层 | CRUD、时长边界、判定表 8 组合、历史缺陷回归 | 内存 SQLite + fixture 隔离 |
| 接口层 | 正向流 / 框架校验 / 业务缺口 / 边界·安全·类型 | `TestClient` + `dependency_overrides` 换成内存库 |

- **数据隔离**：全部用 `sqlite3(':memory:')` + fixture 建表/清表，**不碰真实数据**
- **需求驱动**：时长边界用"边界三兄弟"（合法边界 / 越界）；三合一校验用**判定表法**把 2×2×2=8 组合收敛成一条参数化用例
- **异常专项**：空串、超长、纯空格、emoji、SQL 注入字符串、类型错误、重复提交
- **回归看门狗**：每发现一个 bug 就追写一条用例
- **覆盖率**：`pytest-cov` 实测 `web/main.py` **95%**（未覆盖部分为 MySQL 环境分支与防御性代码）
- **质量门禁**：CI 里 `--cov-fail-under=70`，覆盖率不达标直接 fail
- **报告**：每次运行生成单文件 HTML 报告（CI 上作为 Artifacts 可下载）

**测试抓到的真实缺陷（都已补回归用例）**：

| # | 缺陷 | 后果 |
|---|---|---|
| 1 | 空库 `SUM()` 返回 `None` | 统计接口崩溃 |
| 2 | 时长校验只写在 CLI，**Web 接口绕过** | 负数 / 0 / 超大时长直接进库 |
| 3 | `done` 字段被存成字符串 | 接口返回 `"1"` 而非布尔，前端 `if (done)` 恒真 |
| 4 | **表单接口完全没有校验**（`Form` 参数不走模型） | `minutes=0`、坏日期、纯空格全能进库 |
| 5 | 内容纯空格被当作合法内容 | `min_length=1` 只管字符数，没管"是否空白" |

## 🔄 持续集成（CI）

每次 `git push` 到 main 分支，GitHub Actions 自动执行：

1. 在干净的 Ubuntu 虚拟机拉取代码
2. 安装 Python 3.13 + 依赖（读 `requirements.txt`，与本地共用同一份清单）
3. 跑全部 106 个用例（业务层 + 接口层）
4. **覆盖率门禁**：`--cov-fail-under=70`，覆盖率低于 70% 直接 fail
5. **上传测试报告**：单文件 HTML 报告作为 Artifacts 可下载（`if: always()` —— 失败时也要能拿到报告）

全绿 ✅ 才代表这次提交合格；有红 ❌ 说明代码有问题，要回去改。配置在 `.github/workflows/ci.yml`。

## 🛠️ 技术栈

- Python 3
- SQLite / MySQL 8.0
- pymysql
- **FastAPI**（Web 接口层，12 个路由）+ **pydantic**（入参校验）
- pytest + **pytest-cov**（覆盖率）
- Git / GitHub（含 **GitHub Actions CI**）
- Linux（阿里云 ECS 部署运行）

## 🚀 使用方法

```bash
# 先装依赖（本地与 CI 共用一份清单）
pip install -r requirements.txt

# SQLite 版（零配置，直接跑）
python 记录学习日志脚本.py

# MySQL 版（需先在本机建 config.py 配置密码）
python db_mysql.py

# 运行全部测试
pytest -v
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
