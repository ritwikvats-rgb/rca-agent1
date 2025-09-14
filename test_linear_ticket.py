#!/usr/bin/env python3
"""
Test Linear API ticket creation with proper error handling
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_linear_api():
    load_dotenv()
    
    api_key = os.getenv('LINEAR_API_KEY')
    if not api_key:
        print("❌ No LINEAR_API_KEY found in environment")
        return False
    
    print(f"🔑 Testing Linear API Key: {api_key[:20]}...")
    
    url = 'https://api.linear.app/graphql'
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    # Step 1: Test basic connection and get teams
    print("\n1. Testing API connection and getting teams...")
    team_query = {
        'query': '''
        {
          teams {
            nodes {
              id
              name
              key
            }
          }
        }
        '''
    }
    
    try:
        team_response = requests.post(url, json=team_query, headers=headers, timeout=10)
        print(f"   Status: {team_response.status_code}")
        
        if team_response.status_code != 200:
            print(f"   ❌ HTTP Error: {team_response.text}")
            return False
            
        team_data = team_response.json()
        
        if 'errors' in team_data:
            print(f"   ❌ GraphQL Errors: {team_data['errors']}")
            return False
            
        teams = team_data.get('data', {}).get('teams', {}).get('nodes', [])
        if not teams:
            print("   ❌ No teams found")
            return False
            
        team = teams[0]
        team_id = team['id']
        print(f"   ✅ Team found: {team['name']} (ID: {team_id})")
        
    except Exception as e:
        print(f"   ❌ Connection error: {str(e)}")
        return False
    
    # Step 2: Create a simple issue
    print("\n2. Creating Linear issue...")
    
    # Use the simplest possible mutation
    issue_mutation = {
        'query': '''
        mutation {
          issueCreate(input: {
            teamId: "''' + team_id + '''"
            title: "RCA Agent Test Ticket"
            description: "Test ticket from RCA Agent"
          }) {
            success
            issue {
              id
              identifier
              title
              url
            }
          }
        }
        '''
    }
    
    try:
        issue_response = requests.post(url, json=issue_mutation, headers=headers, timeout=15)
        print(f"   Status: {issue_response.status_code}")
        
        if issue_response.status_code != 200:
            print(f"   ❌ HTTP Error: {issue_response.text}")
            return False
            
        issue_data = issue_response.json()
        print(f"   Raw response: {json.dumps(issue_data, indent=2)}")
        
        if 'errors' in issue_data:
            print(f"   ❌ GraphQL Errors: {issue_data['errors']}")
            return False
            
        create_result = issue_data.get('data', {}).get('issueCreate', {})
        
        if create_result.get('success'):
            issue = create_result.get('issue', {})
            print(f"\n   ✅ SUCCESS! Linear ticket created:")
            print(f"      🆔 ID: {issue.get('identifier')}")
            print(f"      📝 Title: {issue.get('title')}")
            print(f"      🔗 URL: {issue.get('url')}")
            return True
        else:
            print(f"   ❌ Issue creation failed: {create_result}")
            return False
            
    except Exception as e:
        print(f"   ❌ Issue creation error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎫 Testing Linear API Integration...")
    success = test_linear_api()
    
    if success:
        print("\n🎉 LINEAR INTEGRATION WORKING PERFECTLY!")
    else:
        print("\n❌ Linear integration needs debugging")
