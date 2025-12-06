"""Basic usage example for Pup SDK."""

import asyncio
import sys

# Add the parent directory to the path so we can import pup_sdk
sys.path.append('..')

from pup_sdk import PupClient
from pup_sdk.exceptions import PupConnectionError, PupError


async def basic_chat_example():
    """Example of basic chat functionality."""
    print("🐕 Basic Chat Example")
    print("=" * 30)
    
    try:
        # Connect to Alberto
        client = await PupClient.connect()
        print("✅ Connected to Alberto!")
        
        # Send a message
        response = await client.say_woof(
            "Hey Alberto! What can you help me with?"
        )
        print(f"🐕 Alberto: {response.response}")
        
        # Check his status
        status = await client.get_status()
        print(f"📊 Status: Available={status.available}, Version={status.version}")
        
        await client.close()
        
    except PupConnectionError:
        print("❌ Could not connect to Alberto. Make sure he's running!")
    except PupError as e:
        print(f"❌ Error: {e}")


async def file_operations_example():
    """Example of file operations."""
    print("\n📁 File Operations Example")
    print("=" * 35)
    
    try:
        client = await PupClient.connect()
        
        # List current directory
        files = await client.list_files(".", recursive=False)
        print(f"📂 Found {len(files)} items:")
        for file_info in files[:5]:  # Show first 5
            icon = "📁" if file_info.is_directory else "📄"
            print(f"  {icon} {file_info.name}")
        
        # Read this example file
        content = await client.read_file(__file__)
        print(f"\n📄 Reading {__file__}:")
        print(f"   Size: {len(content)} characters")
        print(f"   First line: {content.split(chr(10))[0]}")
        
        await client.close()
        
    except PupConnectionError:
        print("❌ Could not connect to Alberto")
    except PupError as e:
        print(f"❌ Error: {e}")


async def shell_command_example():
    """Example of running shell commands."""
    print("\n💻 Shell Command Example")
    print("=" * 32)
    
    try:
        client = await PupClient.connect()
        
        # Run a simple command
        result = await client.run_command("echo 'Woof from the shell!'")
        print(f"🚀 Command: {result.command}")
        print(f"✅ Success: {result.success}")
        print(f"📤 Output: {result.stdout}")
        
        await client.close()
        
    except PupConnectionError:
        print("❌ Could not connect to Alberto")
    except PupError as e:
        print(f"❌ Error: {e}")


async def search_example():
    """Example of file searching."""
    print("\n🔍 Search Example")
    print("=" * 22)
    
    try:
        client = await PupClient.connect()
        
        # Search for "async" in the current directory
        results = await client.search_files("async", directory="..", max_results=5)
        print(f"🔍 Found {len(results)} results for 'async':")
        
        for result in results:
            print(f"  📄 {result.file_path}:{result.line_number}")
            print(f"     {result.line_content.strip()}")
        
        await client.close()
        
    except PupConnectionError:
        print("❌ Could not connect to Alberto")
    except PupError as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all examples."""
    print("🐕 Pup SDK Examples\n")
    
    await basic_chat_example()
    await file_operations_example()
    await shell_command_example()
    await search_example()
    
    print("\n✨ All examples completed!")
    print("💡 Try running the web interface: python -m pup_sdk.cli web")
    print("💡 Or try the CLI: python -m pup_sdk.cli chat --interactive")


if __name__ == "__main__":
    asyncio.run(main())