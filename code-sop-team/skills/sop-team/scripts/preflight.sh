#!/usr/bin/env bash
# 工程 SOP 专家团 · 第 0 步环境自检（macOS / Linux / Git Bash）
# 用法：bash preflight.sh [--root <代码目录>]
# 退出码：0 可开工 / 1 有阻塞项
set -u

ROOT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) ROOT="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

FAIL=""; WARN=""

ok_py() { [ -n "${1:-}" ] && [ -x "$1" ] && "$1" -V 2>&1 | grep -qE '^Python 3\.(8|9|1[0-9])'; }

# ---- 1) 定位闸门脚本 ----
GATE="${SOP_GATE:-}"
[ -n "$GATE" ] && [ -f "$GATE" ] || GATE="$(ls "$HOME"/.qwenworkcn/plugins-custom/*/bin/sop_gate.py 2>/dev/null | sort -r | head -1)"
if [ -n "${GATE:-}" ] && [ -f "$GATE" ]; then
  echo "OK   闸门: $GATE"
else
  echo "FAIL 闸门: 未找到 sop_gate.py（检查插件是否已安装；或设 SOP_GATE=<绝对路径>）"
  FAIL="$FAIL gate"
fi

# ---- 2) 定位 Python：PATH → QwenWork 记录 → WorkBuddy → 常见位置 ----
PY=""; WHERE=""
for c in python3 python py; do
  p="$(command -v "$c" 2>/dev/null)" || continue
  if ok_py "$p"; then PY="$p"; WHERE="PATH"; break; fi
done

if [ -z "$PY" ]; then
  REC="$HOME/.qwenworkcn/bin/.runtime-preparation.json"
  if [ -f "$REC" ]; then
    cand="$(grep -o '"executable"[[:space:]]*:[[:space:]]*"[^"]*"' "$REC" | head -1 | sed 's/.*"\([^"]*\)"$/\1/')"
    if ok_py "$cand"; then PY="$cand"; WHERE="QwenWork 运行时记录"; fi
  fi
fi

if [ -z "$PY" ]; then
  for p in $(ls -d "$HOME"/.workbuddy/binaries/python/versions/*/bin/python3 \
                   "$HOME"/.workbuddy/binaries/python/versions/*/python.exe 2>/dev/null | sort -Vr); do
    if ok_py "$p"; then PY="$p"; WHERE="WorkBuddy 受管 Python"; break; fi
  done
fi

if [ -z "$PY" ]; then
  for p in /usr/bin/python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    if ok_py "$p"; then PY="$p"; WHERE="常见安装位置"; break; fi
  done
fi

if [ -n "$PY" ]; then
  echo "OK   解释器: $PY"
  echo "      来源: $WHERE · 版本: $("$PY" -V 2>&1)"
else
  echo "FAIL 解释器: 未找到 Python 3.8+（PATH / QwenWork 记录 / WorkBuddy / 常见位置都没有）"
  echo "      安装: macOS → brew install python@3.12   Linux → apt install python3   Windows → winget install -e --id Python.Python.3.12"
  FAIL="$FAIL python"
fi

# ---- 3) 可选：项目侧自检 ----
if [ -n "$ROOT" ]; then
  if [ ! -d "$ROOT" ]; then
    echo "FAIL 目录: $ROOT 不存在"; FAIL="$FAIL root"
  elif [ -n "$PY" ] && [ -n "${GATE:-}" ] && [ -f "$GATE" ]; then
    OUT="$("$PY" "$GATE" doctor --root "$ROOT" 2>&1)"
    BAD="$(printf '%s\n' "$OUT" | grep -E '^FAIL' || true)"
    WN="$(printf '%s\n' "$OUT" | grep -E '^WARN' || true)"
    if [ -n "$BAD" ]; then printf '%s\n' "$BAD" | sed 's/^/FAIL doctor: /'; FAIL="$FAIL doctor"; fi
    if [ -n "$WN" ]; then printf '%s\n' "$WN" | sed 's/^/WARN doctor: /'; WARN="$WARN doctor"; fi
    [ -z "$BAD" ] && [ -z "$WN" ] && echo "OK   doctor: 全项通过"
  fi
fi

# ---- 4) 结论 ----
echo ""
if [ -n "$FAIL" ]; then
  echo "结论: BLOCK（${FAIL# }）—— 修完再开工；确实无法启用硬闸时必须明说「软约束降级模式」"
  exit 1
fi
if [ -n "$WARN" ]; then
  echo "结论: OK(有告警) —— 可开工，但要向用户说明告警影响"
else
  echo "结论: OK —— 后续统一用 \"$PY\" 调用闸门，不要假设 PATH 里有 python"
fi
exit 0
