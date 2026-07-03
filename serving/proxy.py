"""
DLI 강의용 인증·정책 프록시
─────────────────────────────
수강생(공개 HTTPS) → [이 프록시] → SGLang(localhost:30000, Qwen3.5-35B-A3B)

이 프록시가 하는 일
- 수강생별 API 키 검증 (raw SGLang 키는 절대 노출 안 함)
- Qwen thinking(추론) 강제 OFF  → 깨끗한 직답 + 토큰/요청 대폭 감소
- max_tokens 상한 → 폭주 생성 1명이 전체를 굶기는 것 방지
- 키별 rate-limit + 전역 동시성 상한 → 30명 버스트 보호
- OpenAI 호환 passthrough (/v1/chat/completions, /v1/models, /health), 스트리밍 지원

실행:  serving/run_proxy.sh  참고
환경변수:
  SGLANG_URL        기본 http://localhost:30000
  SGLANG_KEY        (필수) 실제 SGLang --api-key 값
  KEYS_FILE         수강생 키 파일 (한 줄에 `key[,이름]`), 없으면 DLI_KEYS(콤마구분) 사용
  MODEL_ID          기본 Qwen/Qwen3.5-35B-A3B
  MAX_TOKENS_CEIL   기본 512
  FORCE_NO_THINK    기본 1 (thinking 강제 OFF)
  RATE_PER_MIN      키당 분당 요청 수, 기본 30
  MAX_CONCURRENCY   전역 동시 요청 상한, 기본 48
  PROXY_HOST/PORT   기본 127.0.0.1 / 8080
"""
from __future__ import annotations
import os, time, asyncio, collections
from typing import Any
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# ── 설정 ─────────────────────────────────────────────
SGLANG_URL      = os.getenv("SGLANG_URL", "http://localhost:30000").rstrip("/")
SGLANG_KEY      = os.getenv("SGLANG_KEY", "")
MODEL_ID        = os.getenv("MODEL_ID", "Qwen/Qwen3.5-35B-A3B")
MAX_TOKENS_CEIL = int(os.getenv("MAX_TOKENS_CEIL", "512"))
FORCE_NO_THINK  = os.getenv("FORCE_NO_THINK", "1") not in ("0", "false", "False", "")
RATE_PER_MIN    = int(os.getenv("RATE_PER_MIN", "30"))
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "48"))

def _load_keys() -> dict[str, str]:
    """{key: 이름} 매핑. KEYS_FILE 우선, 없으면 DLI_KEYS(콤마구분)."""
    keys: dict[str, str] = {}
    path = os.getenv("KEYS_FILE")
    if path and os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, _, name = line.partition(",")
            keys[k.strip()] = name.strip() or k.strip()[:8]
    else:
        for k in filter(None, (os.getenv("DLI_KEYS", "").split(","))):
            keys[k.strip()] = k.strip()[:8]
    return keys

STUDENT_KEYS = _load_keys()
_sema = asyncio.Semaphore(MAX_CONCURRENCY)
_hits: dict[str, collections.deque] = collections.defaultdict(collections.deque)
_client: httpx.AsyncClient | None = None
_bearer = HTTPBearer(auto_error=False)

app = FastAPI(title="DLI LLM Proxy")


@app.on_event("startup")
async def _startup():
    global _client
    if not SGLANG_KEY:
        raise RuntimeError("SGLANG_KEY 환경변수가 필요합니다 (실제 SGLang --api-key 값).")
    if not STUDENT_KEYS:
        print("⚠️  수강생 키가 비어 있습니다. KEYS_FILE 또는 DLI_KEYS 를 설정하세요.")
    _client = httpx.AsyncClient(base_url=SGLANG_URL, timeout=httpx.Timeout(300.0, connect=10.0))
    print(f"✅ proxy → {SGLANG_URL}  | 수강생 키 {len(STUDENT_KEYS)}개 | "
          f"no_think={FORCE_NO_THINK} | max_tokens≤{MAX_TOKENS_CEIL} | "
          f"rate={RATE_PER_MIN}/min | concurrency≤{MAX_CONCURRENCY}")


@app.on_event("shutdown")
async def _shutdown():
    if _client:
        await _client.aclose()


def _auth(cred: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    if cred is None or cred.credentials not in STUDENT_KEYS:
        raise HTTPException(401, "유효하지 않은 API 키입니다. 강사에게 발급받은 키를 확인하세요.")
    return cred.credentials


def _rate_limit(key: str):
    now = time.monotonic()
    dq = _hits[key]
    while dq and now - dq[0] > 60:
        dq.popleft()
    if len(dq) >= RATE_PER_MIN:
        raise HTTPException(429, f"요청이 너무 많습니다 (분당 {RATE_PER_MIN}회 제한). 잠시 후 다시 시도하세요.")
    dq.append(now)


def _apply_policy(body: dict[str, Any]) -> dict[str, Any]:
    body["model"] = MODEL_ID                                   # 모델 id 고정
    mt = body.get("max_tokens")
    body["max_tokens"] = min(int(mt), MAX_TOKENS_CEIL) if mt else MAX_TOKENS_CEIL
    if FORCE_NO_THINK:                                         # thinking 강제 OFF
        ctk = body.get("chat_template_kwargs") or {}
        ctk.setdefault("enable_thinking", False)
        body["chat_template_kwargs"] = ctk
    return body


@app.get("/health")
async def health():
    try:
        r = await _client.get("/health")
        return {"proxy": "ok", "upstream": r.status_code}
    except Exception as e:
        return JSONResponse({"proxy": "ok", "upstream": f"unreachable: {e}"}, status_code=503)


@app.get("/v1/models")
async def models(_: str = Depends(_auth)):
    r = await _client.get("/v1/models", headers={"Authorization": f"Bearer {SGLANG_KEY}"})
    return JSONResponse(r.json(), status_code=r.status_code)


@app.post("/v1/chat/completions")
async def chat_completions(request: Request, key: str = Depends(_auth)):
    _rate_limit(key)
    body = _apply_policy(await request.json())
    headers = {"Authorization": f"Bearer {SGLANG_KEY}", "Content-Type": "application/json"}
    stream = bool(body.get("stream"))
    async with _sema:
        if stream:
            async def gen():
                async with _client.stream("POST", "/v1/chat/completions",
                                          json=body, headers=headers) as up:
                    async for chunk in up.aiter_raw():
                        yield chunk
            return StreamingResponse(gen(), media_type="text/event-stream")
        r = await _client.post("/v1/chat/completions", json=body, headers=headers)
        return JSONResponse(r.json(), status_code=r.status_code)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("PROXY_HOST", "127.0.0.1"),
                port=int(os.getenv("PROXY_PORT", "8080")), log_level="info")
