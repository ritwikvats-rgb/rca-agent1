"""Functions to read CSV/YAML/MD files and repo source files."""
import json
import csv
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from .schema import Incident


def load_incident(incident_path: str) -> Incident:
    """Load incident from JSON file."""
    with open(incident_path, 'r') as f:
        data = json.load(f)
    return Incident(**data)


def load_services() -> Dict[str, Dict[str, str]]:
    """Load services mapping from CSV."""
    services = {}
    with open('data/services.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            services[row['service']] = {
                'repo': row['repo'],
                'owners': row['owners']
            }
    return services


def load_routes() -> Dict[str, Dict[str, str]]:
    """Load routes mapping from YAML."""
    with open('data/routes_openapi.yaml', 'r') as f:
        return yaml.safe_load(f)


def load_jobs() -> List[Dict[str, str]]:
    """Load jobs registry from CSV."""
    jobs = []
    with open('data/jobs_registry.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(dict(row))
    return jobs


def load_error_index() -> List[Dict[str, str]]:
    """Load error index from CSV."""
    errors = []
    with open('data/error_index.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            errors.append(dict(row))
    return errors


def load_releases() -> List[Dict[str, str]]:
    """Load releases from CSV."""
    releases = []
    with open('data/releases.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            releases.append(dict(row))
    return releases


def load_logs() -> List[Dict[str, str]]:
    """Load mock logs from CSV."""
    logs = []
    with open('data/logs_mock.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            logs.append(dict(row))
    return logs


def load_guidelines() -> List[Dict[str, str]]:
    """Load code guidelines from CSV."""
    guidelines = []
    with open('docs/guidelines.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            guidelines.append(dict(row))
    return guidelines


def load_prd_yaml(feature: str) -> Optional[Dict[str, Any]]:
    """Load PRD YAML file for a feature."""
    prd_path = f'docs/prd/{feature}.yml'
    if Path(prd_path).exists():
        with open(prd_path, 'r') as f:
            return yaml.safe_load(f)
    return None


def load_repo_file(repo: str, file_path: str) -> Optional[str]:
    """Load source code file from repo."""
    full_path = f'repos/{repo}/{file_path}'
    if Path(full_path).exists():
        with open(full_path, 'r') as f:
            return f.read()
    return None


def get_file_extension(file_path: str) -> str:
    """Get file extension for syntax highlighting."""
    ext = Path(file_path).suffix.lower()
    ext_map = {
        '.ts': 'typescript',
        '.js': 'javascript',
        '.py': 'python',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.cpp': 'cpp',
        '.c': 'c'
    }
    return ext_map.get(ext, 'text')
