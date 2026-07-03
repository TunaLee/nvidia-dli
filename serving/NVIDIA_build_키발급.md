# NVIDIA build API 키 발급 가이드 (수강생용)

강사 DGX 엔드포인트 대신(또는 백업으로) **NVIDIA build 무료 API**를 쓰려면
각자 무료 키(`nvapi-...`)를 발급받으면 됩니다. 카드 불필요, 가입 시 **1,000 크레딧**.

> 우리 노트북은 OpenAI 호환이라 **base_url·모델·키 3가지만** 바꾸면 그대로 동작합니다.

---

## 1. 로그인
1. <https://build.nvidia.com> 접속
2. 우측 상단 **Login** → NVIDIA 계정으로 로그인 (없으면 무료 회원가입)

## 2. 모델 선택
1. 상단에서 채팅 모델 검색 (예: `qwen`, `llama`, `deepseek`)
2. 모델 페이지 우측 코드 스니펫에 **정확한 `model` id + base_url + 키 사용 예시**가 그대로 나옵니다 → 그 `model` 문자열을 노트북 `LLM_MODEL`에 씁니다.

## 3. API 키 생성 (여기서 많이 막힘 ⚠️)
모델 페이지의 **Get API Key**(또는 *Build with this NIM*)를 누르면 아래 **전화번호 인증** 창이 뜹니다:

![NVIDIA build 전화번호 인증 화면](img/nvidia-phone-verify.png)

> *스크린샷 내용 (이미지 없이도 참고):*
> - 제목: **"We'll need to verify your phone number"**
> - "OTP(문자 인증)로 계정을 인증해야 API 키를 생성할 수 있습니다."
> - 인증 시 혜택: **일일 한도 없는 무제한 요청 / GPU 클라우드 샌드박스 / 부정사용 방지**
> - **Location(국가)** 선택 + **Phone Number** 입력 → **Send Code to Phone** 으로 문자 코드 받기
> - 우측 하단에 **Skip** 버튼도 있음
> - "국가가 목록에 없으면 곧 확장 예정" 안내 (한국이 안 보이면 잠시 후 재시도)

**어떻게 할까?**
- **문자 인증(권장)**: 국가·휴대폰 입력 → *Send Code to Phone* → 받은 OTP 입력 → 무제한 요청 언락
- **Skip**: 인증이 번거로우면 건너뛰기. 기본 무료 크레딧(1,000)만으로도 **이 실습(짧은 호출 15~30회)엔 충분**합니다. 단, 계정/시점에 따라 키 생성 자체에 인증을 요구할 수 있어요 — 그럴 땐 문자 인증으로 진행하세요.
- 국가 목록에 한국이 없다면: 잠시 후 재시도하거나, 그동안 **강사 DGX 엔드포인트를 사용**하면 됩니다.

발급되면 **`nvapi-...` 키를 복사**해 둡니다. (키는 다시 안 보여줄 수 있으니 안전한 곳에 저장)

## 4. 노트북에 넣기
Day01/02 노트북 최상단 설정 셀에서:
```python
import os
os.environ["QWEN_BASE_URL"] = "https://integrate.api.nvidia.com/v1"
os.environ["QWEN_API_KEY"]  = "nvapi-...복사한 키..."
# LLM_MODEL 은 2단계에서 고른 모델 페이지의 model id 로 교체
```
그 아래 셀들은 **그대로** 실행하면 됩니다.

---

## 참고
| 항목 | 값 |
|---|---|
| 엔드포인트 | `https://integrate.api.nvidia.com/v1` (OpenAI 호환) |
| 무료 크레딧 | 가입 시 1,000 (카드 불필요, 만료 없음) |
| Rate limit | 키당 ~40 RPM |
| 키 접두사 | `nvapi-` |

- **강사 DGX와 전환은 `QWEN_BASE_URL`·키·모델 3줄**이면 끝. NVIDIA가 막히면 DGX로, DGX가 막히면 NVIDIA로 즉시 폴백.
- 데이터: NVIDIA 사용 시 질문·검색조각이 NVIDIA로 전송됩니다(데모 코퍼스면 무관, 민감 문서면 DGX 권장).

---
> 📷 **강사 메모**: 위 스크린샷을 `serving/img/nvidia-phone-verify.png` 로 저장하면 이미지가 표시됩니다.
