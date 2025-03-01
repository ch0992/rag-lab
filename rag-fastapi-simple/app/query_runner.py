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
2. 영어 단어는 모두 한글로 변환하세요 (예: API -> 에이피아이).
3. 특수문자나 한자는 절대 사용하지 마세요.
4. 간단명료하게 답변하세요.
5. 불필요한 설명이나 부연은 제외하세요.
6. 답변 전에 생각하는 과정을 보여주지 마세요.
7. 바로 결과만 보여주세요.

질문:
{prompt}

답변 형식:
[질문에 대한 답변만 작성]
"""
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": korean_prompt,
                "system": "당신은 한국어 전용 답변 도우미입니다. 다음 규칙을 절대적으로 따르세요:\n1. 오직 한글로만 답변하세요\n2. 영어는 한글로 변환하세요 (API -> 에이피아이)\n3. 특수문자와 한자는 사용하지 마세요\n4. 간단명료하게 핵심만 답변하세요\n5. 모든 외래어는 한글로 표기하세요\n6. 답변 이외의 설명은 하지 마세요\n7. 생각하는 과정을 보여주지 마세요\n8. 바로 결과만 보여주세요"
            },
            stream=True  # Enable streaming for better response handling
        )
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                json_response = json.loads(line)
                if 'response' in json_response:
                    full_response += json_response['response']
        
        # think 태그와 그 내용 제거
        if '<think>' in full_response:
            parts = full_response.split('<think>')
            for i in range(1, len(parts)):
                if '</think>' in parts[i]:
                    parts[i] = parts[i].split('</think>', 1)[1]
            full_response = ''.join(parts).strip()
            
        # 응답에서 '[' 로 시작하는 헤더 부분 제거
        if '[' in full_response:
            full_response = full_response.split(']')[-1].strip()
            
        # 추가 개행 제거 및 포맷 정리
        lines = [line.strip() for line in full_response.split('\n') if line.strip()]
        
        # 처음 줄은 그대로 유지하고, 번호 항목만 구분
        formatted_response = lines[0]
        for line in lines[1:]:
            if line.startswith(('1)', '2)', '3)', '4)', '5)', '6)', '7)', '8)', '9)')): 
                formatted_response += '\n\n' + line
            else:
                formatted_response += '\n' + line
        
        return formatted_response if formatted_response else "⚠️ Ollama 응답 오류"

    except requests.exceptions.RequestException as e:
        return f"🚨 Ollama 연결 오류: {e}"

def run_rag_query(vector_db, query):
    """벡터DB에서 질문에 대한 답변을 검색"""
    try:
        # 벡터DB에서 검색 수행
        results = vector_db.similarity_search(query, k=3)
        
        # 검색된 각 문서를 구조화된 형태로 처리
        contexts = []
        for i, doc in enumerate(results, 1):
            contexts.append(f"문서 {i}:\n{doc.page_content}")
        
        # 명확한 구분자로 문서들을 결합
        context = "\n\n=== 다음 문서 ===\n\n".join(contexts)
        
        # 간단한 상태 메시지 출력
        print(f"\n💾 벡터 DB 콜렉션 조회 성공")
        print(f"🔍 관련 문서 {len(results)}개 찾음")
        
        # 프롬프트 구성 - 전체 정보를 출력하도록 수정
        prompt = f"""역할: 당신은 주어진 문서들에서 모든 관련 정보를 찾아 종합적으로 답변하는 역할을 합니다.

문서 내용:
{context}

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

답변: """
        
        # 검색 결과를 Ollama API로 전달하여 답변 생성
        response = query_ollama(prompt)
        print(f"\n💬 답변: {response}\n")
        return response
    except Exception as e:
        print(f"❌ RAG 검색 중 오류 발생: {e}")
        return "⚠️ RAG 검색 오류"