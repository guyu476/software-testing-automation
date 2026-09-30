# -*- coding: utf-8 -*-
"""购物车页对象。

定位器核对自 src/app/cart/page.tsx：
  - 结算按钮文案随勾选数量变化：「请勾选商品」/「去结算（N 种）」
    所以用 contains 匹配「去结算」，不能写死全等
  - 勾选圈：aria-label="勾选结算" / "取消勾选"
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.checkout_page import CheckoutPage


class CartPage(BasePage):
    PATH = "/cart"

    CHECKOUT_BUTTON = (By.XPATH, "//button[contains(normalize-space(),'去结算')]")
    CHECK_ALL_LABEL = (By.CSS_SELECTOR, "[aria-label='勾选结算']")
    EMPTY_HINT = (By.XPATH, "//*[contains(text(),'购物车') and contains(text(),'空')]")

    def load(self):
        self.open(self.PATH)
        return self

    def wait_loaded(self):
        self.visible(By.TAG_NAME, "body")
        return self

    def has_items(self):
        """购物车里有东西时才会出现结算按钮。"""
        return self.has(*self.CHECKOUT_BUTTON, timeout=5)

    def go_to_checkout(self):
        self.click(*self.CHECKOUT_BUTTON)
        self.wait_url_contains("/checkout")
        return CheckoutPage(self.driver)
