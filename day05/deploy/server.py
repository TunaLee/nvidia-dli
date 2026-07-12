"""Day05 미니프로젝트 · 사내 도우미 MCP 서버 (배포용 통합 파일)
FastMCP Cloud(Horizon) 진입점: server.py:mcp
로컬 실행: fastmcp run server.py  (또는 python server.py)
"""
import asyncio
from fastmcp import FastMCP, Context
from pydantic import BaseModel

# ── 사내 문서(데이터) ───────────────────────────────────────────────
DOCS = [
    {"doc_id": "leave",    "title": "연차 및 휴가 규정", "category": "인사", "body": "연차 휴가는 사용 3영업일 전까지 사내포털에서 신청하고 팀장 승인을 받는다."},
    {"doc_id": "expense",  "title": "비용 정산 절차",   "category": "재무", "body": "비용 정산은 영수증을 첨부해 정산 메뉴에서 접수하고 재무팀이 최종 승인한다."},
    {"doc_id": "security", "title": "정보보안 정책",     "category": "보안", "body": "외부 USB는 원칙적으로 금지되며 파일 공유는 사내 승인 드라이브만 사용한다."},
    {"doc_id": "remote",   "title": "재택근무 및 근태",  "category": "인사", "body": "재택근무는 주 2회까지 가능하며 전날 18시까지 팀 채널에 공유한다."},
    {"doc_id": "err4021",  "title": "오류 코드 안내",     "category": "IT",   "body": "에러코드 ERR-4021은 인증 토큰 만료를 의미하며 재로그인으로 해결한다."},
    {"doc_id": "x100",     "title": "제품 X-100 매뉴얼",  "category": "제품", "body": "제품 X-100의 펌웨어 최신 버전은 3.0이며 전용 앱의 설정 메뉴에서 업데이트한다."},
]
NOTES = []
LEVELS = {"참고", "중요", "긴급"}

mcp = FastMCP("HelperServer")

# ── 검색 = Tool (간단 키워드 RAG) ───────────────────────────────────
@mcp.tool(annotations={"readOnlyHint": True})
def search_docs(query: str, k: int = 2) -> list:
    """사내 문서에서 질문과 관련된 문서를 찾는다 (단어 겹침 · 실무는 임베딩/하이브리드)"""
    scored = sorted(DOCS, key=lambda d: -sum(w in d["body"] for w in query.split()))
    return [{"doc_id": d["doc_id"], "title": d["title"], "body": d["body"]} for d in scored[:k]]

# ── 메모 저장 = Tool (부작용) ───────────────────────────────────────
@mcp.tool
def add_note(text: str) -> dict:
    """메모를 저장한다 (부작용)"""
    NOTES.append(text)
    return {"저장됨": text, "총개수": len(NOTES)}

# ── 플래그 = Tool (입력 검증·친절한 에러) ───────────────────────────
@mcp.tool
def flag_doc(doc_id: str, level: str) -> str:
    """문서에 중요도 플래그를 단다. 허용값이 아니면 친절한 에러."""
    if level not in LEVELS:
        raise ValueError(f"level은 {sorted(LEVELS)} 중 하나여야 합니다. 받은 값: '{level}'")
    if not any(d["doc_id"] == doc_id for d in DOCS):
        raise ValueError(f"'{doc_id}' 문서가 없습니다.")
    return f"{doc_id} → {level}"

# ── 상태 = Tool (구조화 출력) ───────────────────────────────────────
class ServerStats(BaseModel):
    docs: int
    notes: int
    categories: int

@mcp.tool(annotations={"readOnlyHint": True})
def stats() -> ServerStats:
    """서버 상태를 구조화해 반환 (읽기 전용)"""
    return ServerStats(docs=len(DOCS), notes=len(NOTES), categories=len({d["category"] for d in DOCS}))

# ── 재색인 = Tool (Context·진행 보고) ───────────────────────────────
@mcp.tool
async def reindex(ctx: Context) -> dict:
    """문서를 다시 색인하며 진행률을 보고한다 (오래 걸리는 작업 예시)"""
    for i, d in enumerate(DOCS):
        await ctx.report_progress(i + 1, len(DOCS))
        await asyncio.sleep(0)
    await ctx.info("색인 완료")
    return {"reindexed": len(DOCS)}


if __name__ == "__main__":
    mcp.run()   # 로컬 stdio. 원격 HTTP는: mcp.run(transport="http", host="0.0.0.0", port=8000)
