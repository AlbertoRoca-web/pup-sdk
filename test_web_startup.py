import asyncio
import os
import sys
from contextlib import asynccontextmanager

async def test_startup():
    """Test the web app startup logic directly"""
    print('=== Testing Web App Startup ===')
    
    try:
        # Set test environment
        os.environ['OPEN_API_KEY'] = 'sk-test123startup'
        os.environ['SYN_API_KEY'] = ''
        
        # Import and test the lifespan logic
        sys.path.insert(0, '.')
        from pup_sdk.web.app import create_app
        from fastapi import FastAPI
        
        print('Creating app...')
        app = create_app()
        
        # Simulate the lifespan startup
        print('Simulating lifespan startup...')
        from pup_sdk.web.app import lifespan
        from pup_sdk.client import PupClient
        
        async with app as test_app:
            print('App started successfully')
            
            # Check if client was created
            client = getattr(test_app.state, 'client', None)
            if client:
                print(f'✅ Client created: demo_mode={client.demo_mode}, is_connected={client.is_connected}')
                print(f'✅ Has API key: {bool(client.api_key)}')
            else:
                print('❌ No client created')
                
            return True
            
    except Exception as e:
        print(f'❌ Startup failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_startup())
    print(f'Test result: {"PASSED" if success else "FAILED"}')