"""Use data maps to collect candidate repos/files and attach reasons."""
from typing import List, Dict, Any
from .schema import Incident, Candidate
from .loaders import (
    load_services, load_routes, load_jobs, load_error_index, 
    load_releases, load_logs
)


def correlate_incident(incident: Incident) -> List[Candidate]:
    """Find candidate files for the incident using data maps."""
    candidates = {}  # repo/file -> candidate
    
    # Load all data maps
    services = load_services()
    routes = load_routes()
    jobs = load_jobs()
    error_index = load_error_index()
    releases = load_releases()
    logs = load_logs()
    
    # Helper to add or update candidate
    def add_candidate(repo: str, file: str, score: int, reason: str):
        key = f"{repo}/{file}"
        if key not in candidates:
            candidates[key] = Candidate(
                repo=repo,
                file=file,
                score=0,
                reasons=[]
            )
        candidates[key].score += score
        candidates[key].reasons.append(reason)
    
    # 1. Service mapping (+1 base score)
    if incident.service in services:
        service_info = services[incident.service]
        repo = service_info['repo']
        # Add a base candidate for the service
        add_candidate(repo, "unknown", 1, f"Service {incident.service} maps to {repo}")
    
    # 2. Endpoint mapping (+3 points)
    if incident.api_endpoint and incident.service:
        service_routes = routes.get(incident.service, {})
        if incident.api_endpoint in service_routes:
            handler = service_routes[incident.api_endpoint]
            if '#' in handler:
                file_path, function = handler.split('#')
                repo = services.get(incident.service, {}).get('repo', 'unknown')
                add_candidate(repo, file_path, 3, f"Endpoint {incident.api_endpoint} maps to {file_path}")
    
    # 3. Job/workflow mapping (+2 points)
    if incident.job_id:
        for job in jobs:
            if job['job_id'] == incident.job_id:
                repo = job['repo']
                handler = job['handler']
                if '#' in handler:
                    file_path, function = handler.split('#')
                else:
                    file_path = handler
                add_candidate(repo, file_path, 2, f"Job {incident.job_id} maps to {file_path}")
    
    # 4. Error signature mapping (+2 points)
    if incident.error_message:
        for error in error_index:
            if error['signature'] in incident.error_message:
                repo = error['repo']
                file_path = error['path_hint']
                add_candidate(repo, file_path, 2, f"Error signature '{error['signature']}' maps to {file_path}")
    
    # 5. Logs mention (+1 point)
    if incident.request_id:
        for log in logs:
            if log['request_id'] == incident.request_id:
                message = log['message']
                # Extract file path from log message
                if ' at ' in message:
                    parts = message.split(' at ')
                    if len(parts) > 1:
                        file_info = parts[1]
                        if ':' in file_info:
                            file_path = file_info.split(':')[0]
                            # Try to determine repo from service
                            repo = services.get(incident.service, {}).get('repo', 'unknown')
                            add_candidate(repo, file_path, 1, f"Request {incident.request_id} mentioned in logs at {file_path}")
    
    # 6. Release changes (+1 point)
    if incident.version and incident.service:
        for release in releases:
            if release['service'] == incident.service and release['release_tag'] == incident.version:
                # This is a placeholder - in real implementation, we'd parse git commits
                repo = services.get(incident.service, {}).get('repo', 'unknown')
                add_candidate(repo, "changed_in_release", 1, f"Changed in release {incident.version}")
    
    # Convert to list and sort by score
    candidate_list = list(candidates.values())
    candidate_list.sort(key=lambda c: c.score, reverse=True)
    
    return candidate_list


def get_top_candidate(incident: Incident) -> Candidate:
    """Get the highest-scoring candidate."""
    candidates = correlate_incident(incident)
    if candidates:
        return candidates[0]
    
    # Fallback candidate
    services = load_services()
    service_info = services.get(incident.service, {'repo': 'unknown', 'owners': 'unknown'})
    return Candidate(
        repo=service_info['repo'],
        file="unknown",
        score=0,
        reasons=["No specific mapping found"]
    )
