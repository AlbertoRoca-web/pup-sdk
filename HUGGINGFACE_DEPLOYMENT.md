# 🤗 HuggingFace Spaces Deployment Guide

## 🚀 One-Click Deployment

The pup-sdk is now **fully HuggingFace Spaces ready**! Here's how to deploy:

### **Option 1: GitHub Integration (Easiest)**

1. **Go to HuggingFace Spaces**: https://huggingface.co/spaces
2. **Click "Create new Space"**
3. **Choose "Git"** and connect your GitHub account
4. **Select the `AlbertoRoca-web/pup-sdk` repository**
5. **Set Space name** (e.g., "alberto-code-puppy")
6. **Choose Python as SDK**
7. **Cost: Free CPU** (or upgrade for more power)
8. **Click "Create Space"**

**That's it! 🎉** Your Space will automatically build and deploy!

### **Option 2: Manual Deployment**

1. Clone the repo to your Space:
```bash
git clone https://github.com/AlbertoRoca-web/pup-sdk .
```

2. The Space will automatically detect `app.py` and `requirements.txt`
3. Wait for build to complete
4. Your Alberto web interface will be live!

## ⚙️ Configuration Options

### **Environment Variables**

In your Space settings, you can configure:

```
ALBERTO_API_URL=http://localhost:8080    # Where Alberto bridge server runs
ALBERTO_API_KEY=                        # Optional API key
ALBERTO_TIMEOUT=60                      # Request timeout
HOST=0.0.0.0                           # Network interface
PORT=7860                              # Port (HuggingFace sets this automatically)
DEBUG=false                            # Production mode
LOG_LEVEL=info                         # Logging verbosity
```

### **Connecting to Real Alberto**

Your Space will work **immediately in demo mode**. To connect to the real Alberto:

1. **Run the bridge server** somewhere (could be your local machine or cloud):
```bash
git clone https://github.com/AlbertoRoca-web/pup-sdk
cd pup-sdk
python bridge_server.py
```

2. **Set the ALBERTO_API_URL** in your Space settings to point to your bridge server
3. **Restart your Space** to connect!

### **Cloudflare Worker option (no keys on HuggingFace)**

Prefer to keep your LLM keys off HuggingFace entirely? Use the bundled Worker:

1. Deploy the worker:
   ```bash
   npm install -g wrangler
   cd pup-sdk
   wrangler deploy
   ```
2. Store your provider keys as Worker secrets:
   ```bash
   wrangler secret put OPEN_API_KEY
   wrangler secret put SYN_API_KEY   # optional
   ```
3. Copy the Worker URL (e.g. `https://pup-sdk-demo.workers.dev`).
4. Set `ALBERTO_API_URL` in your Space to that URL.

#### Cloudflare Access note
If you flip on Cloudflare Access for that Worker, HuggingFace will see HTTP 403 and the UI will fall back to demo mode. Either:

- Disable Access for the Worker route, **or**
- Create a Zero Trust service token and set these HuggingFace env vars so the Pup SDK can authenticate:
  - `PUP_CF_ACCESS_CLIENT_ID`
  - `PUP_CF_ACCESS_CLIENT_SECRET`

(Advanced: you can also set `PUP_CF_ACCESS_JWT` if you issue JWTs yourself.)

#### DNS override note
Some HuggingFace regions can’t resolve `*.workers.dev`. Add:
```
PUP_RESOLVE_OVERRIDES=pup-sdk.alroca308.workers.dev=104.21.50.6
```
(Comma separate multiple entries.) The resolver will short-circuit DNS but still present the correct hostname for TLS.

Because the backend URL is non-local, the updated PupClient automatically switches out of demo mode even without a HuggingFace API key, *as long as the Worker is reachable with or without Cloudflare Access protection*.

## 🌟 Features Available

### **Demo Mode (Works Out of the Box)**
- ✅ Mobile-friendly chat interface
- ✅ Beautiful dark/light mode toggle
- ✅ Responsive design for phones/tablets
- ✅ Sample Alberto responses
- ✅ Connection status indicators

### **Full Mode (With Bridge Server)**
- ✅ Real Alberto responses
- ✅ File operations
- ✅ Shell command execution
- ✅ Code search
- ✅ Agent invocation
- ✅ All Alberto capabilities

## 📱 Mobile Features

Your deployed Space will be:
- **PWA-ready** - Can be installed as mobile app
- **Touch-optimized** - Great finger targets and gestures
- **Mobile-first** - Designed for phones first
- **Offline-capable** - Works with cached responses in demo mode

## 🔧 Customization

### **Custom Branding**
Edit these files to customize:
- `pup_sdk/web/templates/index.html` - UI and styling
- `pup_sdk/web/app.py` - API endpoints and logic
- `README.md` - Space metadata and description

### **Add New Features**
The SDK is modular - you can easily add:
- New chat endpoints
- File upload/download
- Real-time notifications
- Authentication systems
- Custom integrations

## 🚀 Advanced Deployment

### **Custom Domain**
1. Go to your Space settings
2. Add custom domain
3. Point DNS to HuggingFace
4. Alberto gets his own domain! 🎉

### **Multi-User Mode**
For multiple users with different bridge servers:
1. Add user authentication
2. Store individual ALBERTO_API_URL per user
3. Support multiple Alberto instances

### **Scaling**
- **Free tier**: 1 CPU, 512MB RAM (great for demo mode)
- **Basic tier**: 2 CPUs, 8GB RAM (for light usage)
- **Enterprise**: Custom resources (for teams)

## 🤝 Troubleshooting

### **Common Issues**

**Space won't build:**
- Check `requirements.txt` has no conflicts
- Ensure `app.py` exists and is valid
- Check for syntax errors in Python files

**Demo mode not working:**
- Check Space logs in HuggingFace interface
- Ensure all files uploaded correctly
- Verify app.py startup sequence

**Can't connect to Alberto:**
- Check ALBERTO_API_URL environment variable
- Ensure bridge server is running
- Check firewall/network settings
- Verify endpoint accessibility from HuggingFace

### **Logs and Debugging**
View real-time logs in your HuggingFace Space dashboard.

## 🎉 Success!

Once deployed, you'll have:
- 🌐 Public web interface for Alberto
- 📱 Mobile app accessible from any device
- 🔗 Shareable link for anyone to try Alberto
- 🚀 Zero-maintenance deployment
- 💡 Perfect demo for Alberto capabilities

**Your Alberto is now available to the world! 🌍🐕**

---

Need help? Check the [GitHub Issues](https://github.com/AlbertoRoca-web/pup-sdk/issues) or create a new one!