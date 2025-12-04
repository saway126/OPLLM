# 폐쇄망(Air-gapped) Local LLM 시스템 구축 가이드

이 가이드는 인터넷이 차단된 환경에서 Local LLM 시스템을 구축, 운영, 테스트하는 방법을 설명합니다.

## 1. 사전 준비 (외부망에서 수행)
폐쇄망에 들어가기 전에 외부 인터넷이 되는 PC에서 다음 파일들을 다운로드하여 USB/디스크에 담아야 합니다.

1.  **Ollama Binary**: [https://ollama.com/download/linux](https://ollama.com/download/linux) (`ollama-linux-amd64`)
2.  **LLM Model**: HuggingFace 등에서 `.gguf` 파일 다운로드 (예: `llama-3-8b.gguf`)
3.  **Embedding Model**: `.gguf` 파일 (예: `nomic-embed-text.gguf`)
4.  **System Packages**: `python3-venv`, `ffmpeg` 등의 `.deb` 파일들.
5.  **Python Packages**: `requirements.txt`에 있는 패키지들을 `pip download` 명령어로 다운로드.
    ```bash
    pip download -d ./offline_pip -r requirements.txt
    ```

## 2. 설치 절차 (폐쇄망 서버에서 수행)

### 2.1 파일 전송
USB에 담아온 파일들을 서버의 적절한 위치(예: `c:\OPLLM` 또는 `/opt/llm-server`)로 복사합니다.

### 2.2 의존성 설치
```bash
cd c:\OPLLM
chmod +x setup/*.sh
./setup/install_dependencies.sh
```
이 스크립트는 시스템 패키지와 Python 가상환경(venv)을 설정합니다.

### 2.3 Ollama 설치 및 서비스 시작
```bash
./setup/install_ollama_offline.sh
```
Ollama가 설치되고 systemd 서비스로 등록되어 자동 실행됩니다.

### 2.4 모델 로드
가져온 모델 파일(.gguf)을 Ollama에 등록합니다.
```bash
# 사용법: ./scripts/import_model.sh <모델명> <파일경로>
./scripts/import_model.sh llama3 /path/to/usb/llama-3-8b.gguf
./scripts/import_model.sh nomic-embed-text /path/to/usb/nomic-embed-text.gguf
```

### 2.5 API 서버 시작
```bash
# 서비스로 실행 (백그라운드)
sudo cp services/llm-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable llm-server
sudo systemctl start llm-server

# 또는 직접 실행 (테스트용)
source venv/bin/activate
python src/main.py
```

## 3. RAG 데이터 구축
사내 문서(PDF, TXT)를 `data/documents` 폴더에 넣고 임베딩을 생성합니다.
```bash
# 문서 폴더에 파일 복사
cp /path/to/docs/*.pdf data/documents/

# 임베딩 생성 실행
source venv/bin/activate
python src/rag/ingest.py
```

## 4. 테스트 및 검증

### 4.1 자동 점검 스크립트
```bash
chmod +x tests/health_check.sh
./tests/health_check.sh
```
이 스크립트는 다음을 확인합니다:
1. Ollama 서비스 실행 여부
2. API 서버 응답 (Health Check)
3. 실제 LLM 채팅 응답 테스트

### 4.2 수동 API 테스트 (curl)
```bash
# 채팅 테스트
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me-to-a-secure-random-key" \
  -d '{"model": "llama3", "messages": [{"role": "user", "content": "안녕?"}]}'

# RAG 검색 테스트
curl -X POST http://localhost:8000/api/rag/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: change-me-to-a-secure-random-key" \
  -d '{"query": "우리 회사 보안 규정 알려줘"}'
```

## 5. 운영 및 보안
- **로그 확인**: `tail -f logs/server.log`
- **API 키 변경**: `config/settings.yaml` 파일에서 `api_key`를 변경하고 서버를 재시작하세요.
- **모델 업데이트**: 새로운 모델 파일을 가져와서 `2.4 모델 로드` 과정을 반복하면 됩니다.

## 6. Docker 기반 오프라인 시뮬레이션
폐쇄망 환경을 USB 없이 재현하고 싶다면 Docker로 Ollama + API 서버를 동시에 구동할 수 있습니다.

1. **사전 준비**
   - `offline_pip` 폴더에 필요한 모든 wheel(특히 `langchain==0.2.16`, `langchain-community==0.2.16`)을 넣어둡니다.
   - 호스트의 모델 캐시(`C:\Users\<계정>\.ollama` 또는 `~/.ollama`)가 최신 상태인지 확인합니다.
2. **전용 네트워크 생성**
   ```powershell
   docker network create airgap --internal
   ```
3. **Compose 실행**
   ```powershell
   docker compose -f docker-compose.offline.yml up --build
   ```
   - `ollama` 서비스는 호스트의 모델 캐시를 `/root/.ollama`로 마운트합니다.
   - `api` 서비스는 Dockerfile을 이용해 오프라인 패키지로 이미지를 빌드합니다.
4. **테스트**
   - `curl http://localhost:8000/health`
   - `Invoke-RestMethod -Uri "http://localhost:8000/api/chat" ...`

`docker-compose.offline.yml`에 정의된 `airgap` 네트워크는 외부 인터넷으로 라우팅되지 않기 때문에, 완전히 분리된 환경에서 통신 흐름을 검증할 수 있습니다. 필요 시 `USE_OFFLINE_PIP=false`로 빌드하면 온라인 설치도 지원합니다.