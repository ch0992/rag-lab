# RAG Lab - Simple FastAPI Implementation

이 프로젝트는 Ollama와 ChromaDB를 사용하는 한국어 특화 RAG(Retrieval-Augmented Generation) 시스템의 기본 구현입니다. FastAPI를 통해 RESTful API를 제공하며, 문서 기반 질의응답 서비스를 구현합니다.

## 프로젝트 구조

```
rag-fastapi-simple/
├── app/
│   ├── document/        # 문서 파일 저장소 (.txt)
│   ├── app.py          # FastAPI 서버 및 API 엔드포인트
│   ├── embeddings.py   # 임베딩 모델 설정
│   ├── parse_response.py # 응답 파싱 유틸리티
│   ├── query_runner.py  # 쿼리 처리 및 Ollama 연동
│   └── vector_store.py  # ChromaDB 벡터 저장소 관리
└── README.md
```

## 주요 파일 설명

### 1. `app.py`
- FastAPI 서버 구현
- API 엔드포인트 정의:
  - `/upload`: 문서 업로드 및 벡터 DB 저장
  - `/query`: RAG 기반 질의응답
  - `/collections`: 저장된 콜렉션 목록 조회
  - `/collections/{collection_name}`: 특정 콜렉션 조회/삭제
- 서버 시작 시 `document/` 폴더의 텍스트 파일 자동 로드

### 2. `embeddings.py`
- 다국어 지원 sentence-transformer 모델 설정
- 모델: `paraphrase-multilingual-MiniLM-L12-v2`

### 3. `query_runner.py`
- Ollama API 연동 및 쿼리 처리
- 한글 전용 응답 생성 로직
- 문서 기반 엄격한 답변 생성

### 4. `vector_store.py`
- ChromaDB 벡터 저장소 관리
- 문서 청크 저장 및 검색 기능

## 사전 요구사항

### 필수 설치 항목
- Python 3.9 이상
- Docker Desktop with Kubernetes 활성화
  - Docker Desktop > Settings > Kubernetes > Enable Kubernetes
- kubectl CLI 도구
- Homebrew (Mac OS)


## 실행 방법

### 1. ChromaDB 설치

ChromaDB는 프로젝트의 `infra-setup/vectordb` 디렉토리의 설치 가이드를 참고하여 설치해주세요.

### 2. Ollama 설치 및 실행 (필수 선행 작업)
```bash
# Ollama 설치 (Mac)
brew install ollama

# Ollama 서버 실행 (별도의 터미널에서 실행)
ollama serve

# 다른 터미널에서 모델 다운로드
ollama pull deepseek-r1:8b

# 모델 테스트 (선택사항)
ollama run deepseek-r1:8b
```

### 2. 가상환경 설정 및 서버 실행
```bash
# 프로젝트 디렉토리로 이동
cd rag-fastapi-simple

# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
# 또는
# .\venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt

# FastAPI 서버 실행
cd app
uvicorn app:app --reload
```

### 4. API 사용
```bash
# 문서 업로드
curl -X POST http://localhost:8000/upload \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/document.txt"

# 질의응답
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"collection_name":"document","query":"질문내용"}'

# 콜렉션 목록 조회
curl http://localhost:8000/collections
```

## 특징
- 한국어 특화 RAG 시스템
- 실시간 문서 기반 질의응답
- 자동 문서 로드 및 벡터화
- 엄격한 문서 기반 답변 생성
- 순수 한글 응답 지원

