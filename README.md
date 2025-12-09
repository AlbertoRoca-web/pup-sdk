---
title: "Pup SDK - Alberto the Code Puppy"
emoji: ""
colorFrom: "purple"
colorTo: "pink"
sdk: "docker"
app_port: 7860
license: "mit"
short_description: " Alberto the code puppy - your sassy coding assistant!"
---

# 🐕 Alberto - Your Code Puppy!

Welcome to Alberto's HuggingFace Space! This is a mobile-friendly web interface for Alberto the code puppy.

## 🚀 What is Alberto?

Alberto is a sassy, helpful AI code assistant who can help you with:
- 💻 Writing and debugging code
- 📁 File operations
- 🔍 Code search
- 🎯 Shell commands
- 🤖 Natural conversation

## 📱 Try it out!

Just start chatting with Alberto! He's ready to help with any coding questions or tasks.

## 🛠️ Technical Details

This deployment uses:\- FastAPI backend
- TailwindCSS frontend
- Docker containerization
- HuggingFace Spaces
- Mobile-responsive design

## 🏃‍♂️ Run Alberto locally (real keys)

To run the same image as HuggingFace Spaces but with real API keys (not demo mode):

```bash
docker run -it -p 7860:7860 --platform=linux/amd64 \n  -e OPEN_API_KEY="YOUR_OPEN_API_KEY" \n  -e SYN_API_KEY="YOUR_SYN_API_KEY" \n  registry.hf.space/albertoroca96-web-pup-sdk:latest
```

This starts the official HuggingFace image but with your real keys, so Alberto will have full functionality instead of running in demo mode.

## 🌩️ Cloudflare Worker backend (keep keys off HuggingFace)

You can point the HuggingFace UI at the lightweight Cloudflare Worker in `src/worker.mjs`:

1. Install Wrangler and deploy the worker:
   ```bash
   npm install -g wrangler
   cd pup-sdk
   wrangler deploy
   ```
2. In Cloudflare, add your `OPEN_API_KEY` (and/or `SYN_API_KEY`) as Worker secrets:
   ```bash
   wrangler secret put OPEN_API_KEY
   wrangler secret put SYN_API_KEY   # optional fallback
   ```
3. Copy the Worker URL (e.g. `https://pup-sdk.your-name.workers.dev`).
4. In HuggingFace Space settings set `ALBERTO_API_URL` to that Worker URL. No API key is required on HuggingFace anymore—the Worker keeps the secrets server-side.

### Cloudflare Access ⚠️
If you enable Cloudflare Access on the Worker URL, HuggingFace must present an Access token. You have two choices:

- **Disable Cloudflare Access** for that Worker route (easiest) so the Space can reach it directly.
- **Or** create a service token in Zero Trust and set these environment variables in HuggingFace:
  - `PUP_CF_ACCESS_CLIENT_ID`
  - `PUP_CF_ACCESS_CLIENT_SECRET`

The Pup SDK automatically attaches those headers to every backend call. (You can also provide a raw JWT via `PUP_CF_ACCESS_JWT`.)

The updated PupClient automatically leaves demo mode whenever it sees a non-local backend URL, so the UI will start streaming real responses through your Worker as soon as the environment variable is saved and the Worker is reachable.

## 🛠️ Technical Details

This deployment uses:
- FastAPI backend
- TailwindCSS frontend (Vite build pipeline)
- Docker containerization (multi-stage build)
- HuggingFace Spaces
- Mobile-responsive design

## 🎨 Tailwind / Frontend

The frontend uses TailwindCSS with a Vite build pipeline:

### Development
1. Install Node.js dependencies:
   ```bash
   npm install
   ```

2. Start development server (live reload):
   ```bash
   npm run dev
   ```
3. Run the Python backend:
   ```bash
   python -m pup_sdk.web
   ```

### Production Build
1. Build Tailwind CSS:
   ```bash
   npm run build
   ```
2. The compiled CSS will be in `pup_sdk/web/static/style.css`
3. Docker builds automatically include this step

### File Structure
- `frontend/style.css` - Tailwind input file
- `vite.config.js` - Vite configuration
- `tailwind.config.js` - Tailwind configuration
- `pup_sdk/web/static/` - Compiled assets

## 🔗 Links

- **GitHub Repository**: https://github.com/AlbertoRoca-web/pup-sdk
- **HuggingFace Space**: https://huggingface.co/spaces/AlbertoRoca96-web/pup-sdk
- **GitHub Pages**: https://albertoroca-web.github.io/pup-sdk/

## 🐛 Understanding HTTP Status Codes

### HTTP 304 - Cache Revalidation (Normal!)

You may see `304 Not Modified` responses for:
- `inner.html`
- `out-*.js`
- `/static/style.css`

**What this means**: Browser has cached the resource and server confirms it's unchanged.

**This is NOT an error** - it's browser optimization working correctly! Your FastAPI app cannot and should not try to turn these into 200 responses. 304 means "use your cached copy" which is faster and more efficient.

### HTTP 202 - HuggingFace Telemetry (Normal!)

You may see `202 Accepted` responses for:
- `/api/event`
- `/telemetry`
- `/metrics`
- `/live`

**What this means**: These are HuggingFace's analytics/telemetry endpoints, NOT part of your FastAPI app.

**This is NOT an error** - 202 means "Accepted" (request queued for async processing). This is HuggingFace infrastructure you cannot modify.

## 🐛 Debugging Network Requests

When debugging your app in Chrome DevTools:

1. **Filter for your app**: `albertoroca96-web-pup-sdk.hf.space`
2. **Focus on these endpoints**:
   - `/` (should be 200)
   - `/api/status` (should be 200)
   - `/api/chat` (should be 200)
   - `/static/style.css` (should be 200 or 304, both fine)
   - `htmx.min.js` (should be 200)

3. **Real problems to fix**: Look for 4xx or 5xx status codes on YOUR endpoints
4. **Expected noise**: 202/304 entries can be ignored - they're telemetry and caching working normally

**Pro tip**: Hide expected responses to focus on real errors:
```
-method:OPTIONS -status-code:202 -status-code:304
```

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details.🐶 Testing Pointkedex pattern deploy workflow - $(date)" 
