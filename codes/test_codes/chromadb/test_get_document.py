import chromadb

chroma_client = chromadb.HttpClient(host="localhost", port=8090)

# "rag_test" 컬렉션 가져오기
collection = chroma_client.get_collection("rag_test")

# 저장된 데이터 조회
all_docs = collection.get(include=["documents", "metadatas"])
print("저장된 데이터:", all_docs)