import os
from typing import List
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings

class VectorStore:
    class EmbeddingFunction:
        def __init__(self, model):
            self.model = model
            
        def __call__(self, input):
            return self.model.embed_documents(input)
    
    def __init__(self):
        self.document_path = settings.DOCUMENT_PATH
        self.persist_dir = settings.PERSIST_DIR
        
        # ChromaDB 데이터 디렉토리 정리
        self._cleanup_chroma_data()
            
        # 임베딩 모델 초기화
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )
        
        # 임베딩 함수 초기화
        self.embed_function = self.EmbeddingFunction(self.embedding_model)
        
        # ChromaDB 초기화
        import chromadb
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
    def _cleanup_chroma_data(self):
        """ChromaDB 데이터 디렉토리 정리"""
        import shutil
        
        # persist_dir가 없으면 생성
        if not os.path.exists(self.persist_dir):
            os.makedirs(self.persist_dir)
            return
            
        # UUID 패턴의 디렉토리 정리
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        import re
        
        for item in os.listdir(self.persist_dir):
            item_path = os.path.join(self.persist_dir, item)
            if os.path.isdir(item_path) and re.match(uuid_pattern, item):
                shutil.rmtree(item_path)

    
    def add_texts(self, texts: List[str], collection_name: str):
        """텍스트를 벡터 스토어에 추가합니다."""
        if not texts:
            return
            
        try:
            # 콜렉션 존재 여부 확인
            try:
                collection = self.client.get_collection(collection_name)
            except:
                # 콜렉션이 없는 경우 생성
                collection = self.client.create_collection(
                    name=collection_name,
                    embedding_function=self.embed_function
                )
                
            # 현재 콜렉션의 문서 ID 확인
            current_docs = collection.get()
            current_ids = set(current_docs.get('ids', []))
            
            # 새로 추가할 문서 ID 생성
            new_docs = []
            new_ids = []
            new_metadatas = []
            
            for i, text in enumerate(texts):
                doc_id = f"{collection_name}_{i}"
                if doc_id not in current_ids:
                    new_docs.append(text)
                    new_ids.append(doc_id)
                    new_metadatas.append({"source": collection_name})
            
            # 새로운 문서가 있는 경우에만 추가
            if new_docs:
                collection.add(
                    documents=new_docs,
                    ids=new_ids,
                    metadatas=new_metadatas
                )
            
        except Exception as e:
            import traceback
            print(f"Error adding documents: {e}")
            print(f"Traceback: {traceback.format_exc()}")
    
    def clear(self):
        """모든 문서와 임베딩을 삭제합니다."""
        collections = self.client.list_collections()
        for collection_name in collections:
            self.client.delete_collection(collection_name)
    
    def similarity_search(self, query_embedding: List[float], collection_name: str, top_k: int = 1) -> str:
        """
        쿼리와 가장 유사한 문서를 찾아 반환합니다.
        """
        try:
            # 콜렉션 가져오기
            collection = self.client.get_collection(collection_name)

            results = collection.query(
                query_embeddings=query_embedding,  # ChromaDB는 단일 임베딩을 바로 받을 수 있음
                n_results=top_k
            )

            
            # 결과 검사
            if not results or 'documents' not in results or not results['documents']:

                return "문서가 없습니다."
                
            if not results['documents'][0]:

                return "문서가 없습니다."
                
            document = results['documents'][0][0]

            return document
            
        except Exception as e:
            import traceback
            print(f"Error in similarity search: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return "문서가 없습니다."
    
    def list_collections(self) -> List[str]:
        """모든 콜렉션 목록을 반환합니다."""
        return self.client.list_collections()
    
    def delete_collection(self, collection_name: str):
        """지정된 콜렉션을 삭제합니다."""
        self.client.delete_collection(collection_name)
        
    def delete_all_collections(self) -> List[str]:
        """모든 콜렉션을 삭제하고 삭제된 콜렉션 목록을 반환합니다."""
        collections = self.list_collections()
        for collection in collections:
            self.delete_collection(collection)
        return collections
        
    def get_collection_documents(self, collection_name: str) -> List[str]:
        """지정된 콜렉션의 모든 문서를 반환합니다."""
        collection = self.client.get_collection(collection_name)
        results = collection.get()
        return results['documents'] if results['documents'] else []
