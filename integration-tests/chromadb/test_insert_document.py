import chromadb

# ✅ 수정된 코드 (HttpClient 사용)
chroma_client = chromadb.HttpClient(host="localhost", port=8090)  # 포트 확인 필요

# 컬렉션 생성
collection = chroma_client.get_or_create_collection(name="rag_test")

# 샘플 데이터 삽입
collection.add(
    ids=["1", "2"],
    documents=["이것은 테스트 문서입니다.", "RAG 시스템 구축 중입니다."],
    metadatas=[{"source": "test1"}, {"source": "test2"}]
)

# 검색 테스트
results = collection.query(
    query_texts=["RAG 구축"],
    n_results=2
)

print(results)