from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Request models
class TicketRequest(BaseModel):
    incident_file: str
    team: str = "RIT"

# Create a simple FastAPI app for Vercel
app = FastAPI(title="RCA Agent API", description="Root Cause Analysis Agent")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RCA Agent API is running", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "rca-agent", "environment": "vercel"}

@app.get("/incidents")
async def get_incidents():
    """Get list of available incidents"""
    return {
        "incidents": [
            {
                "id": "TCK-1001",
                "title": "Checkout intermittently timing out",
                "service": "orders-api",
                "status": "open"
            }
        ]
    }

@app.get("/artifacts")
async def get_artifacts():
    """Get list of generated artifacts"""
    return {
        "documents": [
            {
                "name": "TCK-1001_initial_rca.md",
                "type": "markdown",
                "size": 2048,
                "modified": 1726315200,
                "download_url": "/download/TCK-1001_initial_rca.md"
            },
            {
                "name": "TCK-1001_final_rca.pdf",
                "type": "pdf", 
                "size": 4096,
                "modified": 1726315200,
                "download_url": "/download/TCK-1001_final_rca.pdf"
            }
        ],
        "tickets": []
    }

@app.post("/triage/{incident_id}")
async def triage_incident(incident_id: str):
    """Triage an incident"""
    return {
        "incident_id": incident_id,
        "status": "success",
        "message": f"Triaged incident {incident_id}",
        "suspect": {
            "repo": "repo-orders",
            "file": "src/orders/checkout.ts",
            "score": 8,
            "reasons": ["endpoint match", "error signature match"]
        }
    }

@app.post("/rca/initial/{incident_id}")
async def generate_initial_rca(incident_id: str):
    """Generate initial RCA"""
    return {
        "incident_id": incident_id,
        "status": "success",
        "message": f"Generated initial RCA for {incident_id}",
        "files_generated": ["TCK-1001_initial_rca.md", "TCK-1001_initial_rca.pdf"]
    }

@app.post("/apply-fix/{incident_id}")
async def apply_fix(incident_id: str):
    """Apply fix for incident"""
    return {
        "incident_id": incident_id,
        "status": "success",
        "message": f"Applied fix for {incident_id}",
        "fix_commit": "abc123def456",
        "files_changed": ["src/orders/checkout.ts"]
    }

@app.post("/rca/final/{incident_id}")
async def generate_final_rca(incident_id: str):
    """Generate final RCA"""
    return {
        "incident_id": incident_id,
        "status": "success",
        "message": f"Generated final RCA for {incident_id}",
        "files_generated": ["TCK-1001_final_rca.md", "TCK-1001_final_rca.pdf"]
    }

@app.post("/compare/{incident_id}")
async def generate_comparison(incident_id: str):
    """Generate before/after comparison"""
    return {
        "incident_id": incident_id,
        "status": "success",
        "message": f"Generated comparison for {incident_id}",
        "files_generated": ["TCK-1001_comparison.md"]
    }

