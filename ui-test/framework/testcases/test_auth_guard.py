# -*- coding: utf-8 -*-
"""未登录访问受保护页面的重定向用例。

依据 src/proxy.ts：matcher 覆盖 /checkout /orders /favorites /user /merchant /admin，
未登录一律 302 到 /login?redirect=<原路径>。这是页面级第一道防线。
"""
import pytest
from urllib.parse import unquote

from pages.base_page import BasePage
from pages.home_page import HomePage

PROTECTED_PATHS = ["/orders", "/favorites", "/checkout", "/user", "/merchant", "/admin"]


@pytest.mark.parametrize("path", PROTECTED_PATHS)
def test_guest_redirected_to_login(driver, path):
    page = BasePage(driver).open(path)

    page.wait_url_contains("/login")
    # 注意：浏览器地址栏里的 redirect 是 URL 编码的（%2Forders），
    # 断言前必须先 unquote，否则永远匹配不上。
    url = unquote(page.current_url)
    assert "/login" in url, f"未登录访问 {path} 没有被重定向到登录页"
    # 重定向必须带上原始路径，否则登录后回不到用户本来想去的页面
    assert f"redirect={path}" in url, (
        f"重定向丢了 redirect 参数，当前 URL={page.current_url}"
    )


def test_guest_add_to_cart_redirects(driver):
    """未登录点「加入购物车」应跳登录页，而不是静默失败（依据 add-to-cart-button.tsx）。"""
    home = HomePage(driver).load().wait_products_loaded()
    home.open_first_product()

    from pages.product_page import ProductDetailPage

    detail = ProductDetailPage(driver).wait_loaded()
    detail.add_to_cart()

    detail.wait_url_contains("/login")
    assert "/login" in detail.current_url, "未登录加购没有跳转登录页"
