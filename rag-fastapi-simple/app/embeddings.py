from langchain_huggingface import HuggingFaceEmbeddings

# Use SentenceTransformer model for embeddings
NomicEmbeddings = lambda: HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
    


