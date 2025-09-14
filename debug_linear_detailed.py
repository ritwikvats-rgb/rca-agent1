#!/usr/bin/env python3
"""Detailed debug script for Linear API issues."""

import os
import sys
import requests
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from rca.linear_client import load_linear_config


def test_api_key():
    """Test if the API key is valid."""
    print("🔍 Testing Linear API key validity...")
    
    config = load_linear_config()
    
    if not config['api_key']:
        print("❌ No API key found. Please check your .env file.")
        return False
    
    print(f"🔑 API Key: {config['api_key'][:15]}...")
    
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": config['api_key'],
        "Content-Type": "application/json"
    }
    
    # Simple query to test authentication
    query = """
    query {
      viewer {
        id
        name
        email
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
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📡 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📡 Response Data: {json.dumps(data, indent=2)}")
            
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            viewer = data.get('data', {}).get('viewer', {})
            if viewer:
                print(f"✅ API key is valid!")
                print(f"👤 User: {viewer.get('name', 'Unknown')} ({viewer.get('email', 'No email')})")
                return True
            else:
                print("❌ No viewer data returned")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_teams_query():
    """Test the teams query specifically."""
    print("\n🔍 Testing teams query...")
    
    config = load_linear_config()
    
    url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": config['api_key'],
        "Content-Type": "application/json"
    }
    
    # Teams query
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
        
        print(f"📡 Teams Query Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📡 Teams Response: {json.dumps(data, indent=2)}")
            
            if 'errors' in data:
                print(f"❌ GraphQL errors: {data['errors']}")
                return False
            
            teams = data.get('data', {}).get('teams', {}).get('nodes', [])
            if teams:
                print(f"✅ Found {len(teams)} team(s):")
                for team in teams:
                    print(f"   - {team['key']}: {team['name']}")
                return True
            else:
                print("⚠️  No teams found")
                return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response Text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main debug function."""
    print("🚀 Linear API Detailed Debug\n")
    
    # Test 1: API Key validity
    api_valid = test_api_key()
    
    if api_valid:
        # Test 2: Teams query
        teams_valid = test_teams_query()
        
        if teams_valid:
            print("\n✅ All tests passed! Your Linear integration should work.")
        else:
            print("\n❌ Teams query failed.")
    else:
        print("\n❌ API key test failed.")
        print("\n💡 Troubleshooting steps:")
        print("1. Check your API key is correct")
        print("2. Ensure it starts with 'lin_api_'")
        print("3. Verify it has the right permissions in Linear")
        print("4. Try regenerating the API key")


if __name__ == "__main__":
    main()
