import pytest

@pytest.mark.smoke
def test_records_empty(client):
    resp = client.get('/records')
    assert resp.status_code == 200
    assert resp.json() == []

@pytest.mark.smoke
def test_records(client):
    resp = client.post('/records', json={
        'date': '2026-09-03',
        'topic': 'web测试',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 200

    resp = client.get('/records')
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]['minutes'] == 30
    assert data[0]['topic'] == 'web测试'


# ===================== A 组：框架层校验（FastAPI/pydantic 白送的）=====================
# 这些不用自己写校验代码，但值得写成用例锁住：
# 万一以后有人改了模型定义/接口签名，这里会红 —— 相当于给"框架行为"也做个看守

def test_records_missing_minutes(client):
    """缺 minutes 字段 → 422（missing）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '缺时长字段',
        'done': False
    })
    assert resp.status_code == 422


def test_records_missing_topic(client):
    """缺 topic 字段 → 422（missing）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_records_minutes_wrong_type(client):
    """minutes 传字符串 'abc' → 422（类型不符）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '时长传字符串',
        'minutes': 'abc',
        'done': False
    })
    assert resp.status_code == 422


def test_records_date_wrong_type(client):
    """date 传数字 20260912 → 422（类型不符，字符串字段不收数字）"""
    resp = client.post('/records', json={
        'date': 20260912,
        'topic': '日期传数字',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_get_by_id_wrong_type(client):
    """GET /records/abc → 422（路径参数 id 必须是整数）"""
    resp = client.get('/records/abc')
    assert resp.status_code == 422


def test_get_by_date_missing_param(client):
    """GET /records/by_date 不带 date 参数 → 422（必填 query 参数）"""
    resp = client.get('/records/by_date')
    assert resp.status_code == 422


def test_put_wrong_id_type(client):
    """PUT /records/abc → 422（路径参数类型不符）"""
    resp = client.put('/records/abc', json={
        'date': '2026-09-12',
        'topic': '路径参数类型错',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_form_missing_minutes(client):
    """表单接口 POST /records-form 缺 minutes → 422
    注意：表单用 data=（form 编码），不是 json= """
    resp = client.post('/records-form', data={
        'date': '2026-09-12',
        'topic': '表单缺时长',
    })
    assert resp.status_code == 422


# ===================== B 组：业务校验缺口 =====================
# 期望值按"需求"写，不按代码现状写 → 现在会红，红 = 代码真的有漏洞
# 口径（本次定）：统一机制 —— 全部校验归 pydantic，一律返回 422

def test_records_minutes_negative(client):
    """需求：时长 1~600 分钟 → 负数该被拒（422）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '时长负数',
        'minutes': -10,
        'done': False
    })
    assert resp.status_code == 422


def test_records_minutes_zero(client):
    """需求：时长下限是 1 → 0 该被拒（422）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '时长为零',
        'minutes': 0,
        'done': False
    })
    assert resp.status_code == 422


def test_records_minutes_over_limit(client):
    """需求：时长上限是 600 → 601 该被拒（422）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '时长超上限',
        'minutes': 601,
        'done': False
    })
    assert resp.status_code == 422


