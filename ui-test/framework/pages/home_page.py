# -*- coding: utf-8 -*-
"""首页对象：商品卡片列表 + 顶部导航（用来判断登录态）。

定位器核对自：
  - components/product-card.tsx：卡片是 <a href="/products/{id}">，商品名在 <h3>
  - components/user-nav.tsx：登录后出现「退出」按钮，未登录是「登录」链接
"""
from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class HomePage(BasePage):
    PATH = "/"

    # 首页有两类指向商品的链接：轮播图（a 里是 div+p，标题用 <h2>）
    # 和商品卡片（a 里是 div+h3，标题用 <h3>）。
    # 用 :has(h3) 只要商品卡片，否则 open_first_product 会点进轮播拿到错的标题。
    PRODUCT_LINKS = (By.CSS_SELECTOR, "a[href^='/products/']:has(h3)")
    PRODUCT_TITLES = (By.CSS_SELECTOR, "a[href^='/products/'] h3")
    LOGOUT_BUTTON = (By.XPATH, "//button[normalize-space()='退出']")
    LOGIN_LINK = (By.CSS_SELECTOR, "a[href='/login']")

    def load(self):
        self.open(self.PATH)
        return self

    def wait_products_loaded(self):
        self.find_all(*self.PRODUCT_LINKS)
        return self

    def product_count(self):
        return len(self.find_all(*self.PRODUCT_LINKS))

    def first_product_name(self):
        return self.text_of(*self.PRODUCT_TITLES)

    def open_first_product(self):
        """点第一个商品卡进详情页。"""
        self.clickable(*self.PRODUCT_LINKS).click()
        self.wait_url_contains("/products/")
        return self

    # ---------- 登录态判断 ----------
    def is_logged_in(self):
        return self.has(*self.LOGOUT_BUTTON, timeout=3)

    def is_logged_out(self):
        return self.has(*self.LOGIN_LINK, timeout=3)
