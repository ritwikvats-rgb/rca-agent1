#!/usr/bin/env python3
"""Debug script to list available Linear teams."""

import os
import sys
import requests
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rca.linear_client import load_linear_config


def list_teams():
    """List all teams in the Linear workspace."""
    print("🔍 Fetching teams from Linear workspace...")
    
    config = load_linear_config()
    
    if not config['api_key']:
        print("❌ No API key found. Please check your .env file.")
        return
    
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
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
          description
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
        
        if 'errors' in data:
            print(f"❌ GraphQL errors: {data['errors']}")
            return
        
        teams = data.get('data', {}).get('teams', {}).get('nodes', [])
        
        if not teams:
            print("❌ No teams found in your Linear workspace.")
            return
        
        print(f"✅ Found {len(teams)} team(s) in your Linear workspace:\n")
        
        for i, team in enumerate(teams, 1):
            print(f"{i}. Team Key: '{team['key']}'")
            print(f"   Name: {team['name']}")
            print(f"   ID: {team['id']}")
            if team.get('description'):
                print(f"   Description: {team['description']}")
            print()
        
        print("💡 Use one of these team keys in your .env file:")
        print("   LINEAR_TEAM_KEY=<team_key_from_above>")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    list_teams()
