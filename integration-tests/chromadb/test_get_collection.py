import chromadb

chroma_client = chromadb.HttpClient(host="localhost", port=8090)

# 저장된 컬렉션 목록 조회
collections = chroma_client.list_collections()
print("저장된 컬렉션 목록:", collections)