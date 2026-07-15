# 하네스 생태계 — Superpowers와 gstack 파헤치기

Claude Code 위에 얹는 대표 하네스 둘. **성격이 정반대**라, 무엇을 강제하느냐부터 다르다.

| | Superpowers | gstack |
|---|---|---|
| 정체 | 방법론을 코드로 강제하는 **프로세스 규율** | 역할 페르소나로 구성한 **가상 개발 팀** |
| 스킬 수 | 14개 (적다) | 40여 개 (많다) |
| 방식 | 강제 흐름 — 단계 건너뛰기 차단 | 골라 쓰기 — 명시적 호출 |
| 자동 발동 | 있음 (상황에 맞는 스킬을 스스로 발동) | 없음 (`/명령`으로 직접 호출) |
| 호환 | Claude Code · Codex · Cursor · Copilot · Gemini | 주로 Claude Code (Codex 포트 있음) |
| 한마디 | **어떻게 일하는가**를 강제한다 | **무엇을 해주는가**를 골라 쓴다 |

설치
```
# Superpowers
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# gstack
git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
# Codex: npx gstack-codex init
```

---

## Superpowers — 방법론을 강제하는 14개 스킬

핵심 발상은 **"좋은 습관을 잊지 않게 코드로 강제한다"**. 테스트를 건너뛰거나 계획 없이 구현하는 걸 막는다. 스킬이 상황에 맞게 스스로 발동한다.

### 설계 단계
- **brainstorming** — 기능·컴포넌트·동작 변경 등 **창작 작업 전 필수**. 구현 전에 의도·요구·설계를 대화로 탐색한다. (이 강의 설계에도 이 스킬을 썼다.)

### 계획 단계
- **writing-plans** — 스펙이나 요구사항을 **단계별 구현 계획**으로 만든다. 코드를 만지기 전에.

### 구현 단계
- **test-driven-development** — 구현 코드를 쓰기 전 **실패하는 테스트를 먼저**. RED → GREEN. 우회 불가.
- **subagent-driven-development** — 독립 작업이 있는 계획을 **현재 세션에서 서브에이전트로** 실행.
- **dispatching-parallel-agents** — 공유 상태·순서 의존이 없는 **2개 이상 작업을 병렬로** 디스패치.
- **executing-plans** — 작성된 계획을 **별도 세션에서** 리뷰 체크포인트와 함께 실행.
- **using-git-worktrees** — 작업 공간을 격리한다. 병렬 구현의 충돌 방지.

### 검증 단계
- **systematic-debugging** — 버그·테스트 실패·이상 동작을 만나면, **수정을 제안하기 전에** 근본 원인부터 조사.
- **requesting-code-review** — 작업 완료·주요 기능·병합 전에 요구 충족을 검증.
- **receiving-code-review** — 리뷰 피드백을 받을 때. 무비판 수용이 아니라 기술적 검증.
- **verification-before-completion** — "완료됐다·고쳤다·통과한다"고 주장하기 전에 **실제로 검증 명령을 돌려 증거를 확인**. 주장보다 증거.

### 마무리·확장
- **finishing-a-development-branch** — 구현이 끝나고 테스트가 통과하면 병합·PR·정리 중 무엇을 할지 안내.
- **writing-skills** — 새 스킬을 만들거나 고치거나 검증할 때. 스킬을 만드는 스킬.
- **using-superpowers** — 대화 시작 시 스킬을 어떻게 찾고 쓰는지 확립.

### 언제 쓰나
- 어제보다 **품질이 떨어질 때** — 테스트 강제로 되돌린다.
- **큰 작업을 규율 있게** 몰고 갈 때 — brainstorm → plan → 실패테스트 → 구현 → 리뷰.
- 팀에 **일관된 개발 방식**을 강제하고 싶을 때.

---

## gstack — 가상 개발 팀의 40여 개 스킬

핵심 발상은 **"스타트업 개발 팀의 역할을 페르소나로 제공한다"**. CEO·디자이너·EM·QA·CSO가 각자 관점으로 검토·실행한다. 자동 발동이 아니라 `/명령`으로 골라 부른다.

