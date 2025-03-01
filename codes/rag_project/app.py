from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
import chromadb
from vector_store import store_documents_in_chroma
from query_runner import run_rag_query
from embeddings import NomicEmbeddings

# ChromaDB 설정 및 클라이언트 초기화
PERSIST_DIR = "./data"  # vector_store.py와 동일한 경로 사용
DOCUMENT_DIR = "./document"  # 문서 저장 경로

chroma_client = chromadb.Client(Settings(
    is_persistent=True,
    persist_directory=PERSIST_DIR
))

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # document 폴더가 없다면 생성
    document_path = Path(DOCUMENT_DIR)
    if not document_path.exists():
        document_path.mkdir(parents=True)
        print(f"\n📂 '{DOCUMENT_DIR}' 폴더를 생성했습니다.")
    
    # 텍스트 및 마크다운 파일 로드
    loaded_files = []
    for file_path in document_path.glob('*.txt'):
        collection_name = file_path.stem  # 확장자를 제외한 파일명
        
        try:
            # 파일 내용 직접 읽기
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            if not text_content.strip():
                print(f"\n⚠️ '{file_path.name}' 파일이 비어있습니다.")
                continue
                
            # 벡터 DB 저장
            vector_db = store_documents_in_chroma([text_content], collection_name)
            loaded_files.append(file_path.name)
            print(f"\n📄 '{file_path.name}'를 '{collection_name}' 콜렉션으로 로드했습니다.")
            
        except Exception as e:
            print(f"\n⚠️ '{file_path.name}' 로드 실패: {e}")
    
    if loaded_files:
        print(f"\n📂 총 {len(loaded_files)}개의 파일을 로드했습니다: {', '.join(loaded_files)}")
    else:
        print(f"\nℹ️ '{DOCUMENT_DIR}' 폴더에 로드할 텍스트 파일이 없습니다.")

class LoadDocumentRequest(BaseModel):
    file_path: str = "sample.txt"  # document 폴더 내 파일명 (예: sample.txt, sample.md)
    collection_name: str = ""  # 비어있으면 파일명이 콜렉션명으로 사용됨

class QueryRequest(BaseModel):
    collection_name: str
    query: str

class CollectionContent(BaseModel):
    collection_name: str
    
class DeleteCollectionResponse(BaseModel):
    message: str
    deleted_collection: str

