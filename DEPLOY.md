# 🚀 Deploy Your RCA Agent to Get a Public URL

## Quick Deployment Options

### Option A: Vercel (Recommended - 2 minutes)
1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "New Project"
   - Import your `rca-agent` repository
   - Click "Deploy"
   - Get your URL: `https://rca-agent-[random].vercel.app`

### Option B: Netlify (2 minutes)
1. **Push to GitHub** (same as above)
2. **Deploy to Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Sign in with GitHub
   - Click "New site from Git"
   - Choose your `rca-agent` repository
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `web`
   - Click "Deploy site"
   - Get your URL: `https://[random-name].netlify.app`

### Option C: Replit (1 minute)
1. **Go to [replit.com](https://replit.com)**
2. **Create new Repl:**
   - Click "Create Repl"
   - Choose "Import from GitHub"
   - Enter your repository URL
   - Click "Import from GitHub"
3. **Run your project:**
   - Click "Run" button
   - Get your URL: `https://rca-agent.[username].repl.co`

### Option D: Railway (After CLI installs)
1. **Login to Railway:**
   ```bash
   railway login
   ```
2. **Deploy:**
   ```bash
   railway up
   ```
3. **Get your URL:** Railway will provide a public URL

## Your Project is Ready!

✅ **Railway configuration:** `railway.toml` created
✅ **Procfile:** Created for platform deployment
✅ **Requirements:** All dependencies listed
✅ **Git repository:** Ready for deployment

## Share Your URL

Once deployed, you'll get a public URL like:
- `https://your-app.vercel.app/web/index.html`
- `https://your-app.netlify.app/web/index.html`
- `https://your-app.repl.co/web/index.html`

**Share this URL with your friend and they can access your RCA Agent from anywhere!**

## Features Your Friend Will See

🎯 **Interactive Dashboard** - Click buttons to run RCA operations
📊 **Real-time Results** - See API responses and generated documents
📁 **Download Artifacts** - PDFs, Markdown files, tickets
⚡ **One-Click Demo** - Complete RCA pipeline demonstration
📚 **API Documentation** - Technical details at `/docs`

Your RCA Agent is production-ready and shareable! 🎉
