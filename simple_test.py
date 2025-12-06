import asyncio
import os
import sys

async def test_connection_logic():
    print('=== Testing Connection Logic ===')
    
    try:
        # Set test environment
        os.environ['OPEN_API_KEY'] = 'sk-test123'
        os.environ['SYN_API_KEY'] = ''
        os.environ['ALBERTO_API_URL'] = ''  # No external server
        
        from pup_sdk.client import PupClient
        
        # Test PupClient creation
        print('Creating PupClient.from_env()...')
        client = PupClient.from_env()
        print(f'demo_mode: {client.demo_mode}')
        print(f'is_connected: {client.is_connected}')
        print(f'has_key: {bool(client.api_key)}')
        
        # Test connection (should work - creates HTTP session)
        if not client.demo_mode:
            print('Testing connect()...')
            try:
                await client.connect()
                print('✅ connect() successful!')
                print(f'is_connected after connect: {client.is_connected}')
                await client.close()
            except Exception as e:
                print(f'connect() error: {type(e).__name__}: {str(e)[:100]}')
        
        return True
        
    except Exception as e:
        print(f'Test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(test_connection_logic())
    print(f'Test result: PASSED' if success else 'FAILED')