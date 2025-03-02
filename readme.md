# RAG (Retrieval-Augmented Generation) Lab

이 프로젝트는 Ollama와 ChromaDB를 사용하는 한국어 특화 RAG(Retrieval-Augmented Generation) 시스템의 구현 예제들을 포함하고 있습니다. 다양한 구현 방식과 아키텍처를 통해 RAG 시스템의 이해와 학습을 돕습니다.

## 프로젝트 구조 (Project Structure)

```
rag-lab/
├── rag-fastapi-simple/     # 기본적인 FastAPI RAG 구현
├── rag-fastapi-structured/ # 구조화된 FastAPI RAG 구현
├── rag-jupyter/           # Jupyter Notebook RAG 구현
├── infra-setup/          # 인프라 설치 및 설정
├── integration-tests/    # 인프라 통합 테스트
└── requirements.txt     # 공통 의존성
```

## 필수 요구사항 (Prerequisites)

### 운영 환경 (Operating System)
- Linux 환경 지원

### 프로그래밍 환경 (Programming Environment)
- Python 3.9 이상

### 필수 컴포넌트 (Required Components)

1. **ChromaDB**
   - 설치 옵션:
     - Docker Desktop 클러스터를 통한 설치 (추천)
     - 로컬 설치 (선택사항)
   - 자세한 설치 가이드는 `infra-setup` 디렉토리 참조

2. **Ollama**
   - 한국어 질의응답을 위한 LLM 엔진
   - 모델: deepseek-r1:8b (추천)
   - 설치 방법:
     ```bash
     # Linux
     curl https://ollama.ai/install.sh | sh
     
     # 서버 실행
     ollama serve
     
     # 모델 다운로드
     ollama pull deepseek-r1:8b
     ```

## 구현 예제 (Implementation Examples)

### 1. rag-fastapi-simple
- 기본적인 FastAPI 기반 RAG 구현
- 단일 파일 구조로 빠른 이해와 시작 가능
- 핵심 기능에 집중한 최소한의 구현

### 2. rag-fastapi-structured
- FastAPI의 구조화된 아키텍처 적용
- 라우터, 서비스, 스키마 분리
- 확장 가능하고 유지보수가 용이한 구조

### 3. rag-jupyter
- Jupyter Notebook 기반 RAG 구현
- 단계별 RAG 프로세스 시각화
- 실험과 학습을 위한 인터랙티브 환경

## 인프라 및 테스트 (Infrastructure & Tests)

### 1. infra-setup
- ChromaDB 설치 및 설정
- 벡터 데이터베이스 환경 구성

### 2. integration-tests
- ChromaDB CRUD 테스트
- Ollama API 연동 테스트
- 인프라 컴포넌트 통합 테스트

## 시작하기 (Getting Started)

1. 의존성 설치:
```bash
pip install -r requirements.txt
```

2. ChromaDB 설치:
- `infra-setup` 디렉토리의 설치 가이드 참조

3. Ollama 설치 및 실행:
```bash
# Mac OS
brew install ollama

# 서버 실행
ollama serve

# 모델 다운로드
ollama pull deepseek-r1:8b
```

4. 원하는 구현 예제 실행:
- `rag-fastapi-simple`: 빠른 시작과 기본 이해 (자세한 설명은 [`rag-fastapi-simple/readme.md`](rag-fastapi-simple/readme.md) 참조)
- `rag-fastapi-structured`: 프로덕션 수준의 구현 (자세한 설명은 [`rag-fastapi-structured/README.md`](rag-fastapi-structured/README.md) 참조)
- `rag-jupyter`: 단계별 학습과 실험 (자세한 설명은 [`rag-jupyter/README.md`](rag-jupyter/README.md) 참조)

## 특징 (Features)

- 한국어 특화 RAG 시스템
- 다양한 구현 방식 제공
- 실용적인 예제와 테스트
- 확장 가능한 아키텍처
- 상세한 문서화

## 작성자 (Author)

**최영규 (Yeong-gyu Choi)**
- LinkedIn: [Yeong-gyu Choi](https://www.linkedin.com/in/yeong-gyu-choi-32355b174/)
- Email: ktma82@gmail.com

## 라이선스 (License)

MIT License
