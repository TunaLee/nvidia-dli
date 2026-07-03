"""실습_시작하기.ipynb 안의 <img src="img/NAME.png"> 를 base64 data URI 로 치환.
스크린샷 5장을 img/ 에 저장한 뒤 실행하면 노트북이 자체 완결(이미지 내장)됩니다.

  python embed_screenshots.py
  python embed_screenshots.py 실습_시작하기.ipynb img
"""
import base64, json, re, sys
from pathlib import Path

nb_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("실습_시작하기.ipynb")
img_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("img")

nb = json.loads(nb_path.read_text(encoding="utf-8"))
done, missing = 0, []

def replace(m):
    global done
    name = m.group(1)
    p = img_dir / name
    if not p.exists():
        missing.append(name)
        return m.group(0)
    b64 = base64.b64encode(p.read_bytes()).decode()
    done += 1
    return f'src="data:image/png;base64,{b64}"'

for cell in nb["cells"]:
    if cell["cell_type"] != "markdown":
        continue
    src = "".join(cell["source"])
    src = re.sub(r'src="img/([^"]+)"', replace, src)
    cell["source"] = src.splitlines(keepends=True)

nb_path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"✅ {done}개 이미지 내장 완료 → {nb_path}")
if missing:
    print("⚠️ img/ 에 없는 파일(아직 저장 안 됨):", sorted(set(missing)))
