# RAG API Project

이 프로젝트는 문서 기반 질의응답을 제공하는 FastAPI 기반의 RAG(Retrieval-Augmented Generation) API입니다.

## 기능

- 문서 기반 질의응답
- ChromaDB를 이용한 벡터 저장소
- 임베딩 기반 문서 검색
- Ollama를 이용한 응답 생성
- 다중 문서 컬렉션 지원

## 설치 및 실행

1. Python 가상환경 생성 및 활성화:
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
# 또는
venv\Scripts\activate  # Windows
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

3. Ollama 설치 및 실행:
```bash
# Ollama 설치 (Mac)
brew install ollama

# Ollama 실행
ollama run deepseek-coder
```

4. 환경 설정:
기본 환경 변수가 설정되어 있으며, 필요시 다음 값들을 변경할 수 있습니다:

```python
# config.py 기본값
OLLAMA_BASE_URL: str = "http://localhost:11434"
MODEL_NAME: str = "deepseek-r1:8b"
EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DOCUMENT_PATH: str = "./document"
PERSIST_DIR: str = "./data"  # ChromaDB 데이터 영구 저장 경로
```

5. 서버 실행:
```bash
uvicorn main:app --reload
```

## API 엔드포인트

### 1. 문서 관리
- `POST /api/v1/document/load`: 문서를 로드하고 벡터 DB에 저장
- `POST /api/v1/document/load_all`: 모든 문서를 자동으로 로드

### 2. 컬렉션 관리
- `GET /api/v1/collections`: 모든 컬렉션 목록 조회
- `GET /api/v1/collections/{collection_name}`: 특정 컬렉션의 문서 조회
- `DELETE /api/v1/collections/{collection_name}`: 특정 컬렉션 삭제
- `DELETE /api/v1/collections`: 모든 컬렉션 삭제

### 3. 질의응답
- `POST /api/v1/query`: 문서 기반 질의응답 수행

## 시스템 구성

```
app/
├── main.py                # FastAPI 애플리케이션 진입점
├── config.py             # 환경 변수 및 설정
├── routers/             # API 엔드포인트 정의
│   └── rag_router.py    # RAG 관련 라우터
├── schemas/             # API 요청/응답 스키마
│   └── rag.py          # RAG 관련 스키마
├── services/            # 비즈니스 로직
│   └── rag_service.py  # RAG 서비스 구현
└── utils/              # 유틸리티
    └── vector_store.py # 벡터 저장소 구현
```

## 주요 컴포넌트

### 1. 벡터 저장소 (VectorStore)
- ChromaDB 기반 구현
- 문서의 벡터 임베딩 저장 및 검색
- 다중 컬렉션 지원

### 2. RAG 서비스
- 문서 로딩 및 관리
- 벡터 검색 기반 관련 문서 검색
- Ollama API를 통한 응답 생성

### 3. API 라우터
- RESTful API 엔드포인트 제공
- 에러 처리 및 응답 포맷팅
- 최소화된 로깅

## 성능 최적화

- Ollama API 타임아웃 설정
  * 총 타임아웃: 120초
  * 연결 타임아웃: 30초
  * 읽기 타임아웃: 120초
  * 쓰기 타임아웃: 30초

- 생성 파라미터 최적화
  * temperature: 0.7
  * top_p: 0.9
  * top_k: 40

## 로깅

- 최소화된 로깅 구현
- API 응답만 로그로 출력
- 에러 발생 시 상세 정보 포함
