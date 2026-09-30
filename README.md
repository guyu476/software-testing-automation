# 软件测试自动化实践

针对一个真实部署的多角色电商平台（Next.js 16 + MySQL，约 30 个 API、12 个数据模型）
做的一整套测试实践：接口自动化、UI 自动化、性能测试、数据库练习。

被测站点：<http://119.45.177.154:3000>（演示环境，站点页脚公示了演示账号）

## 目录

| 目录 | 内容 | 技术栈 |
| --- | --- | --- |
| [`api-test/`](api-test) | 接口自动化框架，三层分层 + YAML 数据驱动 | Python / pytest / requests / PyYAML / pytest-html |
| [`ui-test/`](ui-test) | Web UI 自动化框架，Page Object 分层 | Python / Selenium 4 / pytest |
| [`perf-test/`](perf-test) | JMeter 压测计划与一键压测脚本、结果数据 | JMeter / Python |
| [`db-practice/`](db-practice) | MySQL 建表与查询练习 | MySQL |
| [`docs/`](docs) | 学习过程沉淀的笔记（接口测试 / pytest / 压测 / 抓包 / 数据库） | HTML |

## 各模块说明

### api-test —— 接口自动化

```
framework/
├── config.py                 # 环境配置：被测地址、超时
├── api/login_api.py          # api 层：只负责「怎么发请求」
├── testcases/test_login.py   # testcases 层：只负责「发了之后对不对」
├── data/login_cases.yaml     # data 层：用例数据，新增用例只改这里
└── pytest.ini
```

分层规矩：**api 层不发断言、testcases 层不拼请求、data 层承载数据**。
用 pytest 参数化驱动登录接口 4 条用例（正常登录 / 密码错误 / 缺 password 字段 /
账号密码为空），断言覆盖 HTTP 状态码与响应体业务码双层；
用 `requests.Session` 自动携带 Cookie 串联「登录 → 查询当前用户」验证接口关联。

跑法：

```bash
cd api-test/framework
pip install -r ../../ui-test/requirements.txt   # 含 pytest / requests / PyYAML / pytest-html
pytest                                          # 生成 report.html
```

详见 [api-test/framework/03_framework.html](api-test/framework/03_framework.html)。

### ui-test —— Web UI 自动化

```
framework/
├── config.py                 # 环境配置：站点地址、浏览器、超时、演示账号
├── driver_factory.py         # 驱动创建，靠 Selenium Manager 自动匹配，无需手装驱动
├── conftest.py               # session 级 driver + 用例间会话隔离
├── pages/                    # 页面对象：只负责「怎么操作页面」
└── testcases/                # 用例：只负责断言
```

覆盖 14 条用例：登录成功 / 密码错误 / 未勾选协议、退出会话清除、
6 个受保护页面的越权重定向、首页与详情页渲染、加购到结算的完整链路。

工程要点：

- **禁用隐式等待**（`implicitly_wait(0)`），只留显式等待——两者叠加会让实际等待时间失控
- **session 级复用浏览器**，登录态跨用例传递，避免每条用例重启浏览器
- **定位器语义优先**：用 `placeholder`、按钮文案、`aria-label`，不用结构选择器
- **不污染被测环境**：链路用例验到「确认订单页渲染出提交按钮」为止，不提交订单

跑法：

```bash
cd ui-test/framework
python -m pytest                    # 无头模式
set UI_HEADLESS=0 && python -m pytest   # 想看着它自己点
```

### perf-test —— 性能测试

`03_ecommerce_demo.jmx` 是三接口对比基线：不查库的健康检查、查库分页的商品列表、
最重的首页 SSR（131KB HTML）。用 `run_loadtest.py` 一键跑：

```bash
python run_loadtest.py      # 自动起服务 → 健康检查 → 预热路由 → JMeter → 汇总
```

实测结果（`results/statistics-报告-演示.json`）：

| 接口 | 样本 | 平均响应 | p90 |
| --- | --- | --- | --- |
| 全部 | 200 | 368 ms | 616 ms |
| 商品列表 api | 50 | 237 ms | 348 ms |
| 首页 SSR | 50 | 499 ms | 671 ms |

20 并发 × 5 轮，错误率 0%。**SSR 渲染比接口慢一倍以上**，这是压测得出的主要结论。

脚本里两个值得说的设计：**压测前必须预热路由**（dev 模式首次访问要编译，
不预热测的是编译器不是应用）、**健康检查确认服务真能响应**（端口在听 ≠ 服务能用）。

## 环境要求

- Python 3.13 + `pytest` / `requests` / `PyYAML` / `pytest-html`
- UI 自动化额外需要 `selenium>=4.6`（驱动由 Selenium Manager 自动下载）与本机 Edge 或 Chrome
- 性能测试需要 JMeter 5.x 与 JDK

## 说明

- 所有用例针对公开的演示环境运行，账号为站点页脚公示的演示账号，以及为自动化
  单独注册的测试账号；仓库内不含任何生产密钥、数据库连接串或私有凭据。
- `perf-test/results/` 只保留统计结果 JSON 与图表截图，JMeter 的 `.jtl` 明细与
  自动生成的 HTML dashboard 未纳入版本控制。