@pytest.mark.parametrize("minutes, expected", [
    (1, 200),      # 合法边界（下限）
    (600, 200),    # 合法边界（上限）
    (601, 422),    # 越界
])
def test_records_minutes_boundary(client, minutes, expected):
    """边界值三兄弟：合法边界要能进，越界要拒"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '边界值测试',
        'minutes': minutes,
        'done': False
    })
    assert resp.status_code == expected


def test_records_empty_topic(client):
    """需求：内容不能为空 → 空串该被拒（422，min_length 管）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_records_bad_date(client):
    """需求：日期格式 YYYY-MM-DD → 斜杠格式该被拒（422，field_validator 管）"""
    resp = client.post('/records', json={
        'date': '2026/09/12',
        'topic': '日期格式错',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_records_topic_too_long(client):
    """需求（本次新定）：内容最长 200 字 → 3000 字该被拒（422，max_length 管）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '测' * 3000,
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


@pytest.mark.smoke
def test_update(client):
    resp = client.post('/records', json={
        'date': '2026-09-03',
        'topic': 'web测试',
        'minutes': 30,
        'done': False
    })
    new_id = resp.json()['id']
    assert resp.status_code == 200

    resp = client.put(f'/records/{new_id}', json={
        'date': '2026-09-03',
        'topic': 'fastAPI',
        'minutes': 30,
        'done': True
    })
    assert resp.status_code == 200
    resp = client.get('/records')
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]['topic'] == 'fastAPI'

@pytest.mark.smoke
def test_delete(client):
    resp = client.post('/records', json={
        'date': '2026-09-03',
        'topic': 'web测试',
        'minutes': 30,
        'done': False        
    })
    new_id = resp.json()['id']
    assert resp.status_code == 200
    resp = client.delete(f'/records/{new_id}')
    resp = client.get('/records')
    assert resp.json() == []

def test_404(client):
    resp = client.get('/records/999')
    assert resp.status_code == 404
    resp = client.delete('/records/999')
    assert resp.status_code == 404


# ===================== C 组：边界 / 安全 / 类型一致性 =====================

@pytest.mark.smoke
def test_stats_empty_db(client):
    """空库统计：COUNT/SUM 在空表上的行为（COALESCE 兜底成 0，不是 None）"""
    resp = client.get('/stats')
    assert resp.status_code == 200
    assert resp.json() == {'total_count': 0, 'total_minutes': 0}


def test_get_by_date_not_found(client):
    """查一个没人学过的日期 → 200 且空列表（不是 404）"""
    resp = client.get('/records/by_date', params={'date': '1900-01-01'})
    assert resp.status_code == 200
    assert resp.json() == []


def test_sql_injection_string_safe(client):
    """安全：带引号/分号/-- 的内容必须被当普通字符串处理（参数化查询），不能破坏表"""
    evil = "O'Brien; DROP TABLE study_log--"
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': evil,
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 200

    resp = client.get('/records')
    assert resp.status_code == 200
    assert resp.json()[0]['topic'] == evil, '内容应原样存取，不能丢字符'

    # 表还在：注入之后仍能正常写入
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '注入测试后写入',
        'minutes': 10,
        'done': False
    })
    assert resp.status_code == 200


def test_emoji_roundtrip(client):
    """emoji 能存能取（UTF-8 链路完整，不能被截断/转义坏）"""
    content = 'emoji😀测试🚀'
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': content,
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 200

    resp = client.get('/records')
    assert resp.status_code == 200
    assert resp.json()[0]['topic'] == content


def test_done_field_is_bool(client):
    """需求：done 是布尔值 → 接口返回也该是 true / false

    当前实现：库里 done 是 TEXT 列，布尔被存成 '1'，接口返回字符串 "1" ❌
    → 这条红 = 抓到第二个真 bug（前端若写 if (data.done)，字符串 "0" 也是真值）
    """
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': 'done字段类型',
        'minutes': 30,
        'done': True
    })
    assert resp.status_code == 200

    resp = client.get('/records')
    assert resp.status_code == 200
    actual = resp.json()[0]['done']
    assert actual is True, f"done 应为布尔 True，实际是 {actual!r}（类型 {type(actual).__name__}）"


# ===================== D 组：HTML 页面 / 表单流（补覆盖率缺口）=====================
# 背景：覆盖率报告显示 web/main.py 里这些路由一行都没被跑到
# （:49 GET /、:74-79 表单新增成功路径、:188-193 编辑页、:218-226 表单更新、:233-261 列表页）
# 页面类用例的断言方式：状态码 + 页面里应出现的关键字（不需要比对整页 HTML）

def _create_one(client, topic='页面用例'):
    """内部小工具：通过 JSON 接口建一条记录，返回 id（页面用例都要先有数据）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': topic,
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 200
    return resp.json()['id']


@pytest.mark.smoke
def test_index_page(client):
    """GET / 首页表单页 → 200，且含标题关键内容"""
    resp = client.get('/')
    assert resp.status_code == 200
    assert '学习日志管理器' in resp.text


@pytest.mark.smoke
def test_form_create_success(client):
    """表单新增的**成功路径**（之前只测了缺字段 422，没测正常提交）"""
    resp = client.post('/records-form', data={
        'date': '2026-09-12',
        'topic': '表单提交',
        'minutes': 45
    })
    assert resp.status_code == 200
    assert '添加成功' in resp.text

    # 验证真的入库了（页面返回成功 ≠ 数据进了库，要交叉验证）
    resp = client.get('/records')
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]['topic'] == '表单提交'


def test_edit_page_ok(client):
    """GET /edit/{id} 编辑页（有数据）→ 200，且带出原值"""
    new_id = _create_one(client, topic='待编辑')
    resp = client.get(f'/edit/{new_id}')
    assert resp.status_code == 200
    assert '编辑' in resp.text
    assert '待编辑' in resp.text, '编辑页应带出原有内容'


def test_edit_page_404(client):
    """GET /edit/999 编辑页（记录不存在）→ 404"""
    resp = client.get('/edit/999')
    assert resp.status_code == 404


def test_update_form_ok(client):
    """POST /records/{id}/update 表单更新成功 → 200，且库里真的改了"""
    new_id = _create_one(client, topic='更新前')
    resp = client.post(f'/records/{new_id}/update', data={
        'date': '2026-09-12',
        'topic': '更新后',
        'minutes': 60
    })
    assert resp.status_code == 200
    assert '修改成功' in resp.text

    resp = client.get('/records')
    assert resp.json()[0]['topic'] == '更新后'
    assert resp.json()[0]['minutes'] == 60


def test_update_form_404(client):
    """POST /records/999/update 更新不存在的记录 → 404"""
    resp = client.post('/records/999/update', data={
        'date': '2026-09-12',
        'topic': '不存在',
        'minutes': 30
    })
    assert resp.status_code == 404


@pytest.mark.smoke
def test_list_page(client):
    """GET /list 列表页 → 200，且渲染出记录与删除按钮"""
    _create_one(client, topic='列表用例')
    resp = client.get('/list')
    assert resp.status_code == 200
    assert '列表用例' in resp.text
    assert '删除' in resp.text, '列表页应带删除按钮（调 DELETE 接口的 JS）'


def test_put_not_found(client):
    """PUT /records/999 记录不存在 → 404（探测时验过，但一直没写成用例）"""
    resp = client.put('/records/999', json={
        'date': '2026-09-12',
        'topic': '不存在',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 404


def test_put_bad_date(client):
    """PUT 传非法日期 → 422（覆盖 UpdateRecord 的 date 校验分支）"""
    resp = client.put('/records/1', json={
        'date': '2026/09/12',
        'topic': '日期格式错',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


@pytest.mark.smoke
def test_get_record_by_id_ok(client):
    """GET /records/{id} 单条查询的**成功路径**（覆盖率报告揪出来的缺口：
    我们测了 404，却没测"查到一条存在的记录"）"""
    new_id = _create_one(client, topic='单条查询')
    resp = client.get(f'/records/{new_id}')
    assert resp.status_code == 200
    data = resp.json()
    assert data['id'] == new_id
    assert data['topic'] == '单条查询'
    assert data['done'] is False, 'done 也该是布尔值（同一套 _row_to_dict 处理）'


# ===================== E 组：异常专项（T5）=====================
# 期望值一律按"需求"写；会红的用例不是写错了，而是发现了 bug
# 需求口径（本次定）：校验失败统一返回 422（JSON 接口与表单接口一致）

# ---- 内容（topic）----

def test_topic_only_spaces_rejected(client):
    """内容全是空格 '   ' → 该被拒（422）

    需求是"内容不能为空"，而纯空格在业务上就是空。
    注意：min_length=1 只管字符个数，'   ' 长度是 3，所以它能混过去 ❗
    """
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '   ',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_topic_boundary_200_ok(client):
    """内容正好 200 字（合法边界）→ 应通过"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '测' * 200,
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 200


def test_topic_boundary_201_rejected(client):
    """内容 201 字（越界）→ 应被拒（422）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '测' * 201,
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


# ---- 时长（minutes）----

def test_minutes_float_rejected(client):
    """时长传浮点数 1.5 → 应被拒（分钟是整数）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '浮点时长',
        'minutes': 1.5,
        'done': False
    })
    assert resp.status_code == 422


def test_minutes_none_rejected(client):
    """时长传 null → 应被拒（必填字段）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '空时长',
        'minutes': None,
        'done': False
    })
    assert resp.status_code == 422


@pytest.mark.contract
def test_minutes_numeric_string_is_accepted(client):
    """时长传字符串 '30' → **当前会被接受**（pydantic 宽松模式自动转成 30）

    这不是 bug 也不是正确行为，而是"需求没定义"的地方。
    本用例的作用是**把当前行为钉住**：将来若改成严格模式（拒绝数字字符串），
    这条会红，提醒你"这里的行为变了，是有意的吗？"
    """
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '数字字符串时长',
        'minutes': '30',
        'done': False
    })
    assert resp.status_code == 200, '当前行为：宽松模式接受数字字符串（需求未定义）'


# ---- 日期（date）----

def test_date_empty_rejected(client):
    """日期传空串 '' → 应被拒（422）"""
    resp = client.post('/records', json={
        'date': '',
        'topic': '空日期',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_date_impossible_value_rejected(client):
    """日期 '2026-13-45'（格式对但值不存在）→ 应被拒（422）"""
    resp = client.post('/records', json={
        'date': '2026-13-45',
        'topic': '不存在的日期',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


def test_date_too_long_rejected(client):
    """日期传 300 字超长 → 应被拒（422）"""
    resp = client.post('/records', json={
        'date': '2' * 300,
        'topic': '超长日期',
        'minutes': 30,
        'done': False
    })
    assert resp.status_code == 422


# ---- 请求体本身 ----

def test_body_empty_object_rejected(client):
    """请求体是空对象 {} → 应被拒（422，缺必填字段）"""
    resp = client.post('/records', json={})
    assert resp.status_code == 422


def test_body_not_json_rejected(client):
    """请求体不是 JSON（纯文本）→ 应被拒（422）
    注意：传原始 body 用 content=，不是 data=（data= 是给表单用的）"""
    resp = client.post('/records', content='not-json',
                       headers={'Content-Type': 'text/plain'})
    assert resp.status_code == 422


def test_extra_field_ignored(client):
    """多传未知字段 → 忽略它，但**不能把它写进库里**（防脏数据/注入面扩大）"""
    resp = client.post('/records', json={
        'date': '2026-09-12',
        'topic': '多余字段',
        'minutes': 30,
        'done': False,
        'hacker': 'drop table'
    })
    assert resp.status_code == 200

    resp = client.get('/records')
    row = resp.json()[0]
    assert 'hacker' not in row, '未知字段不该进库'
    assert set(row.keys()) == {'id', 'date', 'topic', 'minutes', 'done'}


# ---- 重复提交（幂等性）----

@pytest.mark.contract
def test_duplicate_submit_creates_two_records(client):
    """重复提交同一条数据 → **当前会存两条**（无幂等）

    需求未定义"是否该去重"，所以本用例只钉住现状：
    若以后加了幂等/唯一约束，这条会红，提醒你契约变了。
    """
    payload = {'date': '2026-09-12', 'topic': '重复提交', 'minutes': 30, 'done': False}
    assert client.post('/records', json=payload).status_code == 200
    assert client.post('/records', json=payload).status_code == 200
    assert len(client.get('/records').json()) == 2, '当前行为：不去重'


# ---- PUT（更新）的负向 ----

def test_put_minutes_negative(client):
    """PUT 时长负数 → 应被拒（422）"""
    new_id = _create_one(client)
    resp = client.put(f'/records/{new_id}', json={
        'date': '2026-09-12', 'topic': '改', 'minutes': -1, 'done': False
    })
    assert resp.status_code == 422


def test_put_topic_empty(client):
    """PUT 内容空串 → 应被拒（422）"""
    new_id = _create_one(client)
    resp = client.put(f'/records/{new_id}', json={
        'date': '2026-09-12', 'topic': '', 'minutes': 30, 'done': False
    })
    assert resp.status_code == 422


def test_put_minutes_over_limit(client):
    """PUT 时长 601（越界）→ 应被拒（422）"""
    new_id = _create_one(client)
    resp = client.put(f'/records/{new_id}', json={
        'date': '2026-09-12', 'topic': '改', 'minutes': 601, 'done': False
    })
    assert resp.status_code == 422


# ---- 表单接口的负向（表单参数不走 pydantic 模型 → 目前完全没有校验）----

def test_form_minutes_zero_rejected(client):
    """表单新增：时长为 0 → 应被拒（422，与 JSON 接口同一口径）"""
    resp = client.post('/records-form', data={
        'date': '2026-09-12', 'topic': '表单零时长', 'minutes': '0'
    })
    assert resp.status_code == 422


def test_form_bad_date_rejected(client):
    """表单新增：日期格式非法 → 应被拒（422）"""
    resp = client.post('/records-form', data={
        'date': '2026/09/12', 'topic': '表单坏日期', 'minutes': '30'
    })
    assert resp.status_code == 422


def test_form_topic_only_spaces_rejected(client):
    """表单新增：内容纯空格 → 应被拒（422）"""
    resp = client.post('/records-form', data={
        'date': '2026-09-12', 'topic': '   ', 'minutes': '30'
    })
    assert resp.status_code == 422


def test_update_form_minutes_zero_rejected(client):
    """表单更新：时长为 0 → 应被拒（422）"""
    new_id = _create_one(client)
    resp = client.post(f'/records/{new_id}/update', data={
        'date': '2026-09-12', 'topic': '表单更新', 'minutes': '0'
    })
    assert resp.status_code == 422

