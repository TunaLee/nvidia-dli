# -*- coding: utf-8 -*-
"""[실험] 계획 단계에 tools 를 주면 모델이 '실행'해버리는가?

Day07 슬라이드/노트북의 주장을 실제 Qwen(NVIDIA API)으로 검증한다.

  주장: "계획 단계에 tools 를 넘기면, 모델이 계획을 세우는 대신 그냥 실행해버린다.
        그래서 계획 호출엔 도구를 빼야 한다."

세 갈래로 비교한다 (같은 프롬프트, 도구만 다르게):
  A. tools 안 넘김                    → 계획이 나와야 정상
  B. tools 넘김 (tool_choice 없음)     → 주장대로면 '실행'(tool_calls)이 나온다
  C. tools 넘김 + tool_choice="none"   → 도구를 주되 '부르지 말라'고 명시

실행:
  # 키를 환경변수로 주거나
  set NVIDIA_API_KEY=nvapi-...        (Windows CMD)
  $env:NVIDIA_API_KEY="nvapi-..."     (PowerShell)
  export NVIDIA_API_KEY=nvapi-...     (bash)

  python day07/_실험_계획단계에_도구를_주면.py
"""
import os
import sys
import io
import getpass

if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

from openai import OpenAI

BASE = os.getenv("QWEN_BASE_URL", "https://integrate.api.nvidia.com/v1")
KEY = os.getenv("NVIDIA_API_KEY") or os.getenv("QWEN_API_KEY")
if not KEY:
    # .env 가 있으면 읽는다 (NVIDIA_API_KEY=nvapi-...)
    env = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.strip().startswith(("NVIDIA_API_KEY", "QWEN_API_KEY")) and "=" in line:
                KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
if not KEY:
    KEY = getpass.getpass("NVIDIA API 토큰(nvapi-...): ")

llm = OpenAI(base_url=BASE, api_key=KEY)
MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-next-80b-a3b-instruct")

TOOLS = [
    {"type": "function", "function": {
        "name": "add_task", "description": "할 일을 추가한다 (부작용)",
        "parameters": {"type": "object", "properties": {"title": {"type": "string"}},
                       "required": ["title"]}}},
    {"type": "function", "function": {
        "name": "list_tasks", "description": "할 일 목록을 읽는다 (읽기)",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "set_priority", "description": "작업 우선순위를 바꾼다 (낮음·보통·높음)",
        "parameters": {"type": "object",
                       "properties": {"task_id": {"type": "integer"}, "level": {"type": "string"}},
                       "required": ["task_id", "level"]}}},
]

SYSTEM = "해결 단계를 번호로 나열하라. 실행하지 말고 계획만 세워라."
USER = "'분기 보고서' 관련 할 일 3개를 만들고, 그중 마지막 것만 우선순위를 높음으로 올려줘."
N = 5


def run(label, **kw):
    called, planned, errors = 0, 0, 0
    samples = []
    for i in range(N):
        try:
            m = llm.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": USER}],
                temperature=0.2, max_tokens=400,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                **kw,
            ).choices[0].message
        except Exception as e:
            errors += 1
            samples.append(f"에러: {type(e).__name__}: {str(e)[:90]}")
            continue

        tcs = getattr(m, "tool_calls", None)
        content = (m.content or "").strip()
        # tool_choice="none" 일 때는 tool_calls 가 비지만, 모델이 여전히 도구를 부르려 해서
        # <tool_call> 원문이 content 로 새어나온다. 이것도 '실행 시도'로 세야 한다.
        leaked = "<tool_call>" in content
        if tcs:
            called += 1
            samples.append("도구 호출 → " + ", ".join(t.function.name for t in tcs))
        elif leaked:
            called += 1
            samples.append("⚠️ <tool_call> 원문 유출 (계획 아님) → " + content.replace("\n", " ")[:60])
        else:
            planned += 1
            samples.append("계획 텍스트 → " + content.replace("\n", " / ")[:70])

    print(f"\n── {label} ──")
    print(f"   도구 호출 {called}/{N} · 계획 텍스트 {planned}/{N} · 에러 {errors}/{N}")
    for s in samples:
        print("     ·", s)
    return called, planned, errors


print(f"모델: {MODEL}")
print(f"엔드포인트: {BASE}")
print(f"각 조건 {N}회씩 · temperature=0.2")
print("=" * 66)

a = run("A. tools 안 넘김 (계획 전용 호출)")
b = run("B. tools 넘김 (tool_choice 없음)", tools=TOOLS)
c = run("C. tools 넘김 + tool_choice='none'", tools=TOOLS, tool_choice="none")

print("\n" + "=" * 66)
print("판정")
print("=" * 66)
if b[0] > b[1]:
    print("✅ 주장 확인 — 도구를 주면 모델이 계획 대신 '실행'해버린다.")
    print(f"   (B에서 {b[0]}/{N} 회 도구를 호출)")
elif b[1] > b[0]:
    print("❌ 주장 반박 — 도구를 줘도 모델이 지시를 지켜 '계획'을 세웠다.")
    print(f"   (B에서 {b[1]}/{N} 회 계획만 냄)  → 슬라이드/노트북 문구를 고쳐야 한다.")
else:
    print("⚠️ 애매 — 절반씩 갈렸다. 신뢰할 수 없으니 도구를 빼는 편이 안전하다.")

if c[2] == 0:
    if c[1] > c[0]:
        print("\n➕ tool_choice='none' 도 계획을 냈다 — 이 방법도 쓸 수 있다.")
    else:
        print("\n🚨 tool_choice='none' 은 해결책이 아니다.")
        print("   도구 호출이 '파싱만' 안 될 뿐, 모델은 여전히 도구를 부르려 한다.")
        print("   그 결과 <tool_call> 원문이 content 로 새어나온다 — 계획이 아니라 쓰레기다.")
        print("   → 계획 단계에는 tools 를 아예 넘기지 마라.")
else:
    print(f"\n➖ tool_choice='none' 은 이 엔드포인트에서 에러 ({c[2]}/{N}) — 쓸 수 없다.")
