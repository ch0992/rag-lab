# RAG Lab - Jupyter Notebooks

RAG(Retrieval-Augmented Generation) 시스템을 Jupyter Notebook 환경에서 실습하고 테스트할 수 있는 프로젝트입니다.

## 시스템 구성

- ChromaDB: 벡터 데이터베이스
- Ollama: LLM 서버 (deepseek-r1:8b 모델 사용)
- LangChain: LLM 프레임워크
- HuggingFace Embeddings: 한국어 최적화 임베딩 모델

## 설치 방법

1. 가상환경 설정
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

2. ChromaDB 설치 및 실행
```bash
docker pull chromadb/chroma
docker run -p 8090:8090 chromadb/chroma
```

3. Ollama 설치 및 모델 다운로드
```bash
curl https://ollama.ai/install.sh | sh
ollama pull deepseek-r1:8b
```

## 노트북 구성

1. `00_setup_and_run.ipynb`
   - 환경 설정 확인
   - 서버 상태 점검
   - 필요한 패키지 확인

2. `01_document_store.ipynb`
   - 문서 벡터화
   - ChromaDB에 문서 저장
   - 한국어 텍스트 처리

3. `02_document_view.ipynb`
   - 저장된 문서 조회
   - 벡터 검색 테스트
   - 문서 메타데이터 확인

4. `03_query_documents.ipynb`
   - RAG 질의-응답
   - LLM 연동
   - 컨텍스트 기반 응답 생성

5. `04_all_in_one.ipynb`
   - 모든 기능 통합 버전
   - 환경 설정부터 질의-응답까지 한 번에 실행
   - 예제 문서와 질문 포함

## 사용 방법

### 기본 실행 방법
1. 서버 실행 확인
   - ChromaDB 서버가 8090 포트에서 실행 중인지 확인
   - Ollama 서버가 11434 포트에서 실행 중인지 확인

2. Jupyter Notebook 실행
```bash
source venv/bin/activate
jupyter notebook
```

### 단계별 실행
- 00 → 01 → 02 → 03 순서로 노트북을 실행하며 각 기능을 테스트
- 각 노트북의 셀을 순차적으로 실행
- 마크다운 설명을 참고하여 진행

### 통합 실행
- `04_all_in_one.ipynb` 하나만 실행하여 모든 기능 테스트
- 환경 설정부터 질의-응답까지 자동으로 진행
- 예제 데이터로 즉시 테스트 가능

## 디렉토리 구조

```
rag-jupyter/
├── readme.md
├── requirements.txt
├── 00_setup_and_run.ipynb
├── 01_document_store.ipynb
├── 02_document_view.ipynb
├── 03_query_documents.ipynb
├── 04_all_in_one.ipynb
├── data/           # 문서 데이터 저장
└── chroma/         # 벡터 데이터베이스 저장
```

## 주의사항

- ChromaDB와 Ollama 서버가 실행 중이어야 합니다.
- 대용량 문서 처리 시 메모리 사용량에 주의하세요.
- 한국어 처리를 위해 최적화된 임베딩 모델을 사용합니다.
- 단계별 실행 시 노트북 순서를 지켜주세요.
- 통합 실행 시에는 `04_all_in_one.ipynb` 만으로 충분합니다.
