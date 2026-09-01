"""
test_post.py — 用 Python 标准库向 FastAPI 发送 POST 请求
目的：测试刚才 add_record 接口能不能收到 body 落库
绕开 PowerShell + curl 的所有字符串转义坑
"""

import urllib.request          # Python 标准库：发 HTTP 请求
import json                     # Python 标准库：处理 JSON

# 1. 把 Python 字典转成 JSON 字符串（dict→str→bytes，JSON 双引号由 json.dumps 自动加上）
new_record = {
    "date":    "2026-09-01",
    "topic":   "put测试",
    "minutes": 30,
    "done":    True
}
data = json.dumps(new_record).encode('utf-8')

# 2. 构造一个 POST 请求（告诉服务器：方法 POST + URL + 数据 + 头）
req = urllib.request.Request(
    url='http://127.0.0.1:8000/records/10',
    data=data,                         # body
    headers={'Content-Type': 'application/json'},   # 告诉服务器：body 是 JSON
    method='PUT'
)

# 3. 发请求 + 拿响应 + 打印
with urllib.request.urlopen(req) as resp:
    body = resp.read().decode('utf-8')
    print(f"HTTP 状态码：{resp.status}")
    print(f"返回内容：{body}")
