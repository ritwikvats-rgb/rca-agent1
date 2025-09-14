"""If .env has LINEAR_API_KEY, create real ticket; else save mock JSON."""
import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from .schema import TicketData


def load_linear_config() -> Dict[str, Optional[str]]:
    """Load Linear configuration from environment."""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        'api_key': os.getenv('LINEAR_API_KEY'),
        'team_key': os.getenv('LINEAR_TEAM_KEY', 'FTS')
    }


def create_linear_ticket(ticket_data: TicketData) -> Dict[str, Any]:
    """Create a Linear ticket (real or mock)."""
    config = load_linear_config()
    
    if config['api_key']:
        return create_real_linear_ticket(ticket_data, config)
    else:
        return create_mock_linear_ticket(ticket_data, config)


def get_team_id(config: Dict[str, Optional[str]]) -> Optional[str]:
    """Get team ID from team key using Linear API."""
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": config['api_key'],
        "Content-Type": "application/json"
    }
    
    # Query to get teams
    query = """
    query {
      teams {
        nodes {
          id
          key
          name
        }
      }
    }
    """
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"query": query},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        teams = data.get('data', {}).get('teams', {}).get('nodes', [])
        
        # Find team by key
        for team in teams:
            if team['key'] == config['team_key']:
                return team['id']
        
        return None
    
    except Exception:
        return None


def create_real_linear_ticket(ticket_data: TicketData, config: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """Create a real Linear ticket using the API."""
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": config['api_key'],
        "Content-Type": "application/json"
    }
    
    # Get team ID from team key
    team_id = get_team_id(config)
    if not team_id:
        return {
            'success': False,
            'error': f"Team '{config['team_key']}' not found. Check your LINEAR_TEAM_KEY.",
            'type': 'real'
        }
    
    # GraphQL mutation to create issue
    mutation = """
    mutation IssueCreate($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue {
          id
          identifier
          title
          url
        }
      }
    }
    """
    
    variables = {
        "input": {
            "title": ticket_data.title,
            "description": ticket_data.description,
            "teamId": team_id,
            "priority": ticket_data.priority
        }
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"query": mutation, "variables": variables},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get('data', {}).get('issueCreate', {}).get('success'):
            issue = data['data']['issueCreate']['issue']
            return {
                'success': True,
                'ticket_id': issue['identifier'],
                'ticket_url': issue['url'],
                'type': 'real',
                'message': f"Created Linear ticket: {issue['identifier']}"
            }
        else:
            errors = data.get('errors', [])
            return {
                'success': False,
                'error': f"Linear API error: {errors}",
                'type': 'real'
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Failed to create Linear ticket: {str(e)}",
            'type': 'real'
        }


def create_mock_linear_ticket(ticket_data: TicketData, config: Dict[str, Optional[str]]) -> Dict[str, Any]:
    """Create a mock Linear ticket and save to file."""
    
    # Generate mock ticket ID
    import time
    ticket_id = f"{config['team_key']}-{int(time.time()) % 10000}"
    
    mock_ticket = {
        "id": ticket_id,
        "title": ticket_data.title,
        "description": ticket_data.description,
        "team": config['team_key'],
        "priority": ticket_data.priority,
        "labels": ticket_data.labels,
        "assignee": ticket_data.assignee,
        "status": "Todo",
        "created_at": "2025-09-13T15:30:00Z",
        "url": f"https://linear.app/{config['team_key']}/issue/{ticket_id}",
        "type": "mock"
    }
    
    # Save to mock directory
    mock_dir = Path("linear_mock")
    mock_dir.mkdir(exist_ok=True)
    
    ticket_file = mock_dir / f"{ticket_id}.json"
    with open(ticket_file, 'w') as f:
        json.dump(mock_ticket, f, indent=2)
    
    return {
        'success': True,
        'ticket_id': ticket_id,
        'ticket_url': mock_ticket['url'],
        'file_path': str(ticket_file),
        'type': 'mock',
        'message': f"Created mock Linear ticket: {ticket_id} (saved to {ticket_file})"
    }


def generate_ticket_description(incident_id: str, summary: str, suspect_repo: str, 
                              suspect_file: str, observations: list) -> str:
    """Generate ticket description from RCA data."""
    
    description_parts = [
        f"## Incident: {incident_id}",
        "",
        "### Summary",
        summary,
        "",
        "### Root Cause Analysis",
        f"**Suspect Code:** `{suspect_repo}/{suspect_file}`",
        "",
        "### Key Findings"
    ]
    
    if observations:
        for obs in observations:
            description_parts.append(f"- **{obs.kind.title()}:** {obs.note}")
    else:
        description_parts.append("- Analysis in progress")
    
    description_parts.extend([
        "",
        "### Next Steps",
        "- [ ] Review proposed fixes in RCA document",
        "- [ ] Implement timeout guard and retry logic",
        "- [ ] Add safe dictionary access patterns",
        "- [ ] Update tests and validation",
        "- [ ] Deploy and monitor",
        "",
        "### Links",
        "- Initial RCA document (see `out/` directory)",
        "- PR draft (see `out/` directory)",
        "",
        "_This ticket was auto-generated by RCA Agent_"
    ])
    
    return "\n".join(description_parts)


def create_ticket_from_rca(incident_id: str, rca_data, team_key: str = "FTS") -> Dict[str, Any]:
    """Create a Linear ticket from RCA data."""
    
    # Generate ticket description
    description = generate_ticket_description(
        incident_id,
        rca_data.summary,
        rca_data.suspect.repo,
        rca_data.suspect.file,
        rca_data.observations
    )
    
    # Determine priority based on observations
    priority = 2  # Default: Medium
    if any(obs.kind == "business_logic" for obs in rca_data.observations):
        priority = 1  # High priority for business logic issues
    
    # Create ticket data
    ticket_data = TicketData(
        title=f"[RCA] {rca_data.incident.title}",
        description=description,
        team_key=team_key,
        priority=priority,
        labels=["rca", "bug", "auto-generated"]
    )
    
    return create_linear_ticket(ticket_data)


def list_mock_tickets() -> list:
    """List all mock tickets."""
    mock_dir = Path("linear_mock")
    if not mock_dir.exists():
        return []
    
    tickets = []
    for ticket_file in mock_dir.glob("*.json"):
        try:
            with open(ticket_file, 'r') as f:
                ticket = json.load(f)
                tickets.append(ticket)
        except Exception:
            continue
    
    return sorted(tickets, key=lambda t: t.get('created_at', ''))
