import asyncio
import os
import sys

# Set environment for non-demo mode with OpenAI key
os.environ['OPEN_API_KEY'] = 'sk-test123'
os.environ['SYN_API_KEY'] = ''
os.environ['ALBERTO_API_URL'] = ''

async def test_lifespan():
    print('=== Testing Web App Lifespan ===')
    
    # Import after setting environment
    from pup_sdk.web.app import create_app
    from fastapi import FastAPI
    
    print('Creating FastAPI app...')
    app = create_app()
    
    # Test the lifespan manually
    from pup_sdk.web.app import lifespan
    
    print('Running lifespan...')
    async with app as test_app:
        client = getattr(test_app.state, 'client', None)
        if client:
            print(f'✅ Client in app.state:')
            print(f'   demo_mode: {client.demo_mode}')
            print(f'   is_connected: {client.is_connected}')
            print(f'   has_api_key: {bool(client.api_key)}')
            
            # Test status endpoint through the app
            from fastapi.testclient import TestClient
            test_client = TestClient(test_app)
            
            response = test_client.get('/api/status')
            print(f'📊 /api/status response: {response.json()}')
            
            # Test chat endpoint
            chat_response = test_client.post('/api/chat', json={'message': 'Hello'})
            print(f'💬 /api/chat status: {chat_response.status_code}')
            if chat_response.status_code == 200:
                print(f'Chat response: {chat_response.json()}')
            else:
                print(f'Chat error: {chat_response.json()}')
                
        else:
            print('❌ No client found in app.state')
            return False
            
    print('✅ Lifespan test completed successfully')
    return True

if __name__ == '__main__':
    try:
        success = asyncio.run(test_lifespan())
        print(f'\n✅ ALL TESTS PASSED' if success else '\n❌ TESTS FAILED')
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()