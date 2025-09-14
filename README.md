# RCA Agent (Dummy, Offline) — Full End-to-End

A demonstration project showing how an RCA (Root Cause Analysis) Agent works from incident to resolution.

## What This Does

This agent simulates a complete incident response workflow:

1. **Reads incidents** from JSON files with service/endpoint/error details
2. **Maps incidents to code** using mock data tables (routes, jobs, errors, logs)
3. **Scores candidates** with explainable rules (+3 endpoint match, +2 job match, etc.)
4. **Analyzes against PRDs** to classify business logic vs code quality issues
5. **Generates documents**: Initial RCA, PR drafts, tickets, final RCA, comparisons
6. **Simulates git workflow** with local commits, tags, and fixes
7. **Tracks timeline** and turnaround time (TAT)

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .env.example
├── docs/
│   ├── prd/                    # Product requirements (human + machine readable)
│   ├── guidelines.csv          # Code quality rules
│   └── templates/              # Jinja2 templates for document generation
├── data/                       # Mock system mappings
├── incidents/                  # Sample incident files
├── repos/                      # Mock code repositories to analyze
├── rca/                        # Main Python package
├── scripts/                    # Demo scripts
├── out/                        # Generated documents
└── linear_mock/               # Mock ticket storage
```

## Quick Start

### 🌐 Web Interface (Recommended)
```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start web server
python serve.py

# Open web/index.html in your browser
# Use the dashboard to run operations with buttons!
```

### 📱 Command Line Interface

#### macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/demo.sh
```

#### Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m rca.cli init
python -m rca.cli triage incidents/TCK-1001.json
python -m rca.cli rca incidents/TCK-1001.json --initial
python -m rca.cli draft-pr incidents/TCK-1001.json
python -m rca.cli ticket incidents/TCK-1001.json --team FTS
# Note: Copy the fix commit hash from the output and use it in the next command
python -m rca.cli apply-fix incidents/TCK-1001.json
python -m rca.cli rca incidents/TCK-1001.json --final --fix-commit <PASTE_FIX_COMMIT_HASH>
python -m rca.cli compare incidents/TCK-1001.json
```

## 🎨 Web Dashboard Features

The RCA Agent now includes a professional web interface:

- **🎯 Interactive Operations**: Click buttons to run triage, generate RCAs, apply fixes
- **📊 Real-time Output**: See API responses and command output in real-time
- **📁 Artifact Browser**: Download generated documents (PDFs, Markdown, tickets)
- **🔄 Auto-refresh**: Artifacts update automatically after operations
- **⚡ One-Click Demo**: Run the complete pipeline with a single button
- **📱 Responsive Design**: Works on desktop and mobile devices

### Web Interface Usage:
1. **Start Server**: `python serve.py` (runs on http://127.0.0.1:8000)
2. **Open Dashboard**: Open `web/index.html` in your browser
3. **Run Operations**: Use buttons to execute RCA workflow steps
4. **Download Results**: Click download links for generated documents
5. **API Documentation**: Visit http://127.0.0.1:8000/docs for API details

## How It Works

### 1. Incident Analysis
The agent reads incident JSON files containing:
- Service, endpoint, job IDs
- Error messages and stack traces
- Timeline information

### 2. Code Correlation
Using mock data tables, it maps incidents to specific repositories and files:
- **Routes**: API endpoints → source files
- **Jobs**: Background job IDs → handlers
- **Errors**: Error signatures → likely files
- **Logs**: Request IDs → stack traces
- **Releases**: Version tags → commit history

### 3. Scoring System
Candidates are scored with transparent rules:
- +3 points: Endpoint match
- +2 points: Job/workflow match
- +2 points: Error signature match
- +1 point: Mentioned in logs
- +1 point: Changed in recent release

### 4. PRD Analysis
The agent checks code against Product Requirements Documents:
- **Business Logic Issues**: Violate product promises (timeouts, error handling)
- **Code Quality Issues**: Technical debt (long functions, bare exceptions)

### 5. Document Generation
Automatically produces:
- **Initial RCA**: 5 Whys, impact analysis, suspect identification
- **PR Draft**: Proposed fixes with risk assessment
- **Tickets**: Structured issue tracking
- **Final RCA**: Post-fix analysis with prevention measures
- **Comparison**: Before/after code and timeline analysis

### 6. Git Integration
Creates a local git history to simulate:
- Baseline code state
- Bug introduction
- Release tagging
- Fix implementation

## Example Workflow

The demo incident (`TCK-1001`) simulates a checkout timeout issue:

1. **Incident**: Checkout API timing out after 6 seconds
2. **Analysis**: Maps to `checkout.ts`, identifies missing timeout guard
3. **Classification**: Business logic violation (PRD requires 5s timeout)
4. **Documents**: Generates RCA, PR draft, and ticket
5. **Fix**: Applies timeout guard and retry logic
6. **Validation**: Produces final RCA with prevention measures

## Sample Output

After running the demo, you'll find generated documents in the `out/` directory:
- `TCK-1001_initial_rca.md` and `.pdf`
- `TCK-1001_pr_draft.md`
- `TCK-1001_final_rca.md` and `.pdf`
- `TCK-1001_comparison.md`

## Configuration

Copy `.env.example` to `.env` and configure:
- `LINEAR_API_KEY`: For real Linear ticket creation (optional)
- `LINEAR_TEAM_KEY`: Team identifier for tickets

## Architecture

The system is designed to be:
- **Explainable**: Clear scoring rules and reasoning
- **Extensible**: Easy to add new data sources and rules
- **Realistic**: Simulates real-world incident response workflows
- **Offline**: No external dependencies for core functionality

This demonstrates how an RCA agent could work in production with real GitHub, Linear, and monitoring integrations.

## 🚀 Hosting & Deployment

The RCA Agent is ready for production hosting with Docker support:

### Quick Deployment
```bash
# Simple Docker deployment
./scripts/deploy.sh

# Production deployment with Nginx
./scripts/deploy.sh production
```

### Hosting Options
- **Docker**: Complete containerization with health checks
- **AWS ECS**: Production-ready with load balancing
- **Google Cloud Run**: Serverless container hosting
- **Azure Container Instances**: Simple cloud deployment
- **Heroku/Railway**: Platform-as-a-Service options
- **DigitalOcean**: App Platform deployment

### Features
- 🐳 **Docker & Docker Compose** configurations
- 🌐 **Nginx reverse proxy** for production
- 🔒 **SSL/HTTPS support** with Let's Encrypt
- 📊 **Health checks** and monitoring
- 🔄 **Auto-restart** and scaling options
- 📁 **Persistent storage** for artifacts

For detailed hosting instructions, see [HOSTING.md](HOSTING.md).

### Access URLs
- **Dashboard**: `http://localhost/` (production) or `http://localhost:8000/web/` (development)
- **API**: `http://localhost:8000/` or `http://localhost/api/` (with Nginx)
- **API Docs**: `http://localhost:8000/docs`
