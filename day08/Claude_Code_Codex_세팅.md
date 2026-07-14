# 코딩 에이전트 세팅 & 편의기능 — Claude Code · Codex

Day08에서 다루는 **하네스**(에이전트를 돌리는 런타임)를 직접 써보기 위한 준비 문서.
두 도구 모두 터미널에서 도는 코딩 에이전트다. 설치 방법은 거의 같고, 갈리는 건 **로그인 방식**이다.

> 주의: 이 둘은 각자 Anthropic / OpenAI 계정과 모델을 쓴다. 강의에서 쓰던 **NVIDIA Qwen 키와는 완전히 별개**다.

---

## 공통 준비물

- **Git** — Claude Code의 Bash 도구, Codex의 저장소 작업에 필요.
  - PowerShell: `winget install Git.Git`  ·  확인: `git --version`
- **Node.js** — npm으로 설치할 때만 필요(네이티브 설치는 불필요). 필요하면:
  - PowerShell: `winget install OpenJS.NodeJS.LTS`  ·  확인: `node -v`
- **작업 폴더** — 코딩 에이전트는 git 저장소 안에서 진가를 낸다. 빈 폴더라도 하나 준비.

터미널이 PowerShell인지 CMD인지는 프롬프트로 구분한다 — `PS C:\...>`면 PowerShell, `C:\...>`면 CMD.

---

## Claude Code 설치

**네이티브 설치(권장, 백그라운드 자동 업데이트)**

```powershell
# Windows PowerShell
irm https://claude.ai/install.ps1 | iex
```

```bat
:: Windows CMD
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

```bash
# macOS / Linux / WSL
curl -fsSL https://claude.ai/install.sh | bash
```

**대안**

```powershell
winget install Anthropic.ClaudeCode          # winget (수동 업데이트)
npm install -g @anthropic-ai/claude-code      # npm, Node 22+ (수동 업데이트)
```

**확인 · 인증 · 시작**

```powershell
claude --version        # 설치 확인
claude doctor           # 설치/설정 점검
cd C:\내프로젝트
claude                  # 실행 → 브라우저 로그인
```

- 인증: 첫 실행 시 브라우저 로그인. **Pro · Max · Team · Enterprise · Console** 계정 필요(무료 플랜은 불가). 바꾸려면 `/login`.
- 윈도우 팁: **Git for Windows**가 있으면 Bash 도구를 쓰고, 없으면 PowerShell 도구로 동작한다. 리눅스 도구체인이나 샌드박스가 필요하면 **WSL 2**에서 리눅스 설치 명령을 쓴다.
- 프로젝트 지침: `/init` → `CLAUDE.md` 생성.
- 기본 모델: **Sonnet 5**(1M 컨텍스트). Opus로 바꾸려면 `/model opus`.

---

## Codex 설치 (OpenAI)

**설치**

```bash
# macOS / Linux (standalone)
curl -fsSL https://chatgpt.com/codex/install.sh | sh
```

```powershell
npm install -g @openai/codex          # npm (윈도우 포함 공통)
```

(Homebrew · winget 경로도 제공된다.)

**인증 · 시작**

```powershell
cd C:\내프로젝트
codex                                 # 실행 → ChatGPT 로그인
```

- 인증: **ChatGPT 로그인**(Plus · Pro · Team) 또는 **`OPENAI_API_KEY`** 환경변수.
  - CMD: `set OPENAI_API_KEY=sk-...`
  - PowerShell: `$env:OPENAI_API_KEY="sk-..."`
  - ChatGPT 로그인은 최신 모델을 바로 쓰고, API 키는 신모델 반영이 늦지만 CI 자동화에 유리하다.
- 프로젝트 지침: `/init` → `AGENTS.md` 생성.
- 기본 모델: **gpt-5.6-sol**. 바꾸려면 `/model`(추론 강도도 함께 선택).

---

## 인증 방식 고르기 (수업 로지스틱스)

학생 수만큼 곱해지므로 **미리 정해두는 게 좋다.**

| | 구독 로그인 (Pro/Max · ChatGPT Plus) | API 키 (Console · OPENAI_API_KEY) |
|---|---|---|
| 준비 | 브라우저 로그인 한 번 | 키 발급 → 환경변수 설정 |
| 비용 | 요금제에 포함 | **호출량만큼 과금** |
| 강의실 적합성 | 간편 — 권장 | 키 배포·비용 관리 필요 |
| CI/자동화 | 제한 | 유리 |

두 도구를 **둘 다 깔 필요는 없다.** 수업에선 보통 하나(주로 **Claude Code**)로 실습하고, 나머지는 개념으로 대비시키는 편이 시간상 낫다.

**첫 확인 과제** — 세팅 검증용으로 "이 폴더 파일 목록 보여줘" 또는 Day07의 버그(`calc.py`)를 그대로 던져 "고쳐서 통과시켜줘"를 시켜보면, 노트북에서 만든 미니 에이전트와 **같은 루프인데 규모만 다르다**는 게 바로 이어진다.

---

## Claude Code 편의기능

- **모드 전환(Shift+Tab)** — 일반 → 자동수락(edits) → **계획(plan)** 모드 순환. 계획 모드는 실행 없이 계획만 세운다.
- **슬래시 명령** — `/init`(CLAUDE.md 생성) · `/clear`(대화 초기화) · `/compact`(대화 요약 압축) · `/model` · `/config` · `/review` · `/rewind` · `/mcp` · `/agents` · `/cost` · `/doctor` · `/vim`.
- **CLAUDE.md** — 프로젝트 지침을 자동 로드. 대화 중 `#`로 즉석 메모 추가.
- **되감기(Esc Esc · /rewind)** — 이전 상태로 복구. 잘못된 편집을 되돌린다.
- **서브에이전트** — `.claude/agents/`에 정의. 별도 컨텍스트로 하위 작업을 병렬 처리(에이전트 팀).
- **스킬(Skills)** — `.claude/skills/<이름>/SKILL.md`. 슬래시(`/이름`)로도, Claude가 자율적으로도 호출.
- **훅(Hooks)** — `settings.json`에 이벤트별 스크립트 등록(PreToolUse 등). 위험 명령 차단·비밀키 스캔 같은 가드레일.
- **플러그인** — 스킬·서브에이전트·명령·훅·MCP를 한 번에 묶어 배포/설치. 확장 공유의 표준.
- **MCP 연결** — `claude mcp add ...` 로 외부 도구를 물린다(Day07에서 만든 MCP 서버도 그대로).
- **확장 사고** — 프롬프트에 "think" · "think hard" · "ultrathink"로 사고 깊이 조절.
- **이미지 입력** — 스크린샷 붙여넣기/드래그로 시각 맥락 전달.
- **`@파일` 멘션 · `!` 인라인 bash** — 파일 참조와 셸 명령을 대화 중에 바로.
- **헤드리스(`claude -p "..."`)** — 스크립트/CI에서 비대화형 실행.
- **세션 재개** — `claude --continue` · `claude --resume`.
- **IDE 통합** — VS Code · JetBrains 확장. 인라인 diff, 편집기 선택 영역을 맥락으로.
- **git/PR** — 커밋·PR 생성, `/pr-comments`로 PR 코멘트 처리.
- **자동 압축** — 컨텍스트가 차면 대화를 자동 요약해 이어감.

