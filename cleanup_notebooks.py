from notebooklm_tools.core.client import NotebookLMClient
from notebooklm_tools.core.auth import load_cached_tokens

def cleanup_duplicate_notebooks():
    try:
        print("Authenticating...")
        tokens = load_cached_tokens()
        if hasattr(tokens, 'cookies'):
            cookies = tokens.cookies
        elif isinstance(tokens, dict) and 'cookies' in tokens:
            cookies = tokens['cookies']
        else:
            cookies = getattr(tokens, 'cookie_jar', None) or getattr(tokens, 'token', None)

        client = NotebookLMClient(cookies=cookies)
        
        print("Listing notebooks...")
        notebooks = client.list_notebooks()
        
        # Target: Title starts with "K_Bank_IPO" (ALL of them to clean slate)
        targets = [nb for nb in notebooks if nb.title.startswith("K_Bank_IPO")]
        
        print(f"Found {len(targets)} duplicate/stale notebooks to delete.")
        
        for nb in targets:
            print(f"Deleting {nb.title} ({nb.id})...")
            client.delete_notebook(nb.id)
            print("Deleted.")
            
        print("Cleanup complete.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup_duplicate_notebooks()
