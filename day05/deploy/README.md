# Day05 사내 도우미 MCP — 배포 & 실행

## 파일 (repo에 필요한 건 사실상 2개)
- `server.py` — 통합 서버 (도구 5개: search_docs·add_note·flag_doc·stats·reindex). **Horizon 진입점 = `server.py:mcp`**
- `requirements.txt` — 의존성 (`fastmcp` 한 줄)
- `client_demo.py` — (배포 후) 노트북/로컬에서 **LLM이 원격 RAG를 실행**하는 클라이언트

## 1) GitHub에 올리기
```bash
git init && git add server.py requirements.txt && git commit -m "helper mcp server"
git remote add origin https://github.com/<나>/<repo>.git && git push -u origin main
```

## 2) Horizon(FastMCP Cloud)에 배포 — 개인 무료
1. **horizon.prefect.io** 접속 → GitHub 로그인
2. 저장소 선택 → **진입점 `server.py:mcp`** 지정 (requirements 자동 감지)
3. **Deploy** → 약 60초 뒤 공개 URL: **`https://<이름>.fastmcp.app/mcp`**

## 3) 우리가 호출해서 LLM이 RAG 실행 (노트북/로컬)
`client_demo.py`에서:
```python
MCP_URL       = "https://<이름>.fastmcp.app/mcp"   # 배포 URL
NVIDIA_API_KEY = "nvapi-..."                       # 클라이언트 LLM(Qwen)
```
실행하면:
```
[LLM → 원격 도구] search_docs({'query': '연차 신청 며칠 전', 'k': 2})
A: 근거에 따르면 연차는 3영업일 전에 신청해야 합니다.
```
→ Qwen이 **배포된 서버의 search_docs를 스스로 호출** → 원격에서 RAG → 그 근거로 답변.
(노트북에선 `if __name__` 대신 `await main()`)

## 서버 상태 확인 (inspect)
- **로컬 파일**: `fastmcp inspect server.py` (리포트) · `fastmcp dev inspector server.py` (웹, Node 필요)
- **배포 URL**: `fastmcp inspect`는 파일 전용이라 URL ❌ → **Inspector 웹 UI에서 URL Connect** 또는 `fastmcp call <URL> search_docs query=연차`

## 주의
- 공개 URL은 **인증 없으면 아무나 접근** → 민감하면 auth 추가.
- `search_docs`는 가벼운 키워드 검색. 실무 RAG(임베딩/하이브리드)로 바꾸면 `requirements.txt`에 `sentence-transformers` 등 추가.
