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

## 📄 License

MIT License - see the [LICENSE](LICENSE) file for details."🐶 Testing Pointkedex pattern deploy workflow - $(date)" 
