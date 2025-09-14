# 🔧 VSCode Terminal Fix Guide

## 🚨 **Issue:** Shell Integration Unavailable

The error "Shell Integration Unavailable" means VSCode can't properly communicate with your terminal shell.

## 🛠️ **Step-by-Step Fix:**

### **1. Update VSCode (Most Important)**
```
Press: CMD/CTRL + Shift + P
Type: "Update"
Select: "Code: Check for Updates"
Install any available updates and restart VSCode
```

### **2. Set Default Terminal Profile**
```
Press: CMD/CTRL + Shift + P
Type: "Terminal: Select Default Profile"
Choose one of these supported shells:
- zsh (recommended for macOS)
- bash
- fish
- PowerShell
```

### **3. For macOS Users (Your System):**
Since you're on macOS, zsh should be your default. Try this:

```
Press: CMD/CTRL + Shift + P
Type: "Terminal: Select Default Profile"
Select: "zsh"
```

### **4. Reset Terminal Settings**
```
Press: CMD/CTRL + Shift + P
Type: "Preferences: Open Settings (JSON)"
Add or modify these settings:
```

```json
{
  "terminal.integrated.defaultProfile.osx": "zsh",
  "terminal.integrated.shellIntegration.enabled": true,
  "terminal.integrated.shellIntegration.decorationsEnabled": "both",
  "terminal.integrated.shellIntegration.history": 100
}
```

### **5. Restart Terminal**
```
Press: CMD/CTRL + Shift + P
Type: "Terminal: Kill All Terminals"
Then open a new terminal: CMD/CTRL + `
```

### **6. Alternative: Use External Terminal**
If VSCode terminal still doesn't work:
```
Press: CMD/CTRL + Shift + P
Type: "Terminal: Open in External Terminal"
This will open your system's default terminal app
```

### **7. Check Shell Path**
Open a new terminal and run:
```bash
echo $SHELL
```
Should show: `/bin/zsh` or `/bin/bash`

If it shows something else, set it manually:
```bash
chsh -s /bin/zsh
```

### **8. Reload VSCode Window**
```
Press: CMD/CTRL + Shift + P
Type: "Developer: Reload Window"
```

## 🧪 **Test Your Terminal:**

After following the steps above, test your terminal:

### **Test 1: Basic Commands**
```bash
pwd
ls -la
echo "Terminal working!"
```

### **Test 2: Python Environment**
```bash
cd /Users/ritwikvats/rca-agent
source .venv/bin/activate
python --version
```

### **Test 3: Git Commands**
```bash
git status
git log --oneline -5
```

## 🔍 **If Still Not Working:**

### **Option A: Use iTerm2 (macOS)**
1. Download iTerm2 from https://iterm2.com/
2. Install and set as default terminal
3. In VSCode settings, set external terminal to iTerm2

### **Option B: Reset VSCode Completely**
1. Close VSCode
2. Delete VSCode settings:
   ```bash
   rm -rf ~/Library/Application\ Support/Code/User/settings.json
   ```
3. Restart VSCode and reconfigure

### **Option C: Use Built-in Terminal App**
1. Open Spotlight (CMD + Space)
2. Type "Terminal"
3. Use the built-in Terminal app for commands

## 🎯 **Quick Test Commands for RCA Agent:**

Once your terminal is working, test these:

```bash
# Navigate to project
cd /Users/ritwikvats/rca-agent

# Activate Python environment
source .venv/bin/activate

# Test Linear API
python test_linear_ticket.py

# Check git status
git status

# Test RCA CLI
python -m rca.cli --help
```

## ✅ **Success Indicators:**

Your terminal is fixed when you can:
- ✅ See command output in VSCode terminal
- ✅ Run Python commands without errors
- ✅ Navigate directories with `cd`
- ✅ See git status and logs
- ✅ Activate virtual environments

## 🆘 **Still Having Issues?**

If none of the above works:

1. **Check VSCode Version:** Should be latest (1.80+)
2. **Check macOS Version:** Should be compatible
3. **Try Safe Mode:** Start VSCode with `--disable-extensions`
4. **Reinstall VSCode:** Download fresh copy from https://code.visualstudio.com/

## 📞 **Alternative Solutions:**

While fixing terminal, you can still:
- Use the browser URLs I provided for testing
- Use external terminal apps
- Use online tools like Repl.it for Python testing
- Use GitHub Codespaces for cloud development

---

**Follow these steps in order, and your terminal should be working again!**
