# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

单文件 Python 工具（`checkin.py`），用于 ikuuu.nl 的每日签到。**只用标准库 `urllib`**，无第三方依赖。

## 认证方式：Cookie

两种来源（`--cookie` 优先于文件）：

1. 命令行参数 `--cookie "<cookie string>"` —— 供 harness / skill 调用
2. 同目录 `cookie.txt`（`.gitignore` 排除，不入库）—— 本地手动用

直接 `POST /user/checkin`，无登录环节。

**不要**改回账号密码方式。`POST /auth/login` 已强制 Geetest V4 人机验证，没有验证码平台就过不去，实测 2026-04-12 报 `系统无法接受您的验证结果`。

Cookie 会过期，用户需要定期手动刷新（F12 抓包 → 替换 `cookie.txt`）。不要为此引入"自动刷新 Cookie"之类的复杂逻辑，手动更新是有意为之的简洁方案。

## 运行

```bash
python3 checkin.py                                    # 用 cookie.txt
python3 checkin.py --cookie "uid=...; email=...; ..."  # 显式传 Cookie
```

未传 `--cookie` 时，脚本从 `Path(__file__).resolve().parent / "cookie.txt"` 读取 —— 所以 `cookie.txt` 必须与 `checkin.py` 在同一目录。

## 退出码

| Code | 含义 |
|---|---|
| 0 | 成功（`ret=1`） |
| 1 | `cookie.txt` 缺失/空 |
| 2 | HTTPError |
| 3 | URLError（网络问题） |
| 4 | 响应非 JSON —— Cookie 过期的典型症状 |
| 5 | `ret=0`（含"今天已经签过了"这类情况） |

## 架构

一个 `main()` 函数干完所有事，没有类、没有模块拆分。修改时优先保持这种"一眼看完"的扁平度，不要为了"可扩展性"提前抽象。
