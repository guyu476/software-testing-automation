# UI 自动化测试框架（Selenium + pytest）

针对电商 demo 站（<http://119.45.177.154:3000>）的 Web UI 自动化测试。
与同目录的接口自动化框架（`api-test/`）配套：接口层验契约，UI 层验真实用户路径。

## 分层结构

```
ui-test/
├── requirements.txt
└── framework/
    ├── config.py            # 环境配置：站点地址、浏览器、超时、演示账号
    ├── driver_factory.py    # 驱动创建与销毁，全项目只此一处
    ├── conftest.py          # pytest fixture：session 级 driver + 每例清 Cookie
    ├── pytest.ini
    ├── pages/               # 页面对象：只负责「怎么操作页面」
    │   ├── base_page.py     #   基类：等待/定位/点击/取值的公共封装
    │   ├── login_page.py
    │   ├── home_page.py
    │   ├── product_page.py
    │   ├── cart_page.py
    │   └── checkout_page.py
    ├── data/
    │   └── login_cases.yaml # 测试数据：新增用例只改这里
    └── testcases/           # 用例：只负责「操作完对不对」
        ├── test_login.py         # 登录成功/失败/退出（数据驱动）
        ├── test_auth_guard.py    # 未登录访问受保护页面被重定向
        └── test_product_flow.py  # 首页→详情→加购→购物车→确认订单
```

分层规矩和 `api-test/framework` 一致：**pages 管操作、testcases 管断言、data 管数据**。
页面改版只动 `pages/`，用例逻辑不动。

## 设计要点

- **驱动自动管理**：靠 Selenium Manager 自动匹配 msedgedriver / chromedriver，
  不需要手工下载驱动、也不配 PATH。
- **session 级 driver**：整个测试会话只开一次浏览器，用例之间清 Cookie 隔离，
  而不是每条用例重启浏览器（否则 5 条用例要开 5 次浏览器）。
- **显式等待，禁用隐式等待**：`implicitly_wait(0)`。隐式等待会和显式等待
  叠加，导致实际等待时间不可控 —— 这是 UI 自动化最常见的坑之一。
- **定位器语义优先**：能用 `placeholder`、`aria-label`、按钮文案就不要用
  `nth-child` 这类结构选择器；结构一改就全断。
- **不污染被测环境**：链路用例验到「确认订单页渲染出提交按钮」为止，
  不点「提交订单」，避免往被测环境造订单数据。

## 怎么跑

```bash
cd D:\selenium\ui-test\framework

# 用装了 selenium 的解释器（本机是 Python 3.13，不是你那个 .venv）
C:\Users\Lenovo\AppData\Local\Programs\Python\Python313\python.exe -m pytest

# 想看它自己点，就关掉无头
set UI_HEADLESS=0
C:\Users\Lenovo\AppData\Local\Programs\Python\Python313\python.exe -m pytest -v
```

跑完在当前目录生成 `report.html`（自包含单文件，可直接发给人看）。

## 环境变量

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `UI_BASE_URL` | `http://119.45.177.154:3000` | 换环境只改这个 |
| `UI_BROWSER` | `edge` | `edge` / `chrome` |
| `UI_HEADLESS` | `1` | 设 `0` 显示浏览器窗口 |
| `UI_TIMEOUT` | `15` | 显式等待上限（秒） |

## 用例覆盖

| 用例 | 验什么 |
| --- | --- |
| `test_login`（3 条，数据驱动） | 正常登录跳转并建立登录态；密码错误给出错误文案；不勾协议不让提交 |
| `test_logout_clears_session` | 退出后回到游客态，会话确实清除 |
| `test_guest_redirected_to_login`（6 条） | /orders、/favorites、/checkout、/user、/merchant、/admin 未登录均重定向到 `/login?redirect=<原路径>`，且 redirect 参数不丢 |
| `test_guest_add_to_cart_redirects` | 未登录点加购跳登录页，不静默失败 |
| `test_product_list_renders` | 首页商品卡片正常渲染 |
| `test_product_detail_renders` | 详情页渲染，且商品名与列表页一致 |
| `test_add_to_cart_then_checkout` | 已登录的完整链路：加购 → 购物车有货 → 确认订单页可提交 |
