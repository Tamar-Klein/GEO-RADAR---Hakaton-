from anthropic import Anthropic
import os
from dotenv import load_dotenv
import httpx

load_dotenv()
a_key = os.getenv('ANTHROPIC_API_KEY', '')

print('Testing Claction with web_search tool...')
try:
    claude_client = Anthropic(api_key=a_key.strip(), http_client=httpx.Client(verify=False))
    print('✓ Connected with httpx.Client')
except TypeError as e:
    print(f'✗ TypeError with httpx: {e}')
    try:
        claude_client = Anthropic(api_key=a_key.strip())
        print('✓ Connected without httpx.Client')
    except Exception as e2:
        print(f'✗ Failed without httpx: {e2}')
except Exception as e:
    print(f'✗ Error: {e}')

# Try to use web_search tool
try:
    response = claude_client.messages.create(
        model='claude-3-5-sonnet-latest',
        max_tokens=100,
        messages=[{'role': 'user', 'content': 'test'}],
        tools=[{'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': 1}]
    )
    print('✓ Web search tool accepted')
except Exception as e:
    print(f'✗ Web search tool error: {str(e)[:300]}')
