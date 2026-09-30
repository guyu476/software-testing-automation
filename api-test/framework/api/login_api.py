"""登录相关接口的封装。

这一层只干一件事：把请求发出去，把响应原样返回。
它不做任何断言、不判断通过失败 —— 那是 testcases 层的活。

为什么要把「发请求」单独抽出来？
因为它是会被复用的。今天测试用例要登录，明天前置准备要登录，
后天做接口关联也要登录。写一次，处处调用。
"""
import requests

from config import BASE_URL, TIMEOUT

LOGIN_PATH = "/api/auth/login"
ME_PATH = "/api/auth/me"


def new_session():
    """开一个会话。

    会话的作用：它会把服务器返回的 Cookie 自动存下来，
    并在后续请求里自动带回去 —— 这就是「登录状态」能保持住的原因。

    你 Postman 里是靠 {{token}} 手动传；代码里一个 Session 对象就全办了。
    两种机制真实项目都会遇到，都要认识。
    """
    return requests.Session()


def login(account, password, session=None):
    """调用登录接口。

    account / password 传 None，表示「这个字段根本不传」，
    用来测「参数缺失」这种异常场景。

    返回：response 对象（原样返回，不解析、不断言）
    """
    payload = {}
    if account is not None:
        payload["account"] = account
    if password is not None:
        payload["password"] = password

    # 没传 session 就退回用 requests 模块本身（单次请求、不保持状态）
    http = session or requests
    return http.post(BASE_URL + LOGIN_PATH, json=payload, timeout=TIMEOUT)


def get_me(session):
    """查询「当前登录的是谁」。

    这个接口靠 Cookie 判断身份，所以必须拿着登录时那个 session 来调。
    """
    return session.get(BASE_URL + ME_PATH, timeout=TIMEOUT)
