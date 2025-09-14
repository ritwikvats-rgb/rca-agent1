#!/usr/bin/env python3
"""
Detailed Linear API debugging script to identify the exact issue
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_linear_api():
    """Test Linear API with detailed debugging"""
    
    print("🔍 DETAILED LINEAR API DEBUGGING")
    print("=" * 50)
    
    # Get API key
    linear_api_key = os.getenv("LINEAR_API_KEY")
    if not linear_api_key:
        print("❌ No LINEAR_API_KEY found in environment")
        return
    
    print(f"🔑 API Key: {linear_api_key[:20]}...")
    
    # Test 1: Basic API connectivity
    print("\n1️⃣ Testing basic API connectivity...")
    try:
        response = requests.get("https://api.linear.app/graphql", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Test 2: Get viewer info (simple query)
    print("\n2️⃣ Testing viewer query...")
    viewer_query = """
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
            "https://api.linear.app/graphql",
            headers={
                "Authorization": linear_api_key,
                "Content-Type": "application/json"
            },
            json={"query": viewer_query},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {json.dumps(result, indent=2)}")
        
        if "errors" in result:
            print("   ❌ GraphQL errors found")
            return
        
        viewer = result.get("data", {}).get("viewer", {})
        print(f"   ✅ Authenticated as: {viewer.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"   ❌ Viewer query failed: {e}")
        return
    
    # Test 3: Get teams
    print("\n3️⃣ Testing teams query...")
    teams_query = """
    query {
        teams {
            nodes {
                id
                name
                key
            }
        }
    }
    """
    
    try:
        response = requests.post(
            "https://api.linear.app/graphql",
            headers={
                "Authorization": linear_api_key,
                "Content-Type": "application/json"
            },
            json={"query": teams_query},
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        result = response.json()
        
        if "errors" in result:
            print(f"   ❌ GraphQL errors: {result['errors']}")
            return
        
        teams = result.get("data", {}).get("teams", {}).get("nodes", [])
        print(f"   ✅ Found {len(teams)} teams:")
        for team in teams:
            print(f"      - {team['name']} (key: {team['key']}, id: {team['id']})")
        
        # Find the correct team ID
        team_id = None
        for team in teams:
            if team['key'] in ['RIT', 'Ritwik']:
                team_id = team['id']
                print(f"   🎯 Using team: {team['name']} (ID: {team_id})")
                break
        
        if not team_id and teams:
            team_id = teams[0]['id']
            print(f"   🎯 Using first team: {teams[0]['name']} (ID: {team_id})")
        
        if not team_id:
            print("   ❌ No teams found")
            return
            
    except Exception as e:
        print(f"   ❌ Teams query failed: {e}")
        return
    
    # Test 4: Create issue with proper structure
    print("\n4️⃣ Testing issue creation...")
    
    # Use the correct mutation structure
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
            lastSyncId
        }
    }
    """
    
    variables = {
        "input": {
            "title": "RCA Agent Test - Detailed Debug",
            "description": "This is a test ticket created by the RCA Agent debugging script to verify Linear API integration.",
            "teamId": team_id,
            "priority": 2
        }
    }
    
    try:
        response = requests.post(
            "https://api.linear.app/graphql",
            headers={
                "Authorization": linear_api_key,
                "Content-Type": "application/json"
            },
            json={
                "query": mutation,
                "variables": variables
            },
            timeout=15
        )
        
        print(f"   Status: {response.status_code}")
        print(f"   Raw response: {response.text}")
        
        if response.status_code != 200:
            print(f"   ❌ HTTP error: {response.status_code}")
            return
        
        result = response.json()
        print(f"   Parsed response: {json.dumps(result, indent=2)}")
        
        if "errors" in result:
            print(f"   ❌ GraphQL errors: {result['errors']}")
            for error in result['errors']:
                print(f"      - {error.get('message', 'Unknown error')}")
                if 'extensions' in error:
                    print(f"        Extensions: {error['extensions']}")
            return
        
        issue_data = result.get("data", {}).get("issueCreate", {})
        if issue_data.get("success"):
            issue = issue_data.get("issue", {})
            print(f"   ✅ SUCCESS! Created issue:")
            print(f"      ID: {issue.get('identifier')}")
            print(f"      Title: {issue.get('title')}")
            print(f"      URL: {issue.get('url')}")
        else:
            print(f"   ❌ Issue creation failed: {issue_data}")
            
    except Exception as e:
        print(f"   ❌ Issue creation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_linear_api()
