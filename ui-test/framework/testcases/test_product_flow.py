# -*- coding: utf-8 -*-
"""核心业务链路 UI 用例：首页 → 商品详情 → 加入购物车 → 购物车 → 确认订单。

刻意不点「提交订单」：自动化用例不应该往被测环境里造订单数据。
验到「确认订单页渲染出提交按钮」为止，边界守在这里。
"""
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.product_page import ProductDetailPage


def test_product_list_renders(driver):
    """首页商品卡片能正常渲染 —— 这是所有下游链路的前置。"""
    home = HomePage(driver).load().wait_products_loaded()

    assert home.product_count() > 0, "首页一个商品卡片都没有渲染出来"
    assert home.first_product_name(), "商品卡片的标题是空的"


def test_product_detail_renders(driver):
    home = HomePage(driver).load().wait_products_loaded()
    name_on_list = home.first_product_name()
    home.open_first_product()

    detail = ProductDetailPage(driver).wait_loaded()

    assert detail.product_name(), "商品详情页没有渲染出商品名（h1 为空）"
    assert name_on_list in detail.product_name() or detail.product_name() in name_on_list, (
        f"详情页商品名与列表页不一致：列表={name_on_list!r} 详情={detail.product_name()!r}"
    )


def test_cart_shows_added_item(cart_ready_user):
    """前置已加购：购物车应能看到商品并给出结算入口。"""
    cart = CartPage(cart_ready_user).load().wait_loaded()

    assert cart.has_items(), "已加购但购物车里没有商品（结算按钮未出现）"


def test_add_to_cart_then_checkout(cart_ready_user):
    """完整链路：购物车有货 → 进确认订单页 → 提交按钮可用。

    这条是最有价值的用例 —— 它把「列表页渲染」「详情页渲染」「加购接口」
    「购物车读取」「结算页渲染」串起来，任何一段坏了它都会红。
    """
    cart = CartPage(cart_ready_user).load().wait_loaded()
    assert cart.has_items(), "前置条件失败：购物车为空"

    checkout = cart.go_to_checkout()
    checkout.wait_loaded()

    assert checkout.heading_text() == "确认订单", "确认订单页标题不对"
    assert checkout.submit_visible(), "确认订单页没有渲染出提交按钮"
