import asyncio
import os

async def main():
    try:
        from pup_sdk.web.app import create_app
        print('Creating FastAPI app...')
        app = create_app()
        print('App created successfully')
        
        print('Client exists:', hasattr(app.state, 'client'))
        if hasattr(app.state, 'client') and app.state.client:
            print('Demo mode:', app.state.client.demo_mode)
            print('Is connected:', app.state.client.is_connected)
            print('Has API key:', bool(app.state.client.api_key))
        else:
            print('No client in app.state')
        
        print('\nTesting status endpoint...')
        from fastapi.testclient import TestClient
        client = TestClient(app)
        response = client.get('/api/status')
        print('Status response:', response.json())
        
    except Exception as e:
        print('Exception:', e)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())