import traceback
print('Starting test...')
try:
    from pup_sdk.client import PupClient
    print('Import successful')
    client = PupClient.from_env()
    print('from_env successful')
    print('demo_mode:', client.demo_mode)
    print('is_connected:', client.is_connected)
    print('has_key:', bool(client.api_key))
except Exception as e:
    print('Exception:')
    traceback.print_exc()