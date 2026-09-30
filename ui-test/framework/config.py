# -*- coding: utf-8 -*-
"""环境配置：换环境只改这一个文件。

被测对象是公网部署的 demo 站（站点页脚公示了演示账号）。
用环境变量覆盖即可切换环境，不改代码：
    set UI_BASE_URL=http://127.0.0.1:3000
    set UI_BROWSER=chrome
    set UI_HEADLESS=0
"""
import os

# 被测站点
BASE_URL = os.getenv("UI_BASE_URL", "http://119.45.177.154:3000")

# 浏览器：edge / chrome
BROWSER = os.getenv("UI_BROWSER", "edge").lower()

# 无头模式。CI 上跑用 1；本地想看着它自己点，设 UI_HEADLESS=0
HEADLESS = os.getenv("UI_HEADLESS", "1") != "0"

# 显式等待上限（秒）。页面是 SSR + 客户端二次渲染，给足但不无限等
TIMEOUT = int(os.getenv("UI_TIMEOUT", "15"))

WINDOW_SIZE = "1440,900"

# 站点页脚公示的演示账号，密码统一 123456
ACCOUNTS = {
    "user": ("demo@example.com", "123456"),
    "merchant": ("merchant@example.com", "123456"),
    "merchant2": ("merchant2@example.com", "123456"),
    "admin": ("admin@example.com", "123456"),
}

# 故意写错的密码，用于反向用例
WRONG_PASSWORD = "definitely-not-the-password"
