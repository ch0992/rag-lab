from vector_store import parse_llm_response

# Example response from your question
sample_response = """{"model":"deepseek-r1:8b","created_at":"2025-02-28T06:57:49.321508Z","response":"<think>","done":false}{"model":"deepseek-r1:8b","created_at":"2025-02-28T06:57:49.362944Z","response":"\\n","done":false}{"model":"deepseek-r1:8b","created_at":"2025-02-28T06:57:49.405472Z","response":"嗯","done":false}{"model":"deepseek-r1:8b","created_at":"2025-02-28T06:57:49.447274Z","response":"，我","done":false}"""

# Parse the response
parsed_response = parse_llm_response(sample_response)
print("Parsed Response:")
print(parsed_response)
