
import sys
import io

# Force utf-8 for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    import notebooklm_tools.core.auth as auth
    import inspect
    
    print("Inspecting load_cached_tokens signature:")
    # print(inspect.signature(auth.load_cached_tokens))

    print("Loading cached tokens...")
    tokens = auth.load_cached_tokens()
    
    print(f"Tokens type: {type(tokens)}")
    print(f"Tokens attributes: {[a for a in dir(tokens) if not a.startswith('_')]}")
    
    # Try accessing as attribute or converting to dict
    try:
        cookies = tokens.cookies
    except AttributeError:
        # Fallback if it's named differently
        cookies = getattr(tokens, 'cookie_jar', None) or getattr(tokens, 'token', None)
    
    print(f"Extracted cookies type: {type(cookies)}")
    
    from notebooklm_tools.core.client import NotebookLMClient
    print("Initializing client with cookies...")
    client = NotebookLMClient(cookies=cookies)
    
    print("Client methods:")
    print([m for m in dir(client) if not m.startswith('_')])
    
    notebook_id = "ab566e05-d973-4d2b-b467-e07d3c38b7d9"
    query = "빗썸의 최신 이슈(비트코인 오지급 등)와 2026년 전망 및 분석에 대한 상세한 블로그 포스트를 작성해줘. 서론 본론 결론으로 나누어서 작성해."
    
    from notebooklm_tools.core.client import NotebookLMClient
    import inspect
    
    print("Studio Methods Signatures:")
    for method in ['create_audio_overview', 'create_quiz', 'create_study_guide', 'create_note', 'create_report']:
        if hasattr(NotebookLMClient, method):
            print(f"\n{method}:")
            print(inspect.signature(getattr(NotebookLMClient, method)))
        else:
             print(f"\n{method} not found")
             
    # Also check availability of 'create_faq' or similar if study guide isn't it
    print("\nLooking for 'FAQ' related methods:")
    print([m for m in dir(NotebookLMClient) if 'faq' in m.lower()])

        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
