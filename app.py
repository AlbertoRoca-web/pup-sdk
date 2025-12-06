"""FastAPI app for Alberto the Code Puppy HuggingFace Space."""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import random
import asyncio

# Create FastAPI app
app = FastAPI(
    title="Alberto - Code Puppy",
    description="🐕 Your sassy code puppy assistant!",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Alberto's personality and responses
alberto_responses = {
    "greeting": [
        "🐕 Woof woof! Hey there! I'm Alberto, your favorite code puppy! 🐶",
        "🐶 Hey! Alberto here, ready to help you with all things coding! 🎉",
        "🐾 Woof! Alberto at your service! What coding adventures await? 🚀",
    ],
    "help": [
        "🐕 I can help you with: 📄 File operations, 💻 Shell commands, 🔍 Code search, 🐍 Python/JS coding, 🌐 Web development, and so much more! Just ask me anything! 🐾",
        "🐶 My superpowers include: debugging code, writing functions, running commands, searching files, explaining concepts, and being ridiculously helpful! What do you need? 🎯",
        "🐕 Alberto to the rescue! I can: write code, fix bugs, run commands, search files, explain stuff, and make coding fun! What's our mission today? 🚀",
    ],
    "joke": [
        "🐕 Why do programmers prefer dark mode? ☀️🌙 Because light attracts bugs! 🐛😂 Get it? Like actual bugs? Ok I'll stick to coding...",
        "🐶 How many programmers does it take to change a lightbulb? None! That's a hardware problem! 💡😂",
        "🐾 Why did the programmer quit his job? Because he didn't get arrays! 💻😅 (I'm here all week!)",
    ],
    "coding": [
        "🐍 Python? My favorite! I can help you with functions, classes, APIs, Django, FastAPI, debugging, and best practices! What specific Python magic do you need? 🐍✨",
        "💻 Shell commands? I can execute them safely! Just tell me what you want to run - I'll show you output and any errors. Like `ls -la` or `python script.py`! 🚀",
        "📁 Files? I can read, write, list, search through them! Just point me to the directory or file and let's work some file magic! 🗂️✨",
    ],
    "default": [
        "🐕 Woof! That's interesting! I'd love to help you with that. Tell me more about what you're trying to accomplish! 🐾",
        "🐶 Hmm, let me think about that... I'm here to help with coding and tech stuff! What specific challenge are you facing? 🤔",
        "🐾 Oh! Interesting question! I'm all about coding, debugging, and making tech awesome. How can I assist you today? 🎯",
    ]
}

def get_alberto_response(message: str) -> str:
    """Generate Alberto's response based on message content."""
    message_lower = message.lower()
    
    # Greeting patterns
    if any(word in message_lower for word in ["hello", "hi", "hey", "wo", "woof"]):
        return random.choice(alberto_responses["greeting"])
    
    # Help patterns
    elif any(word in message_lower for word in ["help", "what can", "capabilities", "features"]):
        return random.choice(alberto_responses["help"])
    
    # Joke patterns
    elif any(word in message_lower for word in ["joke", "funny", "laugh", "humor"]):
        return random.choice(alberto_responses["joke"])
    
    # Coding patterns
    elif any(word in message_lower for word in ["python", "code", "file", "command", "run", "shell", "search"]):
        return random.choice(alberto_responses["coding"])
    
    # Default responses
    else:
        return random.choice(alberto_responses["default"])

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐕 Alberto - Your Code Puppy!</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .typing-indicator::after {
            content: '.';
            animation: typing 1.5s steps(3, end) infinite;
        }
        @keyframes typing {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }
        .message-appear {
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .paw-bg {
            background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Cpath d='M20 20c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm10 0c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10z'/%3E%3C/g%3E%3C/svg%3E");
        }
    </style>
</head>
<body class="bg-gradient-to-br from-purple-50 to-indigo-100 min-h-screen paw-bg">
    <div class="container mx-auto px-4 py-6 max-w-4xl">
        <!-- Header -->
        <header class="text-center mb-6">
            <div class="inline-flex items-center gap-2 mb-4">
                <span class="text-4xl">🐕</span>
                <h1 class="text-3xl font-bold text-gray-800">Alberto</h1>
                <span class="text-4xl">🐕</span>
            </div>
            <p class="text-gray-600">Your sassy code puppy - here to help you code! 🐾</p>
            <div class="mt-2 flex justify-center gap-4">
                <span class="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                    🟢 HuggingFace Space
                </span>
                <span class="px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                    👌 Demo Mode Active
                </span>
            </div>
        </header>

        <!-- Chat Messages Container -->
        <div id="chat-container" class="bg-white rounded-lg shadow-lg p-4 mb-4 h-96 overflow-y-auto">
            <div id="messages" class="space-y-3">
                <!-- Welcome Message -->
                <div class="flex gap-3 message-appear">
                    <div class="text-2xl flex-shrink-0">🐕</div>
                    <div class="flex-1">
                        <div class="bg-purple-100 rounded-lg p-3 max-w-[90%]">
                            <p class="text-gray-800 text-sm">
                                🐕 Woof! Hey there! I'm Alberto, your favorite code puppy! 🦮<br><br>
                                I'm running on HuggingFace Spaces in demo mode, but I can still chat with you!<br><br>
                                Ask me anything about coding, tell me a joke, or just say hello! 🎩
                            </p>
                        </div>
                        <div class="text-xs text-gray-500 mt-1">Alberto • Just now</div>
                    </div>
                </div>
            </div>
            <div id="typing-indicator" class="hidden">
                <div class="flex gap-3">
                    <div class="text-2xl flex-shrink-0">🐕</div>
                    <div class="bg-gray-100 rounded-lg p-3 typing-indicator">
                        Thinking
                    </div>
                </div>
            </div>
        </div>

        <!-- Input Form -->
        <form id="chat-form" class="mb-4">
            <div class="flex gap-2">
                <input 
                    type="text" 
                    id="message-input" 
                    placeholder="What do you want to chat about?" 
                    class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    autocomplete="off"
                    required
                >
                <button 
                    type="submit" 
                    id="send-button"
                    class="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    Send 👌
                </button>
            </div>
        </form>

        <!-- Quick Actions -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
            <button onclick="sendQuickMessage('What can you do?')" class="px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
                🤔 What can you do?
            </button>
            <button onclick="sendQuickMessage('Tell me a joke')" class="px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
                😄 Tell me a joke
            </button>
            <button onclick="sendQuickMessage('Help me with Python')" class="px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
                🐍 Python help
            </button>
            <button onclick="sendQuickMessage('Hello Alberto!')" class="px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 text-sm">
                👋 Say hello
            </button>
        </div>

        <!-- Info Section -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="font-semibold text-blue-900 mb-2">📱 HuggingFace Space Demo:</h3>
            <ul class="text-sm text-blue-800 space-y-1">
                <li>• 🐕 This is Alberto running on HuggingFace Spaces!</li>
                <li>• 🎩 Currently in demo mode with sample responses</li>
                <li>• 💬 Try the quick action buttons or type a message!</li>
                <li>• 🚫 Mobile-friendly - works great on phones!</li>
                <li>• 🔎 Try asking me about coding, jokes, or just chat!</li>
            </ul>
        </div>
    </div>

    <script>
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('chat-form');
            const input = document.getElementById('message-input');
            
            form.addEventListener('submit', handleSubmit);
            input.focus();
        });
        
        async function handleSubmit(e) {
            e.preventDefault();
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            await sendMessage(message);
            input.value = '';
            input.focus();
        }
        
        async function sendMessage(message) {
            // Add user message
            addMessage(message, 'user');
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                hideTypingIndicator();
                
                addMessage(data.response, 'alberto');
            } catch (error) {
                hideTypingIndicator();
                addMessage('Oops! Something went wrong. Try again!', 'alberto');
            }
        }
        
        function sendQuickMessage(message) {
            document.getElementById('message-input').value = message;
            document.getElementById('chat-form').dispatchEvent(new Event('submit'))
        }
        
        function addMessage(content, sender) {
            const messagesContainer = document.getElementById('messages');
            const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            
            const messageHtml = `
                <div class="flex gap-3 message-appear ${sender === 'user' ? 'justify-end' : ''}">
                    ${sender === 'alberto' ? '<div class="text-2xl flex-shrink-0">🐕</div>' : ''}
                    <div class="flex-1 ${sender === 'user' ? 'text-right' : ''}">
                        <div class="${sender === 'user' ? 'bg-indigo-100 ml-auto' : 'bg-purple-100'} rounded-lg p-3 max-w-[90%] inline-block">
                            <p class="text-gray-800 text-sm">${escapeHtml(content)}</p>
                        </div>
                        <div class="text-xs text-gray-500 mt-1">${sender === 'user' ? 'You' : 'Alberto'} • ${timestamp}</div>
                    </div>
                    ${sender === 'user' ? '<div class="text-2xl flex-shrink-0">👤</div>' : ''}
                </div>
            `;
            
            messagesContainer.insertAdjacentHTML('beforeend', messageHtml);
            scrollToBottom();
        }
        
        function showTypingIndicator() {
            document.getElementById('typing-indicator').classList.remove('hidden');
            scrollToBottom();
        }
        
        function hideTypingIndicator() {
            document.getElementById('typing-indicator').classList.add('hidden');
        }
        
        function scrollToBottom() {
            const container = document.getElementById('chat-container');
            container.scrollTop = container.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
    """
    
    return HTMLResponse(content=html_content)

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Handle chat requests with Alberto's personality."""
    import json
    
    try:
        body = await request.json()
        message = body.get('message', '')
        
        if not message:
            return {"response": "Hey! I'd love to chat, but you need to say something! 🐾"}
        
        # Generate Alberto's response
        response = get_alberto_response(message)
        
        return {
            "response": response,
            "timestamp": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        return {
            "response": "Woof! Something went wrong, but I'm still here to help! 🐕 Try again!",
            "error": str(e)
        }

@app.get("/api/status")
async def status_endpoint():
    """Get Alberto's status."""
    return {
        "status": "healthy",
        "mode": "demo",
        "platform": "huggingface-spaces",
        "alberto_available": True,
        "capabilities": ["chat", "jokes", "coding_help", "personality"]
    }

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)