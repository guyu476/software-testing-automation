# -*- coding: utf-8 -*-
"""登录功能 UI 用例（数据驱动）。

用例数据在 data/login_cases.yaml。新增一条异常场景只改 YAML，
这个文件一个字都不用动 —— 和接口自动化那套数据驱动是同一个思路。
"""
import pytest

from conftest import load_yaml
from pages.home_page import HomePage
from pages.login_page import LoginPage

DATA = load_yaml("login_cases.yaml")


@pytest.mark.parametrize("case", DATA["cases"], ids=lambda c: c["id"])
def test_login(driver, case):
    page = LoginPage(driver).load()
    page.login(case["account"], case["password"], agree=case["agree"])

    if case["expect_success"]:
        # 成功：离开登录页，且顶部出现「退出」——这是登录态最可靠的证据
        HomePage(driver).wait_url_contains("119.45.177.154:3000")
        assert HomePage(driver).is_logged_in(), "登录后顶部没有出现「退出」，登录态未建立"
    else:
        # 失败：留在登录页，并且给出明确错误文案
        assert page.has_error(), "登录失败却没有给出任何错误提示"
        assert case["expect_error"] in page.error_message(), (
            f"错误文案不符，期望包含 {case['expect_error']!r}，实际 {page.error_message()!r}"
        )


def test_logout_clears_session(logged_in_user):
    """退出后应回到游客态：出现「登录」入口、「退出」消失。"""
    home = HomePage(logged_in_user)
    home.open()
    assert home.is_logged_in(), "前置条件失败：未处于登录态"

    home.click(*HomePage.LOGOUT_BUTTON)

    assert home.has(*HomePage.LOGIN_LINK, timeout=8), "退出后没有回到游客态"
    assert not home.is_logged_in(), "退出后「退出」按钮仍然存在，会话未清除"
