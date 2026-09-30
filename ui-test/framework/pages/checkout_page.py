# -*- coding: utf-8 -*-
"""确认订单页对象。

定位器核对自 src/app/checkout/page.tsx：
  - 标题：<h1>确认订单</h1>
  - 提交按钮文案：「提交订单（演示环境暂不付款）」
本框架只验证到「确认订单页正常渲染出提交按钮」为止，不真的提交 ——
自动化用例不应该往被测环境里造订单数据，这条边界要守住。
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    PATH = "/checkout"

    HEADING = (By.XPATH, "//h1[normalize-space()='确认订单']")
    SUBMIT_BUTTON = (By.XPATH, "//button[contains(normalize-space(),'提交订单')]")

    def wait_loaded(self):
        self.visible(*self.HEADING)
        return self

    def heading_text(self):
        return self.text_of(*self.HEADING)

    def submit_visible(self):
        return self.has(*self.SUBMIT_BUTTON, timeout=5)
