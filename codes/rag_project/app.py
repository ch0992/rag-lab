from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_chroma import Chroma
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
    
    # 모든 텍스트 파일 로드
    loaded_files = []
    for file_path in document_path.glob('*.txt'):
        collection_name = file_path.stem  # 확장자를 제외한 파일명
        
        try:
            # 문서 로드 및 분할
            loader = TextLoader(str(file_path))
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            split_docs = text_splitter.split_documents(documents)
            
            # 벡터 DB 저장
            vector_db = store_documents_in_chroma(split_docs, collection_name)
            loaded_files.append(file_path.name)
            print(f"\n📄 '{file_path.name}'를 '{collection_name}' 콜렉션으로 로드했습니다.")
            
        except Exception as e:
            print(f"\n⚠️ '{file_path.name}' 로드 실패: {e}")
    
    if loaded_files:
        print(f"\n📂 총 {len(loaded_files)}개의 파일을 로드했습니다: {', '.join(loaded_files)}")
    else:
        print(f"\nℹ️ '{DOCUMENT_DIR}' 폴더에 로드할 텍스트 파일이 없습니다.")

class LoadDocumentRequest(BaseModel):
    file_path: str
    collection_name: str

class QueryRequest(BaseModel):
    collection_name: str
    query: str

class CollectionContent(BaseModel):
    collection_name: str

@app.post("/load/")
async def load_document(request: LoadDocumentRequest):
    try:
        # Check if file exists
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {request.file_path} not found")
        
        print(f"\n📂 문서 로드 시작: {file_path}")
        
        # 문서 로드 및 분할
        loader = TextLoader(str(file_path))
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        split_docs = text_splitter.split_documents(documents)
        
        # 벡터 DB 저장
        vector_db = store_documents_in_chroma(split_docs, request.collection_name)
        
        print(f"\n💾 벡터 DB 저장 완료: {len(split_docs)} 개의 문서 청크 저장됨")
        
        return {"message": f"Document loaded and stored in collection: {request.collection_name}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/")
async def list_collections():
    try:
        # ChromaDB v0.6.0에서는 콜렉션 이름만 반환
        collection_names = chroma_client.list_collections()
        
        # 저장된 콜렉션이 없다면 기본 콜렉션 추가
        if not collection_names and Path(PERSIST_DIR).exists():
            embeddings = NomicEmbeddings()
            vector_db = Chroma(
                collection_name="rag_test",
                embedding_function=embeddings,
                persist_directory=PERSIST_DIR
            )
            collection_names = ["rag_test"]
        
        print(f"\n📁 조회된 콜렉션: {collection_names}")
        return {"collections": collection_names}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}/contents")
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

@app.post("/query/")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
