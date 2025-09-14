# Vercel Environment Setup for Linear Integration

## Quick Fix: Add Linear API Key to Vercel

### Step 1: Get Your Linear API Key
1. Go to https://linear.app/settings/api
2. Create a new API key if you don't have one
3. Copy the key (starts with `lin_api_`)

### Step 2: Add Environment Variable to Vercel
1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Find your project: `rca-agent1`
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Set:
   - **Name:** `LINEAR_API_KEY`
   - **Value:** `lin_api_[your_actual_key]`
   - **Environments:** Production, Preview, Development (check all)
6. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click **Redeploy** on the latest deployment
3. Wait for deployment to complete

### Step 4: Test
1. Visit your dashboard: https://rca-agent1-ajywzadto-ritwik-vats-projects.vercel.app/demo-dashboard.html
2. Run the workflow through "Create Ticket" step
3. You should now see a real Linear ticket instead of JSON file

## Alternative: Quick Test Without Environment Setup

If you want to test immediately without setting up Vercel environment variables, you can:

1. **Use Local Development:**
   ```bash
   # Run locally with your .env file
   source .venv/bin/activate
   python -m rca.api
   # Then visit http://localhost:8000/demo-dashboard.html
   ```

2. **Test CLI Integration:**
   ```bash
   # This works locally with your .env
   python -m rca.cli ticket incidents/TCK-1001.json --team RIT
   ```

## Expected Results After Fix

### Before (Current State)
- Dashboard shows: `TCK-1001_ticket.json` 
- Type: JSON file
- No Linear integration

### After (With Environment Variable)
- Dashboard shows: `🎫 RIT-8` (or next ticket number)
- Type: Linear Ticket with green border
- Button: "Open in Linear" → opens real ticket

## Troubleshooting

### If Still Showing JSON After Setup:
1. **Check Environment Variable:** Ensure LINEAR_API_KEY is set in Vercel
2. **Check API Key:** Verify the key works by testing locally
3. **Check Team Key:** Ensure "RIT" team exists in your Linear workspace
4. **Check Deployment:** Make sure you redeployed after adding the env var

### If Getting Errors:
1. **Check Vercel Logs:** Go to Deployments → View Function Logs
2. **Check API Response:** Use browser dev tools to see actual API response
3. **Test Locally:** Run the same API call locally to debug

## Manual Verification

You can test the API directly:

```bash
# Test the Vercel API endpoint
curl -X POST https://rca-agent1-ajywzadto-ritwik-vats-projects.vercel.app/api/ticket \
  -H "Content-Type: application/json" \
  -d '{"incident_file": "incidents/TCK-1001.json", "team": "RIT"}'
```

Expected response with environment variable:
```json
{
  "status": "success",
  "ticket_id": "RIT-8",
  "ticket_url": "https://linear.app/ritwik-vats/issue/RIT-8/...",
  "type": "real",
  "message": "Created Linear ticket RIT-8"
}
```

Expected response without environment variable:
```json
{
  "status": "success", 
  "ticket_id": "FTS-123",
  "ticket_url": "https://linear.app/team/issue/FTS-123",
  "type": "mock",
  "message": "Created mock ticket (Error: ...)"
}
```

---
**Next Steps:** Add LINEAR_API_KEY to Vercel environment variables and redeploy.
