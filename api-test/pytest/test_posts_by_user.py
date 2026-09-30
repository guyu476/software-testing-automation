"""
第一讲：把 Postman 里的「数据驱动 8 条用例」翻译成代码

Postman 里你点过的东西  ->  代码里对应的东西
------------------------------------------------------------------
请求方法 + URL          ->  requests.get(url, params=...)
环境变量 {{userId}}      ->  params 字典里的一个值
Tests 里的断言           ->  assert 语句
导入的 CSV 数据文件      ->  csv.DictReader 一行行读进来
Collection Runner 迭代  ->  @pytest.mark.parametrize
报告里的用例名           ->  pytest.param(..., id="用例名")
"""
import csv
import pathlib

import pytest
import requests

# ---------- 1. 被测接口（和你 Postman 里那个是同一个地址）----------
BASE_URL = "https://jsonplaceholder.typicode.com/posts"

# ---------- 2. 测试数据文件 ----------
# __file__ 是「当前这个 py 文件」的路径
# .with_name(...) 表示「换成同目录下的这个文件名」
# 这样写的好处：不管你从哪个目录敲 pytest 命令，都能找到这份 CSV
CSV_FILE = pathlib.Path(__file__).with_name("posts_by_user.csv")


def load_cases():
    """把 CSV 的每一行，变成一条 pytest 用例参数"""
    cases = []
    with open(CSV_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cases.append(
                pytest.param(
                    row["userId"],              # 第 1 个参数
                    int(row["expectedStatus"]), # 第 2 个参数（CSV 读出来是字符串，要转成数字）
                    int(row["expectedCount"]),  # 第 3 个参数
                    id=row["caseName"],         # 报告里显示的用例名
                )
            )
    return cases


# ---------- 3. 一条测试用例 = 发请求 + 断言 ----------
@pytest.mark.parametrize("user_id, expected_status, expected_count", load_cases())
def test_posts_by_user(user_id, expected_status, expected_count):
    # 【发请求】对应 Postman 里点 Send
    resp = requests.get(BASE_URL, params={"userId": user_id}, timeout=10)

    # 【断言 1】状态码  对应 postman: pm.response.to.have.status(200)
    assert resp.status_code == expected_status

    # 【断言 2】返回条数  对应 postman: pm.expect(jsonData.length).to.eql(10)
    assert len(resp.json()) == expected_count
