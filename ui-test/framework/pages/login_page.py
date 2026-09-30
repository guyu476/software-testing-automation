# -*- coding: utf-8 -*-
"""登录页对象。

定位器全部对着站点源码核过（src/app/login/page.tsx），不是猜的：
  - 邮箱/手机号输入框：placeholder="邮箱 / 手机号"（用 placeholder 而不是 type，
    因为页面上有 4 个 input，只有这个能稳定区分「密码登录」这一栏）
  - 密码输入框：type=password
  - 提交按钮：type=submit，文案在「登录 / 重置密码」之间切换
  - 错误提示：<p class="text-sm text-red-500">
  - 协议勾选：type=checkbox，不勾不让提交
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class LoginPage(BasePage):
    PATH = "/login"

    ACCOUNT_INPUT = (By.CSS_SELECTOR, "input[placeholder='邮箱 / 手机号']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "button[type='submit']")
    AGREE_CHECKBOX = (By.CSS_SELECTOR, "input[type='checkbox']")
    ERROR_TEXT = (By.CSS_SELECTOR, "p.text-red-500")

    def load(self):
        self.open(self.PATH)
        self.visible(*self.ACCOUNT_INPUT)
        return self

    def agree_terms(self):
        """勾选服务协议 —— 不勾选点提交会提示「请先阅读并同意」。"""
        box = self.find(*self.AGREE_CHECKBOX)
        if not box.is_selected():
            box.click()
        return self

    def login(self, account, password, agree=True):
        """填表并提交。返回自身，方便链式调用（不负责断言 —— 那是用例层的活）。"""
        if agree:
            self.agree_terms()
        self.type(*self.ACCOUNT_INPUT, account)
        self.type(*self.PASSWORD_INPUT, password)
        self.click(*self.SUBMIT_BUTTON)
        return self

    # ---------- 取值，供用例断言 ----------
    def error_message(self):
        return self.text_of(*self.ERROR_TEXT)

    def has_error(self):
        return self.has(*self.ERROR_TEXT, timeout=6)

    def is_submit_enabled(self):
        return self.find(*self.SUBMIT_BUTTON).is_enabled()
