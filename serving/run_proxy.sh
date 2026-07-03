#!/usr/bin/env bash
# DGX에서 실행: 인증·정책 프록시를 SGLang 옆에 띄웁니다 (localhost:8080).
# 실제 SGLang api-key 는 실행 중인 프로세스에서 읽어 주입 (하드코딩 금지).
set -euo pipefail
cd "$(dirname "$0")"

PID=$(pgrep -f sglang.launch_server | head -1 || true)
if [ -z "${PID:-}" ]; then
  echo "❌ sglang.launch_server 프로세스를 못 찾음. SGLang이 떠 있는지 확인하세요." >&2
  exit 1
fi
export SGLANG_KEY="$(tr '\0' '\n' < /proc/$PID/cmdline | grep -A1 -x -- '--api-key' | tail -1)"
export SGLANG_URL="${SGLANG_URL:-http://localhost:30000}"
export KEYS_FILE="${KEYS_FILE:-$PWD/keys.txt}"
export MAX_TOKENS_CEIL="${MAX_TOKENS_CEIL:-512}"
export RATE_PER_MIN="${RATE_PER_MIN:-30}"
export MAX_CONCURRENCY="${MAX_CONCURRENCY:-48}"
export PROXY_HOST="${PROXY_HOST:-127.0.0.1}"
export PROXY_PORT="${PROXY_PORT:-8080}"

[ -f "$KEYS_FILE" ] || { echo "❌ 수강생 키 파일 없음: $KEYS_FILE  (gen_keys.py 로 생성)"; exit 1; }
echo "▶ proxy on ${PROXY_HOST}:${PROXY_PORT}  → ${SGLANG_URL}  (keys: $KEYS_FILE)"
exec python proxy.py
