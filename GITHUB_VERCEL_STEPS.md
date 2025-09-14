# 🚀 GitHub + Vercel Deployment - Step by Step

## 📋 **PART 1: Upload to GitHub (2 minutes)**

### **Step 1: Go to GitHub**
1. Open your web browser
2. Go to **https://github.com**
3. If you don't have an account:
   - Click **"Sign up"** (top right)
   - Use your email to create free account
4. If you have an account:
   - Click **"Sign in"** (top right)
   - Enter your username/password

### **Step 2: Create New Repository**
1. Once logged in, look for a **green "New"** button (or **"+"** icon)
2. Click **"New repository"**
3. Fill in the form:
   - **Repository name:** `rca-agent`
   - **Description:** `RCA Agent - Incident Analysis Tool`
   - **Make sure it's PUBLIC** (so Vercel can access it)
   - **Don't check** "Add a README file" (we already have one)
4. Click **"Create repository"** (green button at bottom)

### **Step 3: Upload Your Files**
1. You'll see a page with instructions
2. Look for text that says **"uploading an existing file"** (it's a link)
3. Click on **"uploading an existing file"**
4. You'll see a drag-and-drop area
5. **Open your file manager** (Finder on Mac, File Explorer on Windows)
6. **Navigate to your `rca-agent` folder**
7. **Select ALL files** in the folder (Ctrl+A on Windows, Cmd+A on Mac)
8. **Drag all files** into the GitHub upload area
9. Wait for upload to complete (you'll see progress bars)
10. Scroll down and click **"Commit changes"** (green button)

**✅ Your code is now on GitHub!**

## 🌐 **PART 2: Deploy to Vercel (3 minutes)**

### **Step 4: Go to Vercel**
1. Open a new tab in your browser
2. Go to **https://vercel.com**
3. Click **"Sign Up"** (top right)
4. **IMPORTANT:** Choose **"Continue with GitHub"** (this connects your accounts)
5. Authorize Vercel to access your GitHub account

### **Step 5: Import Your Project**
1. Once logged in to Vercel, you'll see a dashboard
2. Click **"New Project"** (big button or in sidebar)
3. You'll see a list of your GitHub repositories
4. Find **"rca-agent"** in the list
5. Click **"Import"** next to it

### **Step 6: Configure Deployment**
1. Vercel will show project settings
2. **Project Name:** Leave as `rca-agent` (or change if you want)
3. **Framework Preset:** Leave as "Other" (Vercel will auto-detect)
4. **Root Directory:** Leave blank (use entire repository)
5. **Build Command:** Leave blank (we don't need to build)
6. **Output Directory:** Leave blank
7. Click **"Deploy"** (blue button)

### **Step 7: Wait for Deployment**
1. Vercel will start building your project
2. You'll see a progress screen with logs
3. Wait 1-2 minutes for deployment to complete
4. You'll see **"Congratulations!"** when done

### **Step 8: Get Your Live URL**
1. After successful deployment, you'll see your project dashboard
2. At the top, you'll see your live URL like:
   - `https://rca-agent-abc123.vercel.app`
3. **IMPORTANT:** Add `/web/index.html` to the end:
   - `https://rca-agent-abc123.vercel.app/web/index.html`
4. Click on this URL to test your site

**🎉 Your final website link is ready!**

## 🔗 **Your Final Shareable URL**

Your website will be live at:
`https://rca-agent-[random-string].vercel.app/web/index.html`

**Share this exact URL with your friend!**

## 📱 **What Your Friend Will See**

When they visit your URL:
- 🎯 **Interactive RCA Dashboard** with operation buttons
- 📊 **Real-time API responses** showing analysis results
- 📁 **Download links** for generated PDFs and reports
- ⚡ **One-click demo** button to run full pipeline
- 📚 **API documentation** at `/docs` endpoint

## 🔄 **Future Updates**

To update your website:
1. Make changes to your local files
2. Upload new files to GitHub (same process as Step 3)
3. Vercel will automatically redeploy your site
4. Your URL stays the same!

## ⚡ **Troubleshooting**

**If deployment fails:**
- Check that all files uploaded to GitHub correctly
- Make sure repository is PUBLIC
- Try deploying again from Vercel dashboard

**If website doesn't load:**
- Make sure you added `/web/index.html` to the end of URL
- Wait a few minutes for DNS to propagate
- Try opening in incognito/private browser window

**Your RCA Agent will be live and accessible worldwide!** 🌍
