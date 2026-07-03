"""수강생 키 발급: keys.txt (프록시용) + roster.csv (배포용) 생성.

  python gen_keys.py 30            # 30명치 생성
  python gen_keys.py 30 --prefix dli
"""
import sys, secrets, csv, argparse

ap = argparse.ArgumentParser()
ap.add_argument("n", type=int, help="수강생 수")
ap.add_argument("--prefix", default="dli")
ap.add_argument("--keys", default="keys.txt")
ap.add_argument("--roster", default="roster.csv")
a = ap.parse_args()

rows = [(f"student{i:02d}", f"{a.prefix}-{secrets.token_hex(12)}") for i in range(1, a.n + 1)]

with open(a.keys, "w", encoding="utf-8") as f:
    f.write("# key,name  — 프록시가 읽는 파일 (외부 유출 금지)\n")
    for name, key in rows:
        f.write(f"{key},{name}\n")

with open(a.roster, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f); w.writerow(["name", "DLI_API_KEY"])
    w.writerows([(n, k) for n, k in rows])

print(f"✅ {a.n}명 키 생성 → {a.keys} (프록시용), {a.roster} (수강생 배포용)")
