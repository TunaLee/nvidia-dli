"""30명 램프 부하테스트 — 실제 수강생 부하(짧은 RAG 질문)를 흉내 냅니다.

  python loadtest.py --url http://localhost:8080/v1 --key <수강생키>
  python loadtest.py --url https://xxx.trycloudflare.com/v1 --key <키> --levels 1,10,30

각 동시성 레벨에서 요청을 동시에 쏘고 p50/p95 지연 + aggregate tok/s + 실패율을 보고합니다.
"""
import argparse, asyncio, time, statistics
import httpx

PROMPTS = [
    "연차 휴가는 며칠 전에 신청하나요? 한 문장으로만.",
    "비용 정산은 누가 최종 승인하나요?",
    "재택근무는 언제까지 알려야 하나요?",
    "ERR-4021 은 무슨 뜻인가요?",
    "X-200 펌웨어는 어떻게 올리나요?",
]

async def one(client, url, key, i):
    body = {"model": "Qwen/Qwen3.5-35B-A3B",
            "messages": [{"role": "user", "content": PROMPTS[i % len(PROMPTS)]}],
            "max_tokens": 256, "temperature": 0.2}
    t0 = time.monotonic()
    try:
        r = await client.post(f"{url}/chat/completions", json=body,
                              headers={"Authorization": f"Bearer {key}"})
        dt = time.monotonic() - t0
        if r.status_code != 200:
            return dt, 0, False
        toks = (r.json().get("usage") or {}).get("completion_tokens", 0)
        return dt, toks, True
    except Exception:
        return time.monotonic() - t0, 0, False

async def level(url, key, n):
    async with httpx.AsyncClient(timeout=httpx.Timeout(180.0, connect=10.0)) as c:
        wall0 = time.monotonic()
        res = await asyncio.gather(*(one(c, url, key, i) for i in range(n)))
        wall = time.monotonic() - wall0
    lat = [d for d, _, ok in res if ok]
    toks = sum(t for _, t, ok in res if ok)
    fails = sum(1 for *_, ok in res if not ok)
    p = lambda q: round(statistics.quantiles(lat, n=100)[q-1], 2) if len(lat) >= 2 else (round(lat[0],2) if lat else None)
    print(f"  동시 {n:>2} | 성공 {n-fails:>2}/{n} | "
          f"p50 {p(50)}s p95 {p(95)}s | wall {round(wall,2)}s | "
          f"aggregate {round(toks/wall,1) if wall else 0} tok/s")

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="예: http://localhost:8080/v1")
    ap.add_argument("--key", required=True)
    ap.add_argument("--levels", default="1,5,10,20,30")
    a = ap.parse_args()
    print(f"target={a.url}")
    for n in (int(x) for x in a.levels.split(",")):
        await level(a.url.rstrip("/"), a.key, n)

if __name__ == "__main__":
    asyncio.run(main())
