# dli-llm · 수강생용 LLM 클라이언트

NVIDIA DLI 강의 실습에서 쓰는 Qwen 엔드포인트에 **키 하나로** 접속합니다.

## 설치
```bash
pip install dli-llm          # 또는 강사 배포 wheel: pip install ./dli_llm-0.1.0-py3-none-any.whl
```

## 사용
```python
import os
os.environ["DLI_API_KEY"] = "강사에게-받은-키"     # roster 의 DLI_API_KEY

from dli_llm import chat, healthcheck
healthcheck()                                    # 연결/키 확인
print(chat("연차 휴가는 며칠 전에 신청하나요?"))
```

## 기존 실습 노트북(OpenAI 방식)과 함께 쓰기
Day01/02 노트북의 `llm = OpenAI(...)` 대신:
```python
from dli_llm import get_client, MODEL
llm = get_client()
llm.chat.completions.create(model=MODEL, messages=[...])
```

## 환경변수
| 변수 | 설명 |
|---|---|
| `DLI_API_KEY` | (필수) 개인 키 |
| `DLI_BASE_URL` | 엔드포인트. 미설정 시 패키지 기본 공개 URL 사용 |

> 임베딩·벡터DB·리랭커는 여러분 노트북(CPU)에서 로컬로 돌아갑니다. 이 패키지는 **생성(LLM)** 호출만 담당합니다.
