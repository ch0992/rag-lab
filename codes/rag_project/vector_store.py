import json
from langchain_chroma import Chroma
from embeddings import NomicEmbeddings  # embed 모듈 사용

# CHROMA 서비스 주소 (Kubernetes 클러스터 내 서비스 기준)
CHROMA_HOST = "localhost"
CHROMA_PORT = "8090"
PERSIST_DIR = "./data"  # ChromaDB 데이터 영구 저장 경로

from chromadb.config import Settings

def parse_llm_response(response: str) -> str:
    """Parse LLM response from JSON format to readable text

    Args:
        response (str): JSON response from LLM

    Returns:
        str: Parsed human readable response
    """
    try:
        # Split response into individual JSON objects
        response_parts = response.split('}{"model"')
        response_parts = [part if i == 0 else '{"model"' + part 
                         for i, part in enumerate(response_parts)]
        
        # Extract actual response text from each part
        full_text = ''
        for part in response_parts:
            try:
                json_obj = json.loads(part)
                if 'response' in json_obj:
                    full_text += json_obj['response']
            except json.JSONDecodeError:
                continue
        
        # Remove think tags and clean up the text
        full_text = full_text.replace('<think>\n', '').replace('</think>', '')
        
        return full_text.strip()
    except Exception as e:
        return f"Error parsing response: {str(e)}"

from langchain.text_splitter import RecursiveCharacterTextSplitter

def store_documents_in_chroma(documents, collection_name="rag_test"):
    """
    문서를 벡터로 변환하여 ChromaDB에 저장하는 함수.
    - RecursiveCharacterTextSplitter로 한글 문서에 최적화된 청크 생성
    - LangChain의 `HuggingFaceEmbeddings`를 사용하여 벡터화
    - Kubernetes 내 ChromaDB 서비스에 연결
    - `persist_directory`를 설정하여 데이터 영구 저장
    """
    try:
        # 한글 문서에 최적화된 텍스트 스플리터 설정
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""],
            chunk_size=300,  # 한글 기준 약 150-200자 정도
            chunk_overlap=50,  # 문맥 유지를 위한 오버랩
            length_function=len,
            keep_separator=False,
            is_separator_regex=False
        )
        
        # 문서를 청크로 분할
        splits = []
        for doc in documents:
            doc_splits = text_splitter.split_text(doc)
            splits.extend(doc_splits)
            
        documents = splits

        # ✅ HuggingFace 임베딩 모델 사용
        embedding_model = NomicEmbeddings()  # embed 모듈 사용

        # ✅ Chroma 클라이언트 설정 (클라이언트 직접 생성)
        settings = Settings(
            is_persistent=True,
            persist_directory=PERSIST_DIR
        )

        # ✅ Chroma 인스턴스 생성
        vector_db = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_model,
            persist_directory=PERSIST_DIR,
            client_settings=settings  # ✅ 클라이언트 설정 적용
        )

        # ✅ 문서를 벡터DB에 추가
        vector_db.add_documents(documents)
        # ChromaDB now automatically persists data

        # ✅ Chroma 객체가 올바른지 확인
        if not isinstance(vector_db, Chroma):
            raise RuntimeError("❌ Chroma 객체 생성 실패: 반환된 객체가 Chroma 인스턴스가 아님")

        return vector_db  # ✅ Chroma 객체 반환
    except Exception as e:
        raise RuntimeError(f"❌ 벡터DB 저장 실패: {e}")