### 계획·리뷰 (역할 관점)
- **/office-hours** — YC 오피스아워 모드. 강제 질문으로 요구사항을 끌어내 설계 문서를 만든다.
- **/spec** — 모호한 의도를 5단계로 정밀한 실행 가능 스펙으로.
- **/autoplan** — CEO·디자인·엔지니어링·DX 리뷰를 순차 자동 실행.
- **/plan-ceo-review** — CEO/창업자 모드로 제품 스코프 결정.
- **/plan-eng-review** — EM 모드로 아키텍처·엣지 케이스·테스트 계획 검토.
- **/plan-design-review** — 디자이너 관점으로 인터페이스·AI 슬롭 점검.
- **/plan-devex-review** — 개발자 경험 관점 리뷰.

### 구현·QA
- **/qa** — 웹앱을 체계적으로 QA 테스트하고 발견한 버그를 고친다. (Playwright 브라우저 구동)
- **/qa-only** — 보고만 하는 QA (수정 안 함).
- **/browse** — QA·도그푸딩용 빠른 헤드리스 브라우저.
- **/review** — 랜딩 전 PR 리뷰 (Staff 엔지니어 관점 버그 사냥).
- **/investigate** — 근본 원인 조사형 체계적 디버깅.
- **/health** — 코드 품질 대시보드.

### 보안
- **/cso** — CSO(보안 책임자) 모드 보안 점검.
- **/careful** — 파괴적 명령에 대한 안전 가드레일.
- **/guard** — 풀 안전 모드: 위험 명령 경고 + 디렉토리 범위 편집 제한.
- **/freeze** · **/unfreeze** — 세션 편집을 특정 디렉토리로 제한/해제.

### 배포
- **/ship** — 베이스 브랜치 병합 → 테스트 → diff 리뷰 → 버전·체인지로그 → 커밋·푸시·PR.
- **/land-and-deploy** — 랜딩 후 배포 워크플로.
- **/canary** — 배포 후 카나리 모니터링.
- **/setup-deploy** — 배포 설정.

### 디자인
- **/design-consultation** — 제품을 이해하고 완전한 디자인 시스템(미학·타이포·색·레이아웃·모션)을 제안.
- **/design-html** — 프로덕션 품질 HTML/CSS 생성.
- **/design-review** — 디자이너의 눈으로 시각 불일치·간격·위계·AI 슬롭·느린 인터랙션을 찾아 고침.
- **/design-shotgun** — AI 디자인 변형 여러 개를 생성해 비교 보드에서 선택·반복.

### 문서
- **/document-generate** — 기능·모듈·전체 프로젝트의 문서를 처음부터 생성.
- **/document-release** — 출시 후 문서 갱신.
- **/make-pdf** — 마크다운을 출판 품질 PDF로.

### 데이터·브라우저·기타
- **/scrape** — 웹 페이지에서 데이터 추출.
- **/skillify** — 성공한 스크래핑 흐름을 재사용 가능한 브라우저 스킬로 코드화.
- **/connect-chrome** — AI가 제어하는 Chromium(사이드바 확장 내장) 실행.
- **/retro** — 주간 엔지니어링 회고.
- **/context-save** · **/context-restore** — 작업 컨텍스트 저장·복원.
- **/learn** — 프로젝트 학습 관리.
- **iOS 전용** — `/ios-qa` · `/ios-fix` · `/ios-design-review` 등 실기기 iOS 워크플로.
- **/codex** — OpenAI Codex CLI 래퍼.

### 언제 쓰나
- **제품 관점 검토**가 필요할 때 — 요청하지 않은 기능을 자꾸 붙일 때 `/plan-ceo-review`.
- **실제 배포**까지 갈 때 — `/ship` · `/land-and-deploy` · `/canary`.
- **디자인·QA를 팀처럼** 골라 쓸 때.

---

## 어느 걸, 언제

| 증상 | 처방 |
|---|---|
| 구현이 자꾸 깨진다 · 테스트를 건너뛴다 | **Superpowers** — 테스트를 강제 |
| 요청 안 한 기능을 자꾸 덧붙인다 | **gstack** `/plan-ceo-review` — 제품 리뷰 먼저 |
| 실제로 배포까지 가야 한다 | **gstack** `/ship` |
| 디자인 품질·AI 슬롭이 문제 | **gstack** `/design-review` |
| 큰 작업을 규율 있게 병렬로 | **Superpowers** — brainstorm → plan → 병렬 구현 |

**둘 다 쓸 수 있다.** Superpowers로 개발 규율을 잡고, gstack의 역할 스킬로 제품·디자인·배포를 검토하는 식으로 보완한다.

> 규모 기준: 소(한 시간)=직접 · 중(반나절)=gstack · 대(며칠)=gstack + Superpowers.
