"""
dli-llm · NVIDIA DLI 강의용 LLM 클라이언트
────────────────────────────────────────
수강생은 강사에게 받은 키만 넣으면 됩니다.

    import os
    os.environ["DLI_API_KEY"] = "강사에게-받은-키"

    from dli_llm import chat, healthcheck
    healthcheck()                       # 연결 확인
    print(chat("연차 휴가는 며칠 전에 신청하나요?"))

기존 노트북(OpenAI 방식)과 함께 쓰려면:

    from dli_llm import get_client, MODEL
    llm = get_client()                  # openai.OpenAI 인스턴스
    llm.chat.completions.create(model=MODEL, messages=[...])

환경변수
  DLI_API_KEY / NVIDIA_API_KEY  (필수) 개인 키
  DLI_BASE_URL  엔드포인트, 기본값은 NVIDIA build (아래 상수)
  DLI_MODEL     모델 id, 기본값은 아래 상수
"""
from __future__ import annotations
import os
from openai import OpenAI

# 기본: NVIDIA build. 강사 DGX로 쓰려면 DLI_BASE_URL=http://124.51.229.210:30001/v1
DEFAULT_BASE_URL = os.getenv("DLI_BASE_URL", "https://integrate.api.nvidia.com/v1")
MODEL = os.getenv("DLI_MODEL", "qwen/qwen3.5-397b-a17b")

__all__ = ["chat", "get_client", "healthcheck", "MODEL"]


def _key() -> str:
    k = os.getenv("DLI_API_KEY") or os.getenv("NVIDIA_API_KEY")
    if not k:
        raise RuntimeError("API 키가 없습니다. DLI_API_KEY 또는 NVIDIA_API_KEY 환경변수를 설정하세요.")
    return k


def get_client() -> OpenAI:
    """설정 완료된 openai.OpenAI 인스턴스를 반환 (기존 노트북 코드와 호환)."""
    return OpenAI(base_url=DEFAULT_BASE_URL, api_key=_key())


def chat(prompt: str, system: str | None = None, *,
         max_tokens: int = 512, temperature: float = 0.2, model: str = MODEL) -> str:
    """질문 하나 → 답변 문자열. (thinking-off·max_tokens 상한은 서버 프록시가 강제)"""
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    out = get_client().chat.completions.create(
        model=model, messages=msgs, max_tokens=max_tokens, temperature=temperature)
    return out.choices[0].message.content


def healthcheck() -> bool:
    """엔드포인트·키 연결 확인. 성공하면 True."""
    try:
        c = get_client()
        models = [m.id for m in c.models.list().data]
        print(f"✅ 연결 OK · endpoint={DEFAULT_BASE_URL} · 모델={models}")
        return True
    except Exception as e:
        print(f"❌ 연결 실패: {type(e).__name__}: {e}")
        print(f"   endpoint={DEFAULT_BASE_URL} · DLI_API_KEY {'설정됨' if os.getenv('DLI_API_KEY') else '없음'}")
        return False
