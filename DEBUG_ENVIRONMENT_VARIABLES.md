# Debug Environment Variables - Testing Guide 🔍

## 🎯 **Debug Endpoint Added**

I've added a debug endpoint to help us verify if the environment variable is properly set in Vercel.

## 🧪 **Testing Steps**

### **Step 1: Wait for Deployment**
The latest commit with the debug endpoint should deploy automatically to Vercel (usually takes 1-2 minutes).

### **Step 2: Test Debug Endpoint**
Visit this URL in your browser:
```
https://rca-agent1-983c06yd9-ritwik-vats-projects.vercel.app/api/debug/env
```

### **Step 3: Analyze Results**

#### **If Environment Variable is Working:**
```json
{
  "linear_api_key_present": true,
  "linear_api_key_length": 49,
  "linear_api_key_prefix": "lin_api_dm...",
  "vercel_env": "production"
}
```

#### **If Environment Variable is Missing:**
```json
{
  "linear_api_key_present": false,
  "linear_api_key_length": 0,
  "linear_api_key_prefix": null,
  "vercel_env": "production"
}
```

## 🔧 **Next Steps Based on Results**

### **If Environment Variable is Present:**
- The issue might be with the Linear API call itself
- Check the `all_env_vars` list to see what's available
- Test the ticket creation again

### **If Environment Variable is Missing:**
1. **Go back to Vercel Dashboard**
2. **Double-check Environment Variables section**
3. **Ensure the variable is saved for Production environment**
4. **Redeploy the application**

## 🎯 **Quick Test Commands**

### **Test Environment Variable:**
```bash
curl https://rca-agent1-983c06yd9-ritwik-vats-projects.vercel.app/api/debug/env
```

### **Test Ticket Creation:**
```bash
curl -X POST https://rca-agent1-983c06yd9-ritwik-vats-projects.vercel.app/api/ticket \
  -H "Content-Type: application/json" \
  -d '{"incident_file": "incidents/TCK-1001.json", "team": "RIT"}'
```

## 🔍 **Expected Behavior**

### **With Environment Variable:**
- Debug endpoint shows `linear_api_key_present: true`
- Ticket creation should return real Linear ticket
- No more "HTTP 500" errors

### **Without Environment Variable:**
- Debug endpoint shows `linear_api_key_present: false`
- Ticket creation returns mock ticket with clear message
- Still shows "Add LINEAR_API_KEY to Vercel environment"

## 📋 **Troubleshooting Matrix**

| Debug Result | Ticket Result | Action Needed |
|-------------|---------------|---------------|
| ✅ Key Present | ✅ Real Ticket | **SUCCESS** - Everything working |
| ✅ Key Present | ❌ Mock Ticket | Check Linear API permissions |
| ❌ Key Missing | ❌ Mock Ticket | Add environment variable to Vercel |
| ❌ Key Missing | ❌ HTTP 500 | Redeploy application |

## 🚀 **Test Now**

1. **Visit debug endpoint:** https://rca-agent1-983c06yd9-ritwik-vats-projects.vercel.app/api/debug/env
2. **Check if `linear_api_key_present` is `true`**
3. **If true:** Test ticket creation in dashboard
4. **If false:** Re-add environment variable in Vercel

---
**This debug endpoint will tell us exactly what's happening with the environment variable!** 🎯
