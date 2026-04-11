---
name: ikuuu-checkin
description: Perform the daily check-in (每日签到) on ikuuu.nl to claim the free traffic bonus. TRIGGER when the user asks to sign in / check in / 签到 to ikuuu, automate their ikuuu daily rewards, or test an ikuuu login cookie. Requires a valid login cookie passed via the `cookie` input; does not accept username/password (the login endpoint enforces Geetest captcha).
---

# ikuuu Daily Check-in

Automates the 每日签到 button on https://ikuuu.nl by POSTing to `/user/checkin` with an authenticated session cookie. Pure Python stdlib, no third-party dependencies.

## Inputs

| Name | Required | Description |
|------|----------|-------------|
| `cookie` | yes | Full `Cookie` header value from an authenticated ikuuu.nl browser session. Must include at least `uid`, `email`, `key`. Extra fields like `_ga*` are harmless. |

The user obtains the cookie by:

1. Logging in at https://ikuuu.nl
2. Opening DevTools → Network tab
3. Clicking the 每日签到 button once manually
4. Copying the value of the `Cookie:` request header on the resulting `POST /user/checkin` request

## Invocation

Run the bundled `checkin.py` from the skill directory, passing the cookie as `--cookie`:

```bash
python3 checkin.py --cookie "<cookie string>"
```

Notes:
- Use **double quotes** around the cookie string — it contains `;` and `=` which the shell would otherwise parse.
- If the cookie contains double quotes or `$`, quote with single quotes or escape accordingly.
- Python 3.8+ is sufficient. No `pip install` needed.

If `--cookie` is omitted, the script falls back to reading `cookie.txt` in the same directory. Harness invocations should always pass `--cookie` explicitly and not rely on the fallback.

## Output

The script prints one log line in the form `[YYYY-MM-DD HH:MM:SS] ret=<n> msg=<server message>` and exits with a code indicating the outcome:

| Exit | Meaning | How to react |
|------|---------|--------------|
| 0 | Check-in succeeded (`ret=1`) — reward granted | Report the `msg` (e.g. `获得了 88 MB 流量`) to the user |
| 1 | No cookie supplied | Ask the user to provide a cookie |
| 2 | HTTP error (4xx/5xx) from ikuuu | Likely transient — retry once; otherwise surface the status code |
| 3 | Network error (DNS, TCP, timeout) | Check connectivity; retry later |
| 4 | Response is not JSON — usually HTML login page | **Cookie has expired.** Ask the user to re-authenticate and supply a fresh cookie (see *Inputs* above) |
| 5 | `ret=0` — most often `您似乎已经签到过了...` | Not an error. Report that the user has already checked in today |

Exit code 5 is a **success-adjacent** outcome: the operation completed, but no new reward was granted because the user had already signed in that day. Skills calling this should treat it as a benign idempotency outcome, not a failure.

## Constraints and non-goals

- **Do not accept username/password.** `POST /auth/login` enforces Geetest V4 captcha and cannot be automated without a paid captcha-solving service. Cookie-based invocation is the only supported path.
- **Do not persist cookies anywhere except where the user tells you to.** The cookie is a long-lived credential; leaking it is equivalent to leaking a session.
- **Do not retry more than once on exit code 2/3.** Repeated failures should be surfaced, not hidden.
- **Do not parse HTML bodies.** If the response is not JSON, treat it as cookie expiry (exit 4) and stop.

## Files

- `checkin.py` — the invocable entry point
- `cookie.txt` — optional local fallback (gitignored); intended for manual/standalone use, not for skill invocations
- `README.md` — human-facing documentation
- `CLAUDE.md` — repo-level notes for Claude Code
- `SKILL.md` — this file
