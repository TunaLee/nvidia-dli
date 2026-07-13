# Day 06 · 캡스톤 — 나만의 MCP 서버 만들기

## 목표

**직접 도구(Tool)를 만들어 MCP 서버를 구성한다. LLM은 NVIDIA API(Qwen)를 쓴다.**

주제는 자유. 핵심은 "실제로 쓸 만한 도구"를 만드는 것이다.

한 문장으로:

> 내가 만든 도구들 → FastMCP 서버 → **NVIDIA Qwen 에이전트가 그 도구를 스스로 골라 호출** → 배포.

---

## 무엇을 만드나 (Day1~5를 녹여서)

### 반드시 담을 것

1. **내가 만든 여러 도구로 구성된 MCP 서버** (`server.py`, FastMCP) — `Day3`
   - 최소 하나는 **행동(부작용) Tool**, 최소 하나는 **읽기/검색** 도구
   - Inspector로 도구가 제대로 뜨는지 확인
2. **친절한 에러 · 입력 검증** — 잘못된 입력에 "무엇을·어떻게 고쳐라"를 알려준다 — `Day5`
3. **에이전트 데모** — **NVIDIA API(Qwen)** 가 tool-calling으로 내 도구를 골라 실제 질문을 푸는 노트북 — `Day5`
4. **배포** — Horizon(공개 URL) 또는 로컬 HTTP 엔드포인트로 호출 가능하게 — `Day5`

### 더 하면 좋은 것 (자유 — 배운 걸 많이 녹일수록 좋다)

- **검색을 진짜 RAG로** — 임베딩 · 하이브리드 · 리랭커 — `Day1~2`
- **Resource + Prompt** — 읽기 URI 리소스, 재사용 프롬프트, 서버 합성(`mount`) — `Day4`
- **똑똑한 기능** — 구조화 출력(Pydantic) / sampling(서버가 NVIDIA API 호출) / elicitation(사용자 확인) / Context 진행 보고 / annotations — `Day5`

> 억지로 다 넣지 말 것. 주제에 **자연스럽게 맞는 것**만 녹인다.

---

## 진행 흐름 (제안)

1. 주제·데이터 정하고 **도구 목록** 스케치
2. 도구 구현 → `server.py` 구성 (Inspector로 확인)
3. **NVIDIA Qwen 에이전트 데모** (tool-calling)
4. 배포 (Horizon / 로컬 HTTP)
5. 다듬기 · 에러·검증 보강 · 시연 준비

---

## 주제가 막히면 (씨앗)

- **리서치 비서** — 웹 검색 + 결과 저장 + 요약
- **나들이 플래너** — 날씨(open-meteo, 키 불필요) + 장소 정보 + 일정 만들기
- **학습 도우미** — 자료 검색 + 퀴즈 생성 + 오답 기록
- **가계부 분석** — CSV 읽기 + 분류 + 통계

→ 하지만 **자기가 실제로 쓸 것**을 만드는 게 가장 좋다.

---

## 제출 방법

프로젝트를 아래 구조의 **디렉터리**로 만들어 제출한다. (폴더 zip 또는 GitHub repo 링크)

```
내프로젝트/
├── server.py          # MCP 서버 — 내가 만든 도구들
├── client.py          # 에이전트 — NVIDIA Qwen이 도구를 호출
├── requirements.txt   # 의존성 (fastmcp, openai 등 실제 쓴 것만)
├── README.md          # 주제 한 줄 · (배포했다면) 공개 URL · 실행법
└── .env.example       # 키 '이름'만 (예: NVIDIA_API_KEY=)
```

**각 파일에 담을 것**
- `server.py` — FastMCP 서버. 도구 최소 2개(읽기 1개+, 행동/부작용 1개+), 잘못된 입력엔 친절한 에러.
- `client.py` — Qwen이 tool-calling으로 `server.py`의 도구를 골라 쓰는 에이전트 루프. `if __name__ == "__main__":` 로 바로 실행되게.
- `requirements.txt` — `pip freeze` 말고 실제 쓴 것만.
- `README.md` — 무엇을 하는 도구인지, 실행 명령, (배포 시) 공개 URL.

**넣지 말 것**
- `.env` (실제 키) — 절대 금지. 키 이름만 `.env.example` 에.
- `.venv/`, `__pycache__/`, 대용량 데이터

**내기 전 자가 점검**
- [ ] `fastmcp inspect server.py` 로 도구가 뜬다
- [ ] `python client.py` 가 오류 없이 끝까지 돌아 답을 낸다 (E2E)
- [ ] 잘못된 입력에 친절한 에러가 난다
- [ ] `.env` 는 빼고 `.env.example` 만 넣었다
- [ ] README 에 주제·실행법(·배포 URL)이 있다

---

## 이런 걸 신경 쓰면 좋다

- 실제로 **쓰고 싶은** 도구인가?
- 도구가 **작고 명확**한가? (하나가 한 가지 일만)
- 이름·설명이 **모델이 고르기 좋게** 쓰였나? (설명 = 모델용 프롬프트)
- 배운 걸 **자연스럽게** 녹였나?

---

## 시작 도움

- **NVIDIA API 키**: `NVIDIA_API_KEY`(`nvapi-...`) — `getpass` 또는 환경변수로. **코드에 하드코딩 금지.**
- **LLM 모델**: `qwen/...-instruct` + `extra_body={"chat_template_kwargs": {"enable_thinking": False}}` (thinking 끄기 — 토큰 폭주 방지)
- **참고 코드**:
  - `day05/Day05_Tool_MCP_실습.ipynb` — 도구 · 친절한 에러 · sampling · 에이전트 tool-calling
  - `day05/deploy/` — `server.py` 통합 예시 · 배포 안내 · 클라이언트 노트북
