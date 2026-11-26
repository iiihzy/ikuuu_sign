# ikuuu 自动签到

用 Cookie 替你每天在 [ikuuu.top](https://ikuuu.top) 点一下"每日签到"的小脚本。Python 标准库，零依赖。

## 为什么是 Cookie 而不是账号密码

ikuuu 的登录接口 `/auth/login` 已经强制 Geetest V4 人机验证，账密方式走不通。Cookie 方式绕过登录环节，直接用已登录会话调 `/user/checkin`。代价是 Cookie 会过期（通常一个月以上），需要偶尔手动更新。

## 准备 Cookie

1. 浏览器登录 ikuuu，打开 `https://ikuuu.top/user`
2. `F12` → **Network** 标签页
3. 手动点一次"每日签到"按钮
4. 在请求列表里找到 `checkin` 这个 POST 请求
5. 在 **Headers → Request Headers** 里复制 `Cookie:` 冒号后面的整串
6. 粘贴到本目录的 `cookie.txt`（新建此文件），保存

关键字段是 `uid`、`email`、`key`，其他（`_ga*`、`_gid`）是统计用的，留着不影响。

## 使用

三种 Cookie 来源，优先级 **`--cookie` > `IKUUU_COOKIE` 环境变量 > `cookie.txt`**：

```bash
# 方式 A：本地手动用，读取同目录 cookie.txt
python3 checkin.py

# 方式 B：通过环境变量传入（适合 OpenClaw、Claude Code 等 harness）
IKUUU_COOKIE="uid=...; email=...; key=..." python3 checkin.py

# 方式 C：命令行参数显式传入（适合一次性调用或调试）
python3 checkin.py --cookie "uid=...; email=...; key=..."
```

输出示例：

```
[2026-04-12 09:05:00] ret=1 msg=获得了 88 MB 流量
```

## 退出码

| 退出码 | 含义 |
|---|---|
| 0 | 签到成功 |
| 1 | `cookie.txt` 不存在或为空 |
| 2 | HTTP 错误（4xx/5xx） |
| 3 | 网络错误 |
| 4 | 响应不是 JSON —— **Cookie 多半已过期**，重新抓一次覆盖 `cookie.txt` |
| 5 | 接口返回 `ret=0`（一般是"今天已经签过了"） |

## 定时执行

自己用 cron / launchd 之类的安排即可，比如每天早上 9 点跑一次：

```
5 9 * * * /usr/bin/python3 /path/to/ikuuu_sign/checkin.py >> /tmp/ikuuu.log 2>&1
```

## 安全

- `cookie.txt` 已在 `.gitignore` 中，**不会**被提交
- 建议把它的权限设成 600：`chmod 600 cookie.txt`
- Cookie 等价于你的登录态，不要贴到公开地方
