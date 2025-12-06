# 🐕 Pup SDK

Official Python SDK for Alberto (your favorite code puppy)! Build mobile apps, web interfaces, and integrations to chat with Alberto from anywhere.

## ✨ Features

- 🚀 Full API access to Alberto's capabilities
- 📱 Mobile-friendly web interface
- 🛠️ File operations, shell commands, and more
- 🐍 Pure Python with async support
- 🌐 Ready for HuggingFace Spaces deployment
- 📚 Comprehensive documentation

## 🚀 Quick Start

```bash
pip install pup-sdk
```

```python
import asyncio
from pup_sdk import PupClient

async def main():
    client = await PupClient.connect()
    response = await client.say_woof("Hey Alberto, what's up?")
    print(response)

asyncio.run(main())
```

## 📱 Web Interface

Launch the web interface:

```python
from pup_sdk.web import launch_web

launch_web(host="0.0.0.0", port=7860)  # HuggingFace Spaces ready!
```

## 🐾 Capabilities

- 📁 File operations (read, write, list)
- 🖥️ Shell command execution
- 🔍 File search and grep
- 🎯 Agent invocation
- 📝 Code editing and refactoring

## 📚 Documentation

See the `docs/` directory for full API documentation and examples.

## 🌟 Examples

Check out the `examples/` folder for:
- Mobile web app
- CLI tool
- Discord bot
- VS Code extension

Made with 🐶 love by Alberto!