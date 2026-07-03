#!/usr/bin/env bash
# 옵션 2) Tailscale Funnel — 이미 Tailscale 이 깔려 있으니 추가 설치 없이 공개 HTTPS.
# 프록시(127.0.0.1:8080)를 https://<host>.<tailnet>.ts.net 로 공개.
# 사전 조건: tailnet 관리자 콘솔에서 Funnel 허용(HTTPS 인증서 + funnel 노드 속성).
set -euo pipefail
PORT="${1:-8080}"
echo "▶ Tailscale Serve/Funnel 설정 (→ http://localhost:${PORT})"
tailscale serve --bg --https=443 "http://127.0.0.1:${PORT}"
tailscale funnel --bg 443
echo "--- 상태 ---"
tailscale funnel status
echo "수강생 base_url = https://<위 ts.net 호스트>/v1"