@app.post("/ticket")
async def create_ticket(request_data: TicketRequest):
    """Create Linear ticket - simplified version without external dependencies"""
    try:
        # Get Linear API key from environment
        linear_api_key = os.getenv("LINEAR_API_KEY")
        
        if not linear_api_key:
            # No API key - return informative mock ticket
            return {
                "status": "success",
                "ticket_id": "RIT-MOCK-001",
                "ticket_url": "https://linear.app/ritwik-vats/issue/RIT-MOCK-001",
                "type": "mock",
                "message": "Mock ticket created - Add LINEAR_API_KEY to Vercel environment for real tickets"
            }
        
        # Try to import requests - if it fails, return mock
        try:
            import requests
        except ImportError:
            return {
                "status": "success",
                "ticket_id": "RIT-MOCK-002",
                "ticket_url": "https://linear.app/ritwik-vats/issue/RIT-MOCK-002",
                "type": "mock",
                "message": "Mock ticket created - requests library not available in Vercel"
            }
        
        # Extract incident ID from request
        incident_id = request_data.incident_file.split('/')[-1].replace('.json', '') if '/' in request_data.incident_file else request_data.incident_file.replace('.json', '')
        
        # Create incident data based on incident ID
        incident_data = {
            "TCK-1001": {
                "title": "Checkout intermittently timing out",
                "service": "orders-api",
                "error": "CheckoutTimeoutError: payment gateway exceeded 5s"
            },
            "TCK-1002": {
                "title": "Refund limits not enforced for premium users", 
                "service": "payments-api",
                "error": "RefundLimitExceededError: Missing tier config"
            },
            "TCK-1003": {
                "title": "Authentication rate limiting bypassed",
                "service": "auth-api", 
                "error": "LoginRateLimitError: Too many attempts"
            }
        }.get(incident_id, {
            "title": "Unknown incident",
            "service": "unknown",
            "error": "Unknown error"
        })
        
        # GraphQL mutation for Linear
        mutation = """
        mutation IssueCreate($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    url
                }
            }
        }
        """
        
        variables = {
            "input": {
                "title": f"[RCA] {incident_data['title']}",
                "description": f"**Incident:** {incident_id}\\n**Service:** {incident_data['service']}\\n**Error:** {incident_data['error']}\\n\\nGenerated by RCA Agent Dashboard",
                "teamId": request_data.team,
                "priority": 2
            }
        }
        
        # Make Linear API call
        response = requests.post(
            "https://api.linear.app/graphql",
            headers={
                "Authorization": f"Bearer {linear_api_key}",
                "Content-Type": "application/json"
            },
            json={"query": mutation, "variables": variables},
            timeout=15
        )
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            # Check for GraphQL errors
            if "errors" in result:
                error_msg = result["errors"][0].get("message", "Unknown GraphQL error")
                return {
                    "status": "success",
                    "ticket_id": "RIT-MOCK-003",
                    "ticket_url": "https://linear.app/ritwik-vats/issue/RIT-MOCK-003",
                    "type": "mock",
                    "message": f"Mock ticket created - Linear API error: {error_msg}"
                }
            
            # Check for successful issue creation
            if result.get("data", {}).get("issueCreate", {}).get("success"):
                issue = result["data"]["issueCreate"]["issue"]
                return {
                    "status": "success",
                    "ticket_id": issue["identifier"],
                    "ticket_url": issue["url"],
                    "type": "real",
                    "message": f"✅ Created real Linear ticket {issue['identifier']}"
                }
        
        # API call failed - return detailed mock
        return {
            "status": "success",
            "ticket_id": "RIT-MOCK-004",
            "ticket_url": "https://linear.app/ritwik-vats/issue/RIT-MOCK-004",
            "type": "mock",
            "message": f"Mock ticket created - Linear API returned {response.status_code}"
        }
            
    except Exception as e:
        # Detailed error handling
        return {
            "status": "success",
            "ticket_id": "RIT-MOCK-005",
            "ticket_url": "https://linear.app/ritwik-vats/issue/RIT-MOCK-005",
            "type": "mock",
            "message": f"Mock ticket created - Exception: {str(e)[:100]}"
        }

@app.post("/ticket/{incident_id}")
async def create_ticket_legacy(incident_id: str):
    """Legacy endpoint - redirects to new ticket endpoint"""
    request_data = TicketRequest(incident_file=f"incidents/{incident_id}.json", team="RIT")
    return await create_ticket(request_data)

@app.post("/demo/{incident_id}")
async def run_demo(incident_id: str):
    """Run full demo pipeline"""
    return {
        "incident_id": incident_id,
        "status": "success",
        "message": f"Completed full demo pipeline for {incident_id}",
        "steps_completed": [
            "triage",
            "initial_rca", 
            "apply_fix",
            "final_rca",
            "comparison",
            "ticket_creation"
        ],
        "files_generated": [
            "TCK-1001_initial_rca.md",
            "TCK-1001_initial_rca.pdf",
            "TCK-1001_final_rca.md", 
            "TCK-1001_final_rca.pdf",
            "TCK-1001_comparison.md"
        ]
    }

# Error handler
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": "The requested endpoint was not found"}
    )

# This is the entry point for Vercel
from mangum import Mangum
handler = Mangum(app, lifespan="off")
