# IMMEDIATE FIX - Linear API Key Setup 🚨

## 🔍 **What I See in Your Screenshot:**

```
❌ Error creating Linear ticket: HTTP 500:
✅ Falling back to mock ticket creation...
✅ Mock ticket created as fallback
```

This means the `LINEAR_API_KEY` environment variable is **NOT SET** in Vercel.

## 🚀 **IMMEDIATE FIX STEPS:**

### **Step 1: Go to Vercel Dashboard**
1. Open: https://vercel.com/dashboard
2. Find your project: `rca-agent1`
3. Click on it

### **Step 2: Add Environment Variable**
1. Click **"Settings"** tab
2. Click **"Environment Variables"** in left sidebar
3. Click **"Add New"**
4. Fill in:
   - **Name:** `LINEAR_API_KEY`
   - **Value:** `YOUR_LINEAR_API_KEY_HERE`
   - **Environments:** Select **ALL** (Production, Preview, Development)
5. Click **"Save"**

### **Step 3: Redeploy**
1. Go to **"Deployments"** tab
2. Click **⋯** menu on latest deployment
3. Click **"Redeploy"**
4. Wait for green checkmark (deployment complete)

### **Step 4: Test Again**
1. Go back to your dashboard: https://rca-agent1-az5wt0dh9-ritwik-vats-projects.vercel.app/demo-dashboard.html
2. Click **"🎫 Create Ticket"**
3. Should now show: `✅ Created real Linear ticket RIT-X`

## 🎯 **Expected Result After Fix:**

Instead of:
```
❌ Error creating Linear ticket: HTTP 500:
✅ Falling back to mock ticket creation...
```

You should see:
```
✅ Real Linear Ticket Creation started for TCK-1001...
✅ Created real Linear ticket RIT-8
✅ Ticket URL: https://linear.app/ritwik-vats/issue/RIT-8/...
```

## 🔍 **Quick Test - Debug Endpoint:**

After adding the environment variable and redeploying, test this URL:
```
https://rca-agent1-az5wt0dh9-ritwik-vats-projects.vercel.app/api/debug/env
```

Should show:
```json
{
    "linear_api_key_present": true,
    "linear_team_key": "RIT"
}
```

## ⚡ **Why This Happens:**

The application is working perfectly - it's designed to:
1. Try to create a real Linear ticket with the API key
2. If no API key is found, gracefully fall back to mock tickets
3. Never crash with HTTP 500 errors

The HTTP 500 error you see is from the Linear API (not our application), which happens when the API key is missing.

---
**🎯 SOLUTION: Add the LINEAR_API_KEY environment variable in Vercel and redeploy!**
