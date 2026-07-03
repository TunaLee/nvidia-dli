# DGX Spark — 수강생 30명용 Qwen API 배포 런북

대면강의에서 수강생이 각자 노트북으로 **공개 HTTPS + 개인 키**로 접근하는 구성.

```
수강생 노트북 (pip: dli-llm, 개인 키)
      │ HTTPS
      ▼
공개 URL  (Cloudflare 터널 또는 Tailscale Funnel)
      ▼
인증·정책 프록시  proxy.py  (DGX localhost:8080)
   · 수강생별 키 검증 (실제 SGLang 키 비노출)
   · thinking OFF 강제 · max_tokens 상한 · rate-limit · 동시성 상한
      ▼
SGLang  (DGX localhost:30000, Qwen/Qwen3.5-35B-A3B)
```

## 왜 이 구조인가 (실측 근거)
- SGLang이 `127.0.0.1:30000`에만 바인딩 → 수강생이 직접 못 닿음. 프록시를 앞에 두고 그것만 공개.
- **thinking(추론) 강제 OFF가 핵심**: 실측상 추론 ON이면 짧은 질문도 답이 안 나오고 토큰을 다 소모(64토큰→답 없음). OFF면 같은 질문이 **27토큰**에 직답 → 30명 동시부하 대폭 감소.
- 실습은 임베딩·벡터DB·리랭커를 **수강생 로컬(CPU)** 에서 처리하고 **생성만** 서버로 → 서버 부하가 가장 가벼운 형태.

## 배포 절차 (DGX에서)
```bash
cd serving
pip install -r requirements.txt

# 1) 수강생 키 발급
python gen_keys.py 30           # keys.txt(프록시용) + roster.csv(배포용)

# 2) 프록시 기동 (SGLang api-key 는 실행 프로세스에서 자동 주입)
./run_proxy.sh                  # 127.0.0.1:8080

# 3) 공개 (둘 중 하나)
./expose_cloudflare.sh 8080     # https://xxx.trycloudflare.com  (설치 필요, 계정 불필요)
#   또는
./expose_tailscale.sh 8080      # https://<host>.<tailnet>.ts.net (funnel 허용 필요)

# 4) 사전 부하테스트 (수업 전 필수)
python loadtest.py --url http://localhost:8080/v1 --key <roster의 키 하나> --levels 1,10,30
```

## 수강생 배포물
- `roster.csv` 의 각 `DLI_API_KEY` 를 학생별로 전달
- 공개 `base_url` (예: `http://124.51.229.210:30001/v1`)
- `pip install dli-llm` (또는 사내 배포 wheel/git)

## 대안: NVIDIA build 무료 API
학생이 각자 무료 키를 발급받아 쓰는 경로. 발급 방법은 [NVIDIA_build_키발급.md](NVIDIA_build_키발급.md) 참고.
DGX와 전환은 `QWEN_BASE_URL`·키·모델 3줄이면 끝 → 서로 백업으로 쓸 수 있음.

## 권장 튜닝 (선택, 처리량↑)
현재 SGLang은 `--dtype bfloat16`. GB10(≈270GB/s 대역폭)에선 **FP8**이 처리량 ~2배·메모리 ~35GB 절감.
또한 수업 중에는 Ollama(11434)·agent_server(8002)를 내려 DGX를 SGLang 전용으로.

```bash
python -m sglang.launch_server --model-path Qwen/Qwen3.5-35B-A3B \
  --host 127.0.0.1 --port 30000 --api-key <KEY> \
  --dtype fp8 --context-length 8192 --max-running-requests 48 \
  --mem-fraction-static 0.9 --reasoning-parser qwen3 --enable-metrics
```
> thinking은 프록시가 요청마다 `enable_thinking=false`로 끄므로 서버 파서는 그대로 둬도 됩니다.

## 보안 메모
- 실제 SGLang 키는 프록시만 알고, 수강생에겐 개인 키만 노출.
- 공개 터널은 인증 프록시 뒤에서만 열 것(raw SGLang을 직접 공개 금지).
- `keys.txt`/`roster.csv` 는 커밋 금지 (.gitignore 처리됨).
