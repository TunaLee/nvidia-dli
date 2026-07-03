#!/usr/bin/env bash
# 옵션 1) Cloudflare 빠른 터널 — 계정/도메인 불필요, 공개 HTTPS URL 즉석 발급.
# 프록시(127.0.0.1:8080)를 공개합니다. 출력되는 https://xxx.trycloudflare.com 를 수강생에게 배포.
set -euo pipefail
PORT="${1:-8080}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "cloudflared 미설치 → 설치 안내:"
  echo "  # Ubuntu/aarch64"
  echo "  curl -L -o cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
  echo "  chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/"
  exit 1
fi
echo "▶ Cloudflare 터널 시작 (→ http://localhost:${PORT}).  아래 trycloudflare.com URL 을 배포하세요."
echo "  수강생 base_url = https://<발급URL>/v1"
exec cloudflared tunnel --url "http://localhost:${PORT}"
