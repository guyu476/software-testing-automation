#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键压测 ecommerce-demo（plan 3）。

由 一键压测-电商项目.bat 调用。整个流程：
  1. 端口 3000 没服务 -> 自己把 next dev 起起来；已经有服务 -> 直接用
  2. 健康检查：确认 /api/health 真的返回 200（端口在听 != 服务能用）
  3. 预热路由：dev 模式首次访问要编译，必须排掉，否则测的是编译器
  4. JMeter CLI 模式跑 03_ecommerce_demo.jmx，同时生成官方 HTML dashboard
  5. 打印每个接口的汇总，打开浏览器看报告
  6. 只关掉"自己启动的"那个服务（复用别人的就不动）
"""

import csv
import os
import shutil
import socket
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = r"D:\ecommerce-demo"
PERF = r"D:\selenium\perf-test"
RESULTS = os.path.join(PERF, "results")
NODE_EXE = r"C:\Program Files\nodejs\node.exe"
NEXT_BIN = os.path.join(ROOT, "node_modules", "next", "dist", "bin", "next")
JMETER_BAT = r"D:\selenium\jmeter\bin\jmeter.bat"
JDK = r"C:\Program Files\Java\jdk-21.0.10"
JMX = os.path.join(PERF, "03_ecommerce_demo.jmx")
JTL = os.path.join(RESULTS, "ecommerce.jtl")
REPORT = os.path.join(RESULTS, "ecommerce-report")
DEVLOG = os.path.join(RESULTS, "dev-server.log")
TASKKILL = r"C:\Windows\System32\taskkill.exe"

HOST = "127.0.0.1"
PORT = 3000
HEALTH = "/api/health"
WARMUP = ["/api/health", "/api/products?page=1&pageSize=10", "/"]
WARMUP_ROUNDS = 2

BAR = "=" * 62


def hr():
    print(BAR, flush=True)


def step(n, total, text):
    print("", flush=True)
    print("[%d/%d] %s" % (n, total, text), flush=True)


def http_get(path, timeout=120):
    """Minimal HTTP/1.1 GET over a raw socket. Returns (status, ttfb_ms, total_ms, bytes)."""
    s = None
    t0 = time.perf_counter()
    try:
        s = socket.create_connection((HOST, PORT), timeout=timeout)
        req = ("GET %s HTTP/1.1\r\nHost: %s:%d\r\nUser-Agent: Mozilla/5.0\r\n"
               "Accept: */*\r\nConnection: close\r\n\r\n" % (path, HOST, PORT))
        s.sendall(req.encode("ascii"))
        buf = bytearray()
        first = None
        while True:
            chunk = s.recv(65536)
            if not chunk:
                break
            if first is None:
                first = time.perf_counter()
            buf += chunk
        total = (time.perf_counter() - t0) * 1000
        ttfb = ((first - t0) * 1000) if first else total
        head = bytes(buf).split(b"\r\n", 1)[0]
        try:
            status = int(head.split(b" ")[1])
        except Exception:
            status = -1
        return status, round(ttfb, 1), round(total, 1), len(buf)
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc), None, None
    finally:
        try:
            if s:
                s.close()
        except Exception:
            pass


def port_listening():
    try:
        c = socket.create_connection((HOST, PORT), timeout=2)
        c.close()
        return True
    except Exception:
        return False


def kill_tree(pid):
    try:
        subprocess.run([TASKKILL, "/PID", str(pid), "/T", "/F"],
                       capture_output=True, timeout=30)
    except Exception:
        pass
    for _ in range(40):
        if not port_listening():
            return True
        time.sleep(0.5)
    return False


def main():
    os.makedirs(RESULTS, exist_ok=True)

    hr()
    print("  ecommerce-demo   一键压测   (测试计划 03, JMeter 命令行模式)", flush=True)
    hr()

    # ---------------- 1. make sure something is serving on 3000 ----------------
    started_by_us = False
    proc = None
    logf = None

    if port_listening():
        step(1, 5, "端口 3000 已有服务在跑 —— 直接复用（压测完我不会关它）")
    else:
        step(1, 5, "端口 3000 空闲 —— 正在为你启动 next dev ...")
        env_node = os.environ.copy()
        env_node["PATH"] = (r"C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;"
                            r"C:\Program Files\nodejs")
        env_node["NODE_ENV"] = "development"
        logf = open(DEVLOG, "w", encoding="utf-8", errors="replace")
        proc = subprocess.Popen([NODE_EXE, NEXT_BIN, "dev", "-p", str(PORT)],
                                cwd=ROOT, env=env_node, stdout=logf,
                                stderr=subprocess.STDOUT)
        started_by_us = True
        t0 = time.perf_counter()
        ready = False
        for _ in range(240):
            if port_listening():
                ready = True
                break
            if proc.poll() is not None:
                break
            time.sleep(0.5)
        if not ready:
            print("        !! 服务在 120 秒内没有监听 3000 端口，日志末尾：", flush=True)
            logf.flush()
            try:
                with open(DEVLOG, encoding="utf-8", errors="replace") as fh:
                    for line in fh.read().splitlines()[-30:]:
                        print("          " + line, flush=True)
            except Exception:
                pass
            kill_tree(proc.pid)
            return 1
        print("        端口就绪，用时 %.1f 秒（pid=%d）" % (time.perf_counter() - t0, proc.pid),
              flush=True)

    # ---------------- 2. health check: a listening socket is not proof of life ---
    step(2, 5, "确认服务真的能响应（端口在听 ≠ 服务能用）...")
    st, ttfb, total, blen = http_get(HEALTH, timeout=120)
    if st != 200:
        print("        !! %s 没有返回 200（实际：%s）" % (HEALTH, st), flush=True)
        print("        !! 拒绝压测一个不响应的服务。日志末尾：", flush=True)
        if started_by_us and logf:
            logf.flush()
            try:
                with open(DEVLOG, encoding="utf-8", errors="replace") as fh:
                    for line in fh.read().splitlines()[-30:]:
                        print("          " + line, flush=True)
            except Exception:
                pass
        if started_by_us and proc:
            kill_tree(proc.pid)
        return 1
    print("        %s 返回 200（%.0f ms）—— 服务是活的。" % (HEALTH, ttfb), flush=True)

    # ---------------- 3. warm up ----------------
    step(3, 5, "预热路由（dev 模式首次访问要编译，不能把编译时间算进结果）...")
    for rnd in range(1, WARMUP_ROUNDS + 1):
        for path in WARMUP:
            st, ttfb, total, blen = http_get(path)
            print("        第%d轮  %-34s %s   %.3f s" % (
                rnd, path, st if st else "连接失败", (total or 0) / 1000), flush=True)
    print("        -> 路由已编译完成，下面 JMeter 的数字才是应用本身的耗时。", flush=True)

    # ---------------- 4. JMeter ----------------
    step(4, 5, "运行 JMeter：20 并发 × 5 轮 × 3 个接口 = 300 个请求")
    if os.path.isdir(REPORT):
        shutil.rmtree(REPORT, ignore_errors=True)
    if os.path.exists(JTL):
        os.remove(JTL)

    env_jm = os.environ.copy()
    env_jm["PATH"] = (r"C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;"
                      + os.path.join(JDK, "bin"))
    env_jm["JAVA_HOME"] = JDK
    t0 = time.perf_counter()
    try:
        r = subprocess.run([JMETER_BAT, "-n", "-t", JMX, "-l", JTL, "-e", "-o", REPORT],
                           env=env_jm, cwd=PERF, capture_output=True, text=True,
                           errors="replace", timeout=900)
        out = (r.stdout or "") + (r.stderr or "")
        rc = r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "JMETER TIMEOUT", -1
    print("        jmeter 退出码=%s  墙钟=%.1f 秒" % (rc, time.perf_counter() - t0), flush=True)
    for line in out.splitlines():
        if "summary" in line and "Err:" in line:
            print("        | " + line.strip(), flush=True)

    ok_report = os.path.exists(os.path.join(REPORT, "index.html"))
    if not ok_report:
        print("        !! 没有生成 HTML 报告，jmeter 输出末尾：", flush=True)
        for line in out.splitlines()[-25:]:
            print("          " + line, flush=True)
    else:
        print("        HTML 报告：%s" % os.path.join(REPORT, "index.html"), flush=True)

    # ---------------- 5. summarise ----------------
    step(5, 5, "结果汇总")
    if os.path.exists(JTL):
        with open(JTL, newline="", encoding="utf-8", errors="replace") as fh:
            rows = list(csv.DictReader(fh))
        groups = {}
        for row in rows:
            groups.setdefault(row["label"], []).append(row)
        print("", flush=True)
        print("        总请求数：%d" % len(rows), flush=True)
        print("", flush=True)
        print("        %-42s %5s %9s %9s %9s %7s" % (
            "接口", "n", "平均(ms)", "最快(ms)", "最慢(ms)", "错误"), flush=True)
        total_err = 0
        for label, g in groups.items():
            el = [int(x["elapsed"]) for x in g]
            errs = sum(1 for x in g if x["success"].lower() != "true")
            total_err += errs
            print("        %-42s %5d %9.0f %9d %9d %7d" % (
                label, len(g), sum(el) / len(el), min(el), max(el), errs), flush=True)
        print("", flush=True)
        print("        总错误数：%d  错误率：%.2f%%" % (
            total_err, 100.0 * total_err / max(1, len(rows))), flush=True)
        if total_err:
            print("", flush=True)
            print("        --- 前 3 条失败原因 ---", flush=True)
            bad = [x for x in rows if x["success"].lower() != "true"][:3]
            for x in bad:
                print("          %s | %s | %s" % (x["label"], x["responseCode"],
                                                  x["responseMessage"][:90]), flush=True)

    if ok_report:
        print("", flush=True)
        print("        正在浏览器里打开报告 ...", flush=True)
        try:
            os.startfile(os.path.join(REPORT, "index.html"))
        except Exception as exc:
            print("        打不开浏览器：%s" % exc, flush=True)

    # ---------------- cleanup ----------------
    print("", flush=True)
    if started_by_us and proc:
        print("        关闭我启动的那个 dev server ...", flush=True)
        kill_tree(proc.pid)
        print("        端口 3000 已释放：%s" % (not port_listening()), flush=True)
    else:
        print("        服务是你自己启动的，保持运行不动它。", flush=True)
    if logf:
        logf.close()

    hr()
    print("  完成。", flush=True)
    hr()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
