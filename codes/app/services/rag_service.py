import os
import json
import httpx
from typing import List, Dict, Any
from config import settings
from utils.embeddings import get_embeddings
from utils.vector_store import VectorStore

class RAGService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.MODEL_NAME
        self.document_path = settings.DOCUMENT_PATH
        
    def load_all_documents(self) -> List[str]:
        """document 폴더의 모든 텍스트 파일을 로드하여 벡터 DB에 저장합니다."""
        loaded_files = []
        try:
            # 문서 폴더 내 모든 .txt 파일 검색
            for file_name in os.listdir(self.document_path):
                if not file_name.endswith('.txt'):
                    continue
                    
                file_path = os.path.join(self.document_path, file_name)
                collection_name = os.path.splitext(file_name)[0]
                
                # 파일 내용 읽기
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
                    
                if text_content:
                    # 벡터 DB 저장
                    self.vector_store.add_texts([text_content], collection_name)
                    loaded_files.append(file_name)
                    
            return loaded_files
            
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    async def query_ollama(self, prompt: str) -> str:
        try:
            # 타임아웃 설정 증가
            timeout = httpx.Timeout(
                timeout=120.0,     # 전체 타임아웃
                connect=30.0,     # 연결 타임아웃
                read=120.0,       # 읽기 타임아웃
                write=30.0,       # 쓰기 타임아웃
                pool=30.0         # 풀 타임아웃
            )
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,  # 스트리밍 비활성화
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "top_k": 40
                        }
                    }
                )

                
                if response.status_code != 200:
                    print(f"Error response from Ollama API: {response.text}")
                    return "⚠️ Ollama API 오류"
                
                json_response = response.json()

                
                if 'response' not in json_response:
    
                    return "⚠️ Ollama 응답 오류"
                
                response_text = json_response['response']
                
                # think 태그와 그 내용 제거
                if '<think>' in response_text:
                    parts = response_text.split('<think>')
                    for i in range(1, len(parts)):
                        if '</think>' in parts[i]:
                            parts[i] = parts[i].split('</think>', 1)[1]
                    response_text = ''.join(parts).strip()
                
                # 응답에서 '[' 로 시작하는 헤더 부분 제거
                if '[' in response_text:
                    response_text = response_text.split(']')[-1].strip()
                
                # 추가 개행 제거 및 포맷 정리
                lines = [line.strip() for line in response_text.split('\n') if line.strip()]
                
                # 처음 줄은 그대로 유지하고, 번호 항목만 구분
                if not lines:
                    return "⚠️ 응답이 비어있습니다."
                    
                formatted_response = lines[0]
                for line in lines[1:]:
                    if line.startswith(('1)', '2)', '3)', '4)', '5)', '6)', '7)', '8)', '9)')): 
                        formatted_response += '\n\n' + line
                    else:
                        formatted_response += '\n' + line
                
                return formatted_response
                
        except Exception as e:
            import traceback
            print(f"Error in query_ollama: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return "⚠️ Ollama API 오류"

    async def run_rag_query(self, collection_name: str, query: str) -> str:
        try:
            # 쿼리 임베딩 생성
            query_embedding = get_embeddings([query])
            # 지정된 콜렉션의 문서 검색
            similar_docs = self.vector_store.similarity_search(query_embedding, collection_name)
            if not similar_docs:
                return "문서가 없습니다."
            
            # 프롬프트 생성
            prompt = f"""역할: 당신은 주어진 문서들에서 모든 관련 정보를 찾아 종합적으로 답변하는 역할을 합니다.

문서 내용:
{similar_docs}

질문: {query}

중요 지침:
1. 모든 문서의 내용을 검토하여 관련된 정보를 모두 찾아주세요.
2. 각 문서의 정보를 종합하여 하나의 완성된 답변을 만들어주세요.
3. 문서에 없는 내용은 추가하지 마세요.
4. 외부 지식이나 추론은 하지 마세요.
5. 영어나 특수문자는 최소한으로 사용하세요.
6. 여러 문서의 정보가 있다면 모두 포함해서 답변해주세요.
7. 답변은 간결하면서도 포괄적이어야 합니다.
8. 문서에서 관련 내용을 찾을 수 없다면 '주어진 문서에서 관련 정보를 찾을 수 없습니다.'라고만 답변해주세요.
9. 답변 시작에는 '💬 답변: '을 붙여주세요.
"""
            # 프롬프트 출력 제거
            
            # Ollama API 호출
            response = await self.query_ollama(prompt)
            return response
            
        except Exception as e:
            import traceback
            print(f"Error in run_rag_query: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return "쿼리 처리 중 오류가 발생했습니다."
