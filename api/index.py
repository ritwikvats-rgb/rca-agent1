from fastapi import FastAPI
from fastapi.responses import JSONResponse
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a simple FastAPI app for Vercel
app = FastAPI(title="RCA Agent API", description="Root Cause Analysis Agent")

@app.get("/")
async def root():
    return {"message": "RCA Agent API is running", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rca-agent"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "rca-agent-api"}

# Try to import and include the main RCA routes
try:
    from rca.api import app as rca_app
    # Mount the RCA app routes
    app.mount("/api", rca_app)
except Exception as e:
    @app.get("/api/error")
    async def api_error():
        return {"error": "RCA modules not available", "details": str(e)}

# This is the entry point for Vercel
def handler(request):
    from mangum import Mangum
    handler = Mangum(app)
    return handler(request, {})