## Codex 편의기능

- **`/permissions`** — 허용 범위와 활성 샌드박스를 확인·조정. 무단 편집/실행을 막는다.
- **샌드박스 · 승인 모드** — 기본이 샌드박스 on(`workspace-write`: 저장소 안만 수정). 모드는 `read-only` · `workspace-write` · `danger-full-access`, 승인은 `on-request` · `never`. 플래그 예: `--sandbox workspace-write --ask-for-approval on-request`.
- **AGENTS.md** — 프로젝트 지침 파일(`/init`으로 생성). Claude Code의 CLAUDE.md에 대응.
- **`codex resume`** — 현재 저장소의 최근 대화를 다시 연다(세션 재개).
- **`codex exec`** — 비대화형/헤드리스 실행. 반복 워크플로·파이프라인용.
- **`codex --image`** — 이미지를 프롬프트에 넣어 시각 맥락 전달.
- **`codex --search`** — 라이브 웹 검색 활성화.
- **`codex mcp`** — 외부 도구를 MCP로 연결.
- **`/model`** — 모델과 추론 강도 선택.
- **`/review`** — 커밋 전 변경사항을 검토하고 이슈를 찾는다.
- **서브에이전트** — 집중 작업을 특화 에이전트에 위임.
- **세 가지 표면** — CLI · IDE 확장 · 클라우드 Codex(ChatGPT에서 위임 → diff·PR 수령).
- **설정 파일** — `~/.codex/config.toml` 로 프로필·MCP 서버 관리.

---

## 한눈 대응표

| 개념 | Claude Code | Codex |
|---|---|---|
| 프로젝트 지침 파일 | `CLAUDE.md` | `AGENTS.md` |
| 지침 생성 | `/init` | `/init` |
| 모델 전환 | `/model` (기본 Sonnet 5) | `/model` (기본 gpt-5.6-sol) |
| 변경 리뷰 | `/review` | `/review` |
| 헤드리스 실행 | `claude -p "..."` | `codex exec` |
| 세션 재개 | `claude --continue` / `--resume` | `codex resume` |
| 외부 도구 | MCP (`claude mcp add`) | MCP (`codex mcp`) |
| 이미지 | 붙여넣기/드래그 | `--image` |
| 웹 검색 | 내장 | `--search` |
| 권한/샌드박스 | 모드 전환(Shift+Tab), 권한 모드 | `/permissions`, `--sandbox` |
| 확장 배포 | 플러그인(스킬·훅·서브에이전트) | config.toml + MCP |

핵심은 하나 — **Day07에서 손으로 만든 "판단·도구·루프"가 이 도구들 안에 규모만 키워 들어 있다.** 계획·컨텍스트·권한·서브에이전트가 그 위에 얹혔을 뿐이다.
