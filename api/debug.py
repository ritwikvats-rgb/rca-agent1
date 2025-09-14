from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/debug/env')
def debug_env():
    """Debug endpoint to check environment variables"""
    linear_api_key = os.getenv("LINEAR_API_KEY")
    linear_team_key = os.getenv("LINEAR_TEAM_KEY", "RIT")
    
    return jsonify({
        "linear_api_key_present": bool(linear_api_key),
        "linear_api_key_length": len(linear_api_key) if linear_api_key else 0,
        "linear_team_key": linear_team_key,
        "vercel_env": os.getenv("VERCEL_ENV", "unknown"),
        "status": "healthy"
    })

@app.route('/debug/linear')
def debug_linear():
    """Debug Linear API connectivity"""
    linear_api_key = os.getenv("LINEAR_API_KEY")
    
    if not linear_api_key:
        return jsonify({"error": "No LINEAR_API_KEY found"})
    
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
        
        return jsonify({
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "headers": dict(response.headers)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

# For Vercel
def handler(request):
    return app(request.environ, lambda status, headers: None)
