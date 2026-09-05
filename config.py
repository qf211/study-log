import os

# 数据库类型：本地 'sqlite'；服务器部署时改成 'mysql'
# 也支持通过环境变量 DATABASE_TYPE 覆盖（CI/服务器不依赖本地文件）
DATABASE_TYPE = os.environ.get('DATABASE_TYPE', 'sqlite')

# 数据库密码：优先读环境变量 DB_PASSWORD，读不到才用占位符兜底
# 这样真实密码不用写死在代码里，避免泄露
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'placeholder-not-a-real-password')
