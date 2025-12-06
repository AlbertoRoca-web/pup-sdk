import os
from pup_sdk.client import PupClient

# Configuration
SPACE_URL = "https://albertoroca96-web-pup-sdk.hf.space"
API_KEY = os.getenv("OPEN_API_KEY")
MODEL = "gpt-4o-mini"

print("🐶 Connecting Alberto the Code Puppy...")
print(f"🔗 Space URL: {SPACE_URL}")
print(f"🤖 Model: {MODEL}")
print(f"🔑 API Key: {'✅ Set' if API_KEY else '❌ Missing'}")

if not API_KEY:
    print("❌ Error: OPEN_API_KEY environment variable is not set!")
    print("💡 Run: export OPEN_API_KEY=your_api_key_here")
    exit(1)

try:
    # Create PupClient instance
    client = PupClient(space_url=SPACE_URL)
    
    # Connect to Alberto
    print("🔄 Establishing connection...")
    response = client.connect(api_key=API_KEY, model=MODEL)
    
    print("✅ Connection successful!")
    print(f"📝 Response: {response}")
    
    # Optionally send a test message
    print("🧪 Sending test message...")
    test_response = client.send_message("Hello Alberto! Can you help me write code?")
    print(f"💬 Test response: {test_response}")
    
except Exception as e:
    print(f"❌ Error connecting to Alberto: {e}")
    print("🔍 Check if:")
    print("   • The Space is running: https://huggingface.co/spaces/AlbertoRoca96-web/pup-sdk")
    print("   • Your OPEN_API_KEY is valid")
    print("   • Network connectivity is working")