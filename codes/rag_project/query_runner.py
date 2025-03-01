import json
import requests
from langchain_community.vectorstores import Chroma

# Ollama 서버 정보
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "deepseek-r1:8b"

def query_ollama(prompt):
    """Ollama API를 사용하여 deepseek-r1:8b 모델 호출 (스트리밍 응답 처리)"""
    try:
        # 프롬프트에 한글 응답 요청 추가
        korean_prompt = f"""
다음 지시사항을 엄격히 따라 답변해주세요:

1. 반드시 한글로만 답변하세요.
2. 영어 단어는 모두 한글로 변환하세요 (예: AI -> 에이아이).
3. 특수문자나 한자는 절대 사용하지 마세요.
4. 간단명료하게 답변하세요.
5. 불필요한 설명이나 부연은 제외하세요.

질문:
{prompt}

답변 형식:
[질문에 대한 간단한 한글 답변만 작성]
"""
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": korean_prompt,
                "system": "당신은 한국어 전용 답변 도우미입니다. 다음 규칙을 절대적으로 따르세요:\n1. 오직 한글로만 답변하세요\n2. 영어는 한글로 변환하세요 (AI -> 에이아이)\n3. 특수문자와 한자는 사용하지 마세요\n4. 간단명료하게 핵심만 답변하세요\n5. 모든 외래어는 한글로 표기하세요\n6. 답변 이외의 설명은 하지 마세요"
            },
            stream=True  # Enable streaming for better response handling
        )
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    full_response += json_response['response']
        
        # 추론 과정을 제거하고 최종 한글 답변만 추출
        if '\n\n' in full_response:
            final_response = full_response.split('\n\n')[-1]
        else:
            final_response = full_response
            
        # 특수 문자 제거 및 공백 정리
        final_response = final_response.strip().replace('"', '')
        return final_response if final_response else "⚠️ Ollama 응답 오류"

    except requests.exceptions.RequestException as e:
        return f"🚨 Ollama 연결 오류: {e}"

def run_rag_query(vector_db, query):
    """벡터DB에서 질문에 대한 답변을 검색"""
    try:
        # 벡터DB에서 검색 수행
        results = vector_db.similarity_search(query, k=3)
        
        # 검색된 문서들의 내용을 하나의 문자열로 결합
        context = "\n\n".join([doc.page_content for doc in results])
        
        # 간단한 상태 메시지 출력
        print(f"\n💾 벡터 DB 콜렉션 조회 성공")
        print(f"🔍 관련 문서 {len(results)}개 찾음")
        
        # 프롬프트 구성 - 문서 내용은 내부적으로만 사용
        prompt = f"""역할: 당신은 주어진 문서에서만 정보를 찾아 답변하는 역할을 합니다.

문서 내용:
{context}

질문: {query}

중요 지침:
1. 반드시 위의 문서 내용에서만 정보를 찾아서 답변해야 합니다.
2. 문서에 없는 내용은 절대 추가하지 마세요.
3. 외부 지식이나 추론을 통한 답변은 하지 마세요.
4. 영어나 특수문자는 사용하지 마세요.
5. 문서에서 찾은 내용을 간결하게 요약해서 답변해주세요.
6. 문서에서 관련 내용을 찾을 수 없다면 '주어진 문서에서 관련 정보를 찾을 수 없습니다.'라고만 답변해주세요.

답변: """
        
        # 검색 결과를 Ollama API로 전달하여 답변 생성
        response = query_ollama(prompt)
        print(f"\n💬 답변: {response}\n")
        return response
    except Exception as e:
        print(f"❌ RAG 검색 중 오류 발생: {e}")
        return "⚠️ RAG 검색 오류"