# -*- coding: utf-8 -*-
"""pytest 全局 fixture。

driver 是 session 级的：整个测试会话只开一次浏览器，用例之间清 Cookie 隔离。
这是 UI 自动化的标准做法 —— 每条用例都重启浏览器会让执行时间翻好几倍。
"""
import pathlib
import sys

import pytest
import yaml

# 让 testcases/ 里能直接 import pages.* / config
FRAMEWORK_DIR = pathlib.Path(__file__).resolve().parent
if str(FRAMEWORK_DIR) not in sys.path:
    sys.path.insert(0, str(FRAMEWORK_DIR))

from config import ACCOUNTS, BASE_URL  # noqa: E402
from driver_factory import create_driver, quit_driver  # noqa: E402
from pages.home_page import HomePage  # noqa: E402
from pages.login_page import LoginPage  # noqa: E402


@pytest.fixture(scope="session")
def driver():
    d = create_driver()
    yield d
    quit_driver(d)


@pytest.fixture(autouse=True)
def clean_session(driver, request):
    """保证用例之间互不影响。

    默认清空 Cookie（回到游客态）；
    但如果用例声明了需要登录（或用 logged_in_user fixture），
    就把登录态存下来、跑完再恢复 —— 这样整个会话只登录一次，
    而不是每条用例都重走一遍登录流程。
    """
    needs_login = (
        "logged_in_user" in request.fixturenames
        or "requires_login" in request.keywords
    )
    saved = driver.get_cookies() if needs_login else None

    if not needs_login:
        try:
            driver.delete_all_cookies()
        except Exception:
            pass

    yield

    if saved is not None:
        # 用例跑完把登录态还回去，供下一条用例复用
        try:
            current = driver.current_url
            driver.get(BASE_URL)
            for c in saved:
                driver.add_cookie(c)
            driver.get(current)
        except Exception:
            pass


@pytest.fixture
def home(driver):
    return HomePage(driver).load()


@pytest.fixture
def login_page(driver):
    return LoginPage(driver).load()


def do_login(driver, account, password):
    """复用度最高的动作：走 UI 登录一次。"""
    LoginPage(driver).load().login(account, password)
    HomePage(driver).wait_url_contains(BASE_URL)
    return driver


@pytest.fixture
def logged_in_user(driver):
    """已登录的普通用户（demo@example.com）。"""
    account, password = ACCOUNTS["user"]
    do_login(driver, account, password)
    return driver


@pytest.fixture
def cart_ready_user(driver):
    """已登录 + 购物车里至少有一件商品。

    加购一次后整个会话复用，避免每条用例都重复「登录 → 加购」。
    """
    account, password = ACCOUNTS["user"]
    do_login(driver, account, password)

    from pages.cart_page import CartPage
    from pages.home_page import HomePage
    from pages.product_page import ProductDetailPage

    cart = CartPage(driver).load().wait_loaded()
    if not cart.has_items():
        home = HomePage(driver).load().wait_products_loaded()
        home.open_first_product()
        detail = ProductDetailPage(driver).wait_loaded()
        detail.add_to_cart()
        assert detail.added_successfully(), "前置准备失败：加购没有成功"
    return driver


def load_yaml(name):
    with open(FRAMEWORK_DIR / "data" / name, encoding="utf-8") as f:
        return yaml.safe_load(f)
