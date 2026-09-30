"""登录接口的测试用例。

这一层只干一件事：调 api 层拿到响应，然后断言。

分工记牢：
    api/       负责「怎么发请求」
    testcases/ 负责「发了之后对不对」
    data/      负责「用什么数据发」
"""
import pathlib

import pytest
import yaml

from api.login_api import get_me, login, new_session

# __file__ 是当前这个测试文件；parents[1] 就是 framework 目录
DATA_FILE = pathlib.Path(__file__).parents[1] / "data" / "login_cases.yaml"


def load_data():
    """读取 YAML 测试数据。

    对比上一讲的 CSV：csv 读出来全是字符串，所以要手动 int()；
    YAML 会自己认类型，200 就是数字 200，不用转换。
    """
    with open(DATA_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


DATA = load_data()


# ---------- 用例 1~4：数据驱动，共用这一个函数 ----------
@pytest.mark.parametrize("case", DATA["cases"], ids=lambda c: c["id"])
def test_login(case):
    resp = login(case["account"], case["password"])

    # 断言 1：HTTP 状态码
    assert resp.status_code == case["expect_status"]

    # 断言 2：响应体里的业务码
    assert resp.json()["code"] == case["expect_code"]


# ---------- 用例 5：接口关联 ----------
def test_login_then_get_me():
    """接口关联：先登录拿到会话，再用同一个会话问「我是谁」。

    这就是你 Postman「接口关联」那讲的代码版 —— 取 → 存 → 用。
    区别是：Postman 里靠 {{token}} 手工传递，这里靠 session 自动携带 Cookie。
    """
    account = DATA["test_account"]["account"]
    password = DATA["test_account"]["password"]

    session = new_session()

    login_resp = login(account, password, session=session)
    assert login_resp.status_code == 200, "登录没成功，后面的关联断言就没意义了"

    me_resp = get_me(session)
    assert me_resp.status_code == 200
    # 未登录时这个接口返回 data: null，登录后才有数据 —— 这就是关联生效的证据
    assert me_resp.json()["data"] is not None
