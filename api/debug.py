import json
import os

def handler(request):
    """Vercel serverless function handler"""
    
    # Parse the request path to determine which endpoint to serve
    path = request.get('path', '/')
    method = request.get('httpMethod', 'GET')
    
    if path.endswith('/debug/env') and method == 'GET':
        return debug_env()
    elif path.endswith('/debug/linear') and method == 'GET':
        return debug_linear()
    else:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not found'})
        }

def debug_env():
    """Debug endpoint to check environment variables"""
    linear_api_key = os.getenv("LINEAR_API_KEY")
    linear_team_key = os.getenv("LINEAR_TEAM_KEY", "RIT")
    
    response_data = {
        "linear_api_key_present": bool(linear_api_key),
        "linear_api_key_length": len(linear_api_key) if linear_api_key else 0,
        "linear_team_key": linear_team_key,
        "vercel_env": os.getenv("VERCEL_ENV", "unknown"),
        "status": "healthy"
    }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_data)
    }

def debug_linear():
    """Debug Linear API connectivity"""
    linear_api_key = os.getenv("LINEAR_API_KEY")
    
    if not linear_api_key:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": "No LINEAR_API_KEY found"})
        }
    
    try:
        import requests
        
        # Test basic connectivity with viewer query
        viewer_query = """
        query {
            viewer {
                id
                name
                email
            }
        }
        """
        
        response = requests.post(
            "https://api.linear.app/graphql",
            headers={
                "Authorization": linear_api_key,
                "Content-Type": "application/json",
                "User-Agent": "RCA-Agent/1.0"
            },
            json={"query": viewer_query},
            timeout=30
        )
        
        response_data = {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "headers": dict(response.headers)
        }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({"error": str(e)})
        }
