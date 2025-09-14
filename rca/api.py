"""FastAPI backend for RCA Agent web interface."""
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RCA Agent API",
    description="Web API for Root Cause Analysis automation",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base paths
BASE_DIR = Path(__file__).parent.parent
OUT_DIR = BASE_DIR / "out"
LINEAR_MOCK_DIR = BASE_DIR / "linear_mock"
INCIDENTS_DIR = BASE_DIR / "incidents"

def run_cli_command(command: List[str]) -> Dict[str, Any]:
    """Run a CLI command and return structured output."""
    try:
        # Ensure we're in the right directory
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "command": " ".join(command)
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out after 60 seconds",
            "returncode": -1,
            "command": " ".join(command)
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "command": " ".join(command)
        }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "RCA Agent API",
        "version": "1.0.0",
        "base_dir": str(BASE_DIR)
    }

@app.get("/incidents")
async def list_incidents():
    """List available incident files."""
    try:
        incidents = []
        if INCIDENTS_DIR.exists():
            for file in INCIDENTS_DIR.glob("*.json"):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    incidents.append({
                        "filename": file.name,
                        "id": data.get("id", file.stem),
                        "title": data.get("title", "Unknown"),
                        "service": data.get("service", "Unknown"),
                        "created_at": data.get("created_at", "Unknown")
                    })
                except Exception as e:
                    logger.warning(f"Failed to parse {file}: {e}")
        
        return {
            "success": True,
            "incidents": incidents,
            "count": len(incidents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/triage/{incident}")
async def triage_incident(incident: str):
    """Run triage analysis on an incident."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "triage", incident_file]
    result = run_cli_command(command)
    
    return {
        "operation": "triage",
        "incident": incident,
        "result": result,
        "timestamp": str(Path().cwd())
    }

@app.post("/rca/initial/{incident}")
async def generate_initial_rca(incident: str):
    """Generate initial RCA document."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "rca", incident_file, "--initial"]
    result = run_cli_command(command)
    
    return {
        "operation": "initial_rca",
        "incident": incident,
        "result": result,
        "artifacts": list_artifacts_for_incident(incident)
    }

@app.post("/apply-fix/{incident}")
async def apply_fix(incident: str):
    """Apply fixes and create commit."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "apply-fix", incident_file]
    result = run_cli_command(command)
    
    return {
        "operation": "apply_fix",
        "incident": incident,
        "result": result
    }

@app.post("/rca/final/{incident}")
async def generate_final_rca(incident: str, fix_commit: str = "latest"):
    """Generate final RCA document."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "rca", incident_file, "--final"]
    if fix_commit != "latest":
        command.extend(["--fix-commit", fix_commit])
    
    result = run_cli_command(command)
    
    return {
        "operation": "final_rca",
        "incident": incident,
        "result": result,
        "artifacts": list_artifacts_for_incident(incident)
    }

@app.post("/compare/{incident}")
async def generate_comparison(incident: str):
    """Generate before/after comparison document."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "compare", incident_file]
    result = run_cli_command(command)
    
    return {
        "operation": "compare",
        "incident": incident,
        "result": result,
        "artifacts": list_artifacts_for_incident(incident)
    }

@app.post("/ticket/{incident}")
async def create_ticket(incident: str, team: str = "FTS"):
    """Create Linear ticket."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "ticket", incident_file, "--team", team]
    result = run_cli_command(command)
    
    # List tickets
    tickets = []
    if LINEAR_MOCK_DIR.exists():
        for ticket_file in LINEAR_MOCK_DIR.glob("*.json"):
            tickets.append(ticket_file.name)
    
    return {
        "operation": "create_ticket",
        "incident": incident,
        "team": team,
        "result": result,
        "tickets": tickets
    }

@app.post("/demo/{incident}")
async def run_demo_pipeline(incident: str):
    """Run complete demo pipeline."""
    incident_file = f"incidents/{incident}.json"
    if not (BASE_DIR / incident_file).exists():
        raise HTTPException(status_code=404, detail=f"Incident file {incident_file} not found")
    
    command = ["python3", "-m", "rca.cli", "demo", incident_file]
    result = run_cli_command(command)
    
    return {
        "operation": "demo_pipeline",
        "incident": incident,
        "result": result,
        "artifacts": list_artifacts_for_incident(incident),
        "tickets": list_tickets()
    }

@app.get("/artifacts")
async def list_artifacts():
    """List all generated artifacts."""
    artifacts = {
        "documents": [],
        "tickets": [],
        "total_size": 0
    }
    
    # List documents in out/
    if OUT_DIR.exists():
        for file in OUT_DIR.iterdir():
            if file.is_file():
                stat = file.stat()
                artifacts["documents"].append({
                    "name": file.name,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "type": file.suffix,
                    "download_url": f"/download/{file.name}"
                })
                artifacts["total_size"] += stat.st_size
    
    # List tickets in linear_mock/
    artifacts["tickets"] = list_tickets()
    
    return artifacts

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download an artifact file."""
    # Check in out/ directory
    file_path = OUT_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    
    # Check in linear_mock/ directory
    file_path = LINEAR_MOCK_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/json'
        )
    
    raise HTTPException(status_code=404, detail=f"File {filename} not found")

def list_artifacts_for_incident(incident: str) -> List[Dict[str, Any]]:
    """List artifacts for a specific incident."""
    artifacts = []
    if OUT_DIR.exists():
        for file in OUT_DIR.glob(f"{incident}*"):
            if file.is_file():
                stat = file.stat()
                artifacts.append({
                    "name": file.name,
                    "size": stat.st_size,
                    "type": file.suffix,
                    "download_url": f"/download/{file.name}"
                })
    return artifacts

def list_tickets() -> List[Dict[str, Any]]:
    """List all tickets."""
    tickets = []
    if LINEAR_MOCK_DIR.exists():
        for ticket_file in LINEAR_MOCK_DIR.glob("*.json"):
            try:
                with open(ticket_file, 'r') as f:
                    data = json.load(f)
                tickets.append({
                    "filename": ticket_file.name,
                    "id": data.get("id", ticket_file.stem),
                    "title": data.get("title", "Unknown"),
                    "team": data.get("team", "Unknown"),
                    "status": data.get("status", "Unknown"),
                    "download_url": f"/download/{ticket_file.name}"
                })
            except Exception as e:
                logger.warning(f"Failed to parse ticket {ticket_file}: {e}")
    return tickets

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
