# Vercel Linear API Integration Fix

## Issue Identified
The dashboard is still showing JSON tickets instead of Linear links because:

1. ✅ **API Fixed:** The Vercel API at `api/index.py` now uses real LinearClient
2. ❌ **Environment Missing:** Vercel deployment doesn't have LINEAR_API_KEY environment variable
3. ❌ **Dependencies Missing:** Vercel may not have all required dependencies for LinearClient

## Root Cause
When the dashboard calls `/api/ticket`, the Vercel API tries to:
1. Import `LinearClient` from `rca.linear_client` 
2. Initialize LinearClient (which needs LINEAR_API_KEY from environment)
3. Call `linear_client.create_ticket()`

But since LINEAR_API_KEY is not set in Vercel environment, it falls back to mock tickets.

## Solution Options

### Option 1: Add Environment Variable to Vercel (Recommended)
```bash
# In Vercel dashboard, add environment variable:
LINEAR_API_KEY=lin_api_[your_key_here]
```

### Option 2: Simplified API Response (Quick Fix)
Modify the API to return a more informative response about the Linear integration status.

### Option 3: Hybrid Approach
Keep the real Linear integration but improve the fallback messaging.

## Current API Behavior
```javascript
// Dashboard calls:
fetch('/api/ticket', {
    method: 'POST',
    body: JSON.stringify({
        incident_file: 'incidents/TCK-1001.json',
        team: 'RIT'
    })
})

// API tries LinearClient but fails due to missing env var
// Falls back to mock response:
{
    "status": "success",
    "ticket_id": "FTS-123", 
    "ticket_url": "https://linear.app/team/issue/FTS-123",
    "type": "mock",
    "message": "Created mock ticket (Error: ...)"
}
```

## Recommended Fix
Add the LINEAR_API_KEY to Vercel environment variables so the real Linear integration works.

## Alternative: Improve Mock Response
If we can't add the environment variable, we should at least make the mock response more realistic and informative.

---
**Status:** Issue identified, solution ready to implement
