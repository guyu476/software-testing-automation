# -*- coding: utf-8 -*-
"""Page 基类 —— 所有页面对象继承它，把「等待 + 定位」的脏活收在一处。

分层规矩和接口自动化那套一致：
    pages/      负责「怎么操作页面」（定位、点击、取值）
    testcases/  负责「操作完对不对」（断言）
    data/       负责「用什么数据测」

这样页面改版时只动 pages/，用例逻辑不用碰。
"""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, TIMEOUT


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    # ---------- 定位 ----------
    def find(self, by, value, timeout=None):
        w = WebDriverWait(self.driver, timeout or TIMEOUT)
        return w.until(EC.presence_of_element_located((by, value)))

    def find_all(self, by, value, timeout=None):
        w = WebDriverWait(self.driver, timeout or TIMEOUT)
        w.until(EC.presence_of_element_located((by, value)))
        return self.driver.find_elements(by, value)

    def clickable(self, by, value, timeout=None):
        w = WebDriverWait(self.driver, timeout or TIMEOUT)
        return w.until(EC.element_to_be_clickable((by, value)))

    def visible(self, by, value, timeout=None):
        w = WebDriverWait(self.driver, timeout or TIMEOUT)
        return w.until(EC.visibility_of_element_located((by, value)))

    # ---------- 操作 ----------
    def click(self, by, value, timeout=None):
        self.clickable(by, value, timeout).click()

    def type(self, by, value, text, timeout=None):
        el = self.visible(by, value, timeout)
        el.clear()
        el.send_keys(text)

    def text_of(self, by, value, timeout=None):
        return self.visible(by, value, timeout).text.strip()

    # ---------- 断言辅助 ----------
    def has(self, by, value, timeout=3):
        """限时探测元素是否存在，不存在返回 False（用于「不应该出现」的断言）。"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return True
        except TimeoutException:
            return False

    def wait_url_contains(self, fragment, timeout=None):
        w = WebDriverWait(self.driver, timeout or TIMEOUT)
        return w.until(EC.url_contains(fragment))

    def wait_text_present(self, text, timeout=None):
        w = WebDriverWait(self.driver, timeout or TIMEOUT)
        return w.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), text))

    # ---------- 导航 ----------
    def open(self, path=""):
        url = BASE_URL + path
        self.driver.get(url)
        return self

    @property
    def current_url(self):
        return self.driver.current_url

    @property
    def title(self):
        return self.driver.title

    @property
    def body_text(self):
        return self.find(By.TAG_NAME, "body").text
