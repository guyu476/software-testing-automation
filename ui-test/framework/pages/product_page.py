# -*- coding: utf-8 -*-
"""商品详情页对象。

定位器核对自 src/components/add-to-cart-button.tsx：
  - 加购按钮：<button type="button">加入购物车</button>
  - 关键交互：未登录时点它不会报错，而是跳 /login?redirect=当前路径
    —— 这正是「未登录加购」这条用例的断言依据
  - 有 SKU 的商品，加购按钮带 disabled，必须先选规格
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class ProductDetailPage(BasePage):
    ADD_TO_CART = (By.XPATH, "//button[normalize-space()='加入购物车']")
    ADD_TO_CART_HINT = (By.XPATH, "//p[contains(text(),'已加入购物车')]")
    # SkuPicker 里的规格按钮（有 SKU 的商品才出现）
    SKU_OPTIONS = (By.CSS_SELECTOR, "button[type='button'][class*='rounded']")

    def wait_loaded(self):
        self.wait_url_contains("/products/")
        self.visible(*self.ADD_TO_CART)
        return self

    def product_name(self):
        return self.find(By.TAG_NAME, "h1").text.strip()

    def is_add_to_cart_enabled(self):
        return self.find(*self.ADD_TO_CART).is_enabled()

    def select_first_sku(self):
        """有规格的商品：点第一个可选规格。没有 SKU 时静默返回。"""
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait
        try:
            WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable(self.SKU_OPTIONS)
            )
        except Exception:
            return False
        self.click(*self.SKU_OPTIONS)
        return True

    def add_to_cart(self):
        """点加购。若按钮因未选规格而禁用，先尝试选规格。"""
        if not self.is_add_to_cart_enabled():
            self.select_first_sku()
        self.click(*self.ADD_TO_CART)
        return self

    def added_successfully(self):
        return self.has(*self.ADD_TO_CART_HINT, timeout=8)