@app.post("/load/", tags=["1. Load"])
async def load_document(request: LoadDocumentRequest):
    """
    텍스트 파일을 로드하여 벡터 DB에 저장합니다.
    
    Args:
        request (LoadDocumentRequest):
            - file_path: document 폴더 내 파일명 (예: sample.txt)
            - collection_name: 저장할 콜렉션명 (비어있으면 파일명 사용)
    
    Returns:
        dict: {
            "message": str - 성공 메시지,
            "collection_name": str - 저장된 콜렉션명
        }
    
    Raises:
        HTTPException: 
            - 404: 파일을 찾을 수 없음
            - 500: 기타 처리 오류
    """
    try:
        # 파일 경로 처리
        file_path = Path(DOCUMENT_DIR) / request.file_path
        if not file_path.exists():
            raise HTTPException(
                status_code=404, 
                detail=f"File '{request.file_path}' not found in '{DOCUMENT_DIR}' directory"
            )
        
        # 콜렉션명이 비어있으면 파일명 사용
        collection_name = request.collection_name or file_path.stem
        print(f"\n📂 문서 로드 시작: {file_path} -> {collection_name} 콜렉션")
        
        # 파일 내용 직접 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
            
        if not text_content.strip():
            raise HTTPException(
                status_code=400,
                detail=f"File '{request.file_path}' is empty"
            )
        
        # 벡터 DB 저장
        vector_db = store_documents_in_chroma([text_content], collection_name)
        print(f"\n💾 벡터 DB 저장 완료: {collection_name} 콜렉션")
        
        return {
            "message": "Document loaded and stored successfully",
            "collection_name": collection_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/", tags=["2. Collections"])
async def list_collections():
    """
    모든 콜렉션 목록을 반환합니다.
    
    Returns:
        dict: {
            "collections": List[str] - 콜렉션 이름 목록
        }
    """
    try:
        # ChromaDB v0.6.0에서는 콜렉션 이름만 반환
        collection_names = chroma_client.list_collections()
        print(f"\n📁 조회된 콜렉션: {collection_names}")
        return {"collections": collection_names}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collections/{collection_name}", response_model=DeleteCollectionResponse, tags=["2. Collections"])
async def delete_collection(collection_name: str):
    """
    지정된 콜렉션을 삭제합니다.
    
    Args:
        collection_name (str): 삭제할 콜렉션 이름
    
    Returns:
        DeleteCollectionResponse: {
            "message": str - 성공 메시지,
            "deleted_collection": str - 삭제된 콜렉션 이름
        }
    
    Raises:
        HTTPException: 콜렉션이 존재하지 않을 경우 404 에러
    """
    try:
        # 콜렉션 존재 여부 확인
        collections = chroma_client.list_collections()
        collection_names = [c.name for c in collections]
        if collection_name not in collection_names:
            raise HTTPException(
                status_code=404,
                detail=f"Collection '{collection_name}' not found"
            )
        
        # 콜렉션 삭제
        chroma_client.delete_collection(name=collection_name)
        print(f"\n🗑️ 콜렉션 삭제 완료: {collection_name}")
        
        return DeleteCollectionResponse(
            message="Collection deleted successfully",
            deleted_collection=collection_name
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}/contents", tags=["2. Collections"])
async def get_collection_contents(collection_name: str):
    try:
        # ChromaDB에서 콜렉션 가져오기
        try:
            collection = chroma_client.get_collection(name=collection_name)
        except ValueError:
            # 콜렉션이 없는 경우 langchain의 Chroma로 시도
            embeddings = NomicEmbeddings()
            vector_db = Chroma(
                collection_name=collection_name,
                embedding_function=embeddings,
                persist_directory=PERSIST_DIR
            )
            collection = chroma_client.get_collection(name=collection_name)
        
        # 콜렉션의 모든 데이터 조회
        result = collection.get()
        documents = result.get('documents', [])
        metadatas = result.get('metadatas', [])
        ids = result.get('ids', [])
        
        # 결과 포맷팅
        contents = []
        for doc, meta, id in zip(documents, metadatas, ids):
            contents.append({
                "id": id,
                "content": doc,
                "metadata": meta if meta else {}
            })
        
        print(f"\n📂 콜렉션 내용 조회: {collection_name}")
        return {"collection_name": collection_name, "contents": contents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/", tags=["3. Query"])
async def process_query(request: QueryRequest):
    try:
        # ChromaDB에서 콜렉션 가져오기
        embeddings = NomicEmbeddings()
        vector_db = Chroma(
            collection_name=request.collection_name,
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR
        )
        
        print(f"\n🔎 쿼리 시작: {request.collection_name} 콜렉션")
        
        # Run RAG query
        response = run_rag_query(vector_db, request.query)
        
        return {"response": response}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/collections", response_model=Dict[str, List[str]], tags=["2. Collections"])
async def delete_all_collections():
    """
    모든 콜렉션을 삭제합니다.
    
    Returns:
        dict: {
            "deleted_collections": List[str] - 삭제된 콜렉션 이름 목록
        }
    """
    try:
        collections = chroma_client.list_collections()
        deleted_collections = []
        
        for collection in collections:
            collection_name = collection.name
            chroma_client.delete_collection(name=collection_name)
            deleted_collections.append(collection_name)
            print(f"\n🗑️ 콜렉션 삭제 완료: {collection_name}")
        
        return {"deleted_collections": deleted_collections}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load/all", response_model=Dict[str, List[str]], tags=["1. Load"])
async def load_all_documents():
    """
    document 폴더의 모든 텍스트 파일을 로드하여 벡터 DB에 저장합니다.
    
    Returns:
        dict: {
            "loaded_files": List[str] - 로드된 파일 이름 목록
        }
    """
    try:
        document_path = Path(DOCUMENT_DIR)
        if not document_path.exists():
            document_path.mkdir(parents=True)
            print(f"\n📂 '{DOCUMENT_DIR}' 폴더를 생성했습니다.")
        
        loaded_files = []
        for file_path in document_path.glob('*.txt'):
            collection_name = file_path.stem
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                if not text_content.strip():
                    print(f"\n⚠️ '{file_path.name}' 파일이 비어있습니다.")
                    continue
                    
                vector_db = store_documents_in_chroma([text_content], collection_name)
                loaded_files.append(file_path.name)
                print(f"\n📄 '{file_path.name}'를 '{collection_name}' 콜렉션으로 로드했습니다.")
                
            except Exception as e:
                print(f"\n⚠️ '{file_path.name}' 로드 실패: {e}")
        
        if loaded_files:
            print(f"\n📂 총 {len(loaded_files)}개의 파일을 로드했습니다: {', '.join(loaded_files)}")
        else:
            print(f"\nℹ️ '{DOCUMENT_DIR}' 폴더에 로드할 텍스트 파일이 없습니다.")
            
        return {"loaded_files": loaded_files}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
