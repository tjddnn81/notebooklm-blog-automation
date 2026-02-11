from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens
import json

try:
    tokens = load_cached_tokens()
    if hasattr(tokens, 'cookies'):
        cookies = tokens.cookies
    elif isinstance(tokens, dict) and 'cookies' in tokens:
        cookies = tokens['cookies']
    else:
        cookies = getattr(tokens, 'cookie_jar', None) or getattr(tokens, 'token', None)

    client = NotebookLMClient(cookies=cookies)
    
    nb_id = "30753d34-d282-4e8f-af7b-58f95e33f9f1"
    print(f"Checking notebook {nb_id}...")
    nb = client.get_notebook(nb_id)
    
    print(f"Type of nb: {type(nb)}")
    print(f"Content: {nb}")
    
    if isinstance(nb, list) and len(nb) > 0:
        real_nb = nb[0]
        print(f"Unwrapped Type: {type(real_nb)}")
        # Check source count on unwrapped
        sources = real_nb.get('sources') if isinstance(real_nb, dict) else getattr(real_nb, 'sources', [])
        print(f"Unwrapped Source count: {len(sources)}")


except Exception as e:
    print(f"Error: {e}")
