#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地压测靶子服务器 (Local Load-Test Target)

用途：给 JMeter 提供一个"随便压、压垮了也没事"的靶子。
特点：
  - 只用 Python 标准库，不需要装任何东西
  - 只监听 127.0.0.1，外网无法访问
  - 多线程，能真正接住并发请求
  - 每来一个请求就在窗口里打一行，方便肉眼确认"JMeter 真的打过来了"

接口：
  GET /                    简易说明页
  GET /api/item?id=1       主压测目标，返回一段 JSON
  GET /api/slow?delay=300  故意慢 delay 毫秒返回（后面讲响应时间用）
  GET /health              健康检查
"""

import json
import sys
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST = "127.0.0.1"
PORT = 8000

# 用紧凑分隔符，让输出跟真实接口一样是 {"code":0,...} 没有多余空格
JSON_ARGS = {"ensure_ascii": False, "separators": (",", ":")}

_counter = {"total": 0}

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>本地压测靶子</title></head>
<body style="font-family:system-ui,-apple-system,'Microsoft YaHei';max-width:660px;margin:60px auto;line-height:1.8;color:#222">
<h2>本地压测靶子服务器已启动</h2>
<p>这个服务跑在你自己机器上，JMeter 压的是它，<b>不碰任何外部网站</b>。</p>
<ul>
  <li><code>/api/item?id=1</code> &mdash; 返回一个 JSON 条目（压测主目标）</li>
  <li><code>/api/slow?delay=300</code> &mdash; 故意慢 300 毫秒返回</li>
  <li><code>/health</code> &mdash; 健康检查</li>
</ul>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    # 用 HTTP/1.1，支持 keep-alive，跟真实服务器行为一致
    protocol_version = "HTTP/1.1"

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        raw = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        _counter["total"] += 1
        n = _counter["total"]

        u = urlparse(self.path)
        q = parse_qs(u.query)

        if u.path == "/":
            self._send(200, INDEX_HTML, "text/html; charset=utf-8")

        elif u.path == "/health":
            self._send(200, json.dumps({"status": "ok", "served": n}, **JSON_ARGS))

        elif u.path == "/api/item":
            try:
                iid = int((q.get("id") or ["1"])[0])
            except ValueError:
                iid = 1
            body = {
                "code": 0,
                "message": "0",
                "ttl": 1,
                "data": {
                    "id": iid,
                    "title": "本地测试条目 #%d" % iid,
                    "owner": "local-load-test-server",
                    "stat": {
                        "view": 10000 + iid,
                        "like": 200 + iid,
                        "reply": 30 + iid,
                    },
                    "served_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "served_by": "%s:%d" % (HOST, PORT),
                },
            }
            self._send(200, json.dumps(body, **JSON_ARGS))

        elif u.path == "/api/slow":
            try:
                delay = int((q.get("delay") or ["300"])[0])
            except ValueError:
                delay = 300
            delay = max(0, min(delay, 10000))
            time.sleep(delay / 1000.0)
            self._send(200, json.dumps({"code": 0, "delayed_ms": delay, "served": n}, **JSON_ARGS))

        else:
            self._send(404, json.dumps({"code": -404, "message": "not found"}, **JSON_ARGS))

    def log_message(self, fmt, *args):
        sys.stdout.write("[%s] req#%-6d  %s\n" % (datetime.now().strftime("%H:%M:%S"), _counter["total"], fmt % args))
        sys.stdout.flush()


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    line = "=" * 62
    print(line)
    print("  本地压测靶子已启动")
    print("  地址      : http://%s:%d" % (HOST, PORT))
    print("  主目标接口: http://%s:%d/api/item?id=1" % (HOST, PORT))
    print(line)
    print("  只监听本机 127.0.0.1，外网访问不到，压它没有任何风险。")
    print("  下面每来一个请求就滚一行 —— 压测时看到它在滚，")
    print("  就说明 JMeter 的流量确实打到这台服务器上了。")
    print(line)
    print("  这个窗口不要关。要停止，按 Ctrl+C 或直接关窗口。")
    print(line)
    sys.stdout.flush()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
