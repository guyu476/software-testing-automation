# -*- coding: utf-8 -*-
"""浏览器驱动管理 —— 全项目只有这里负责创建和销毁 driver。

两个要点：
1. 用 Selenium Manager 自动匹配驱动，不需要手工下载 msedgedriver/chromedriver，
   也不需要配 PATH。Edge 和 Chrome 都是官方支持的。
2. driver 只在 session 级别创建一次，一个测试类共用；每个用例结束只清 Cookie，
   不重启浏览器 —— 否则 5 条用例要开 5 次浏览器，慢得没意义。
"""
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from config import BROWSER, HEADLESS, WINDOW_SIZE


def _common_args():
    args = [
        "--disable-gpu",
        "--no-first-run",
        "--disable-extensions",
        "--disable-popup-blocking",
        f"--window-size={WINDOW_SIZE}",
        "--lang=zh-CN",
    ]
    if HEADLESS:
        args.append("--headless=new")
    return args


def create_driver():
    """按 config.BROWSER 创建 driver。"""
    if BROWSER == "chrome":
        options = ChromeOptions()
        for a in _common_args():
            options.add_argument(a)
        driver = webdriver.Chrome(options=options)
    else:
        options = EdgeOptions()
        for a in _common_args():
            options.add_argument(a)
        driver = webdriver.Edge(options=options)

    driver.set_page_load_timeout(60)
    driver.implicitly_wait(0)  # 一律用显式等待，隐式等待会和显式等待互相干扰
    return driver


def quit_driver(driver):
    if driver is None:
        return
    try:
        driver.quit()
    except Exception:
        pass
