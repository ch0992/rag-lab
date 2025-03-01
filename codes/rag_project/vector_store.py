import json
from langchain_community.vectorstores import Chroma
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
    - `persist_directory`를 설정하여 데이터 영구 저장
    """
    try:
        # 문서가 Document 객체인 경우 텍스트 추출
        texts = []
        for doc in documents:
            if hasattr(doc, 'page_content'):
                texts.append(doc.page_content)
            elif isinstance(doc, str):
                texts.append(doc)
            else:
                raise ValueError(f"Unsupported document type: {type(doc)}")

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
        for text in texts:
            if isinstance(text, str) and text.strip():
                doc_splits = text_splitter.split_text(text)
                splits.extend(doc_splits)

        if not splits:
            raise ValueError("No valid text content found in documents")

        # ✅ 임베딩 모델 사용
        embedding_model = NomicEmbeddings()

        # ✅ Chroma 인스턴스 생성
        vector_db = Chroma.from_texts(
            texts=splits,
            embedding=embedding_model,
            collection_name=collection_name,
            persist_directory=PERSIST_DIR
        )

        return vector_db

    except Exception as e:
        raise RuntimeError(f"❌ 벡터DB 저장 실패: {str(e)}")