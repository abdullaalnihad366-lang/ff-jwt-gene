import os
import sys
import json
import time
import random
import ssl
import gzip
import hashlib
import hmac
import base64
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.crypto import encrypt_proto, decrypt_response
from utils.garena import get_access_token
from utils.protobuf_helpers import create_major_login, parse_major_response

app = Flask(__name__)

def generate_jwt(uid, password):
    """Generate JWT token for a Free Fire account"""
    result = {
        "success": False,
        "uid": uid,
        "jwt_token": None,
        "account_uid": None,
        "region": None,
        "message": "",
        "timestamp": datetime.now().isoformat()
    }
    
    if not uid or not password:
        result["message"] = "UID and Password are required."
        return result
    
    if not uid.isdigit() or len(uid) < 8:
        result["message"] = "Invalid UID format."
        return result
    
    try:
        # Step 1: Get access token
        access_token, open_id = get_access_token(uid, password)
        if not access_token or not open_id:
            result["message"] = "Invalid UID or Password. Failed to get access token."
            return result
        
        # Step 2: Create and send MajorLogin request
        major_login_data = create_major_login(access_token, open_id)
        response_hex = send_major_login(major_login_data)
        
        if not response_hex:
            result["message"] = "Failed to get response from MajorLogin. Account may be banned or invalid."
            return result
        
        # Step 3: Parse response
        parsed_data = parse_major_response(response_hex)
        
        if parsed_data and parsed_data.get('token'):
            result["success"] = True
            result["jwt_token"] = parsed_data['token']
            result["account_uid"] = parsed_data.get('account_uid')
            result["region"] = parsed_data.get('region', 'IND')
            result["message"] = "JWT generated successfully!"
            return result
        
        # Step 4: Try manual parsing
        manual_data = parse_major_response_manual(response_hex)
        if manual_data and manual_data.get('token'):
            result["success"] = True
            result["jwt_token"] = manual_data['token']
            result["account_uid"] = manual_data.get('account_uid')
            result["region"] = manual_data.get('region', 'IND')
            result["message"] = "JWT generated successfully! (Manual parsing)"
            return result
        
        result["message"] = "No JWT token received in response. Account may be invalid or banned."
        return result
        
    except Exception as e:
        result["message"] = f"Error: {str(e)}"
        return result

def send_major_login(encrypted_data):
    """Send MajorLogin request to server"""
    try:
        context = ssl._create_unverified_context()
        conn = http.client.HTTPSConnection("loginbp.ggpolarbear.com", context=context, timeout=20)
        
        headers = {
            'X-Unity-Version': '2018.4.11f1',
            'ReleaseVersion': 'OB54',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
        
        conn.request("POST", "/MajorLogin", body=encrypted_data, headers=headers)
        response = conn.getresponse()
        raw_data = response.read()
        
        if response.getheader('Content-Encoding') == 'gzip':
            with gzip.GzipFile(fileobj=BytesIO(raw_data)) as f:
                raw_data = f.read()
        conn.close()
        
        if response.status in [200, 201]:
            return raw_data.hex()
        return None
    except Exception as e:
        return None

def parse_major_response_manual(hex_data):
    """Manually parse the MajorLogin response without protobuf"""
    try:
        import re
        data = bytes.fromhex(hex_data)
        text = data.decode('utf-8', errors='ignore')
        
        # Look for JWT pattern
        jwt_pattern = r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
        matches = re.findall(jwt_pattern, text)
        if matches:
            return {'token': matches[0]}
        
        # Try to extract account_uid
        uid_pattern = r'"account_uid":\s*(\d+)'
        uid_match = re.search(uid_pattern, text)
        account_uid = uid_match.group(1) if uid_match else None
        
        region_pattern = r'"region":\s*"([^"]+)"'
        region_match = re.search(region_pattern, text)
        region = region_match.group(1) if region_match else None
        
        return {'account_uid': account_uid, 'region': region}
    except:
        return None

@app.route('/')
def index():
    """Simple HTML interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Free Fire JWT Generator API</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                max-width: 900px; 
                margin: 30px auto; 
                padding: 20px; 
                background: #0a0a0f; 
                color: #e0e0e0; 
                line-height: 1.6;
            }
            .container { 
                background: linear-gradient(145deg, #12121f, #1a1a2e); 
                padding: 35px; 
                border-radius: 16px; 
                border: 1px solid rgba(255,255,255,0.05);
                box-shadow: 0 20px 60px rgba(0,0,0,0.8);
            }
            h1 { 
                color: #ff0066; 
                text-align: center; 
                font-size: 2.2em;
                margin-bottom: 5px;
                letter-spacing: 2px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 0.9em;
                letter-spacing: 1px;
            }
            .endpoint { 
                background: #0a0a1a; 
                padding: 18px 20px; 
                border-radius: 10px; 
                margin: 15px 0;
                border-left: 3px solid #ff0066;
            }
            .endpoint code { 
                color: #00e676; 
                background: transparent; 
                padding: 2px 8px; 
                border-radius: 4px;
                font-size: 1.1em;
                word-break: break-all;
            }
            .method {
                display: inline-block;
                background: #ff0066;
                color: white;
                padding: 2px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 0.8em;
                margin-right: 10px;
            }
            .param { color: #ffd700; font-weight: bold; }
            .response { 
                background: #0a0a1a; 
                padding: 18px; 
                border-radius: 10px; 
                overflow-x: auto;
                border: 1px solid rgba(255,255,255,0.05);
                margin: 10px 0;
            }
            .response pre {
                color: #a0e0a0;
                font-size: 0.9em;
                margin: 0;
                white-space: pre-wrap;
                word-wrap: break-word;
            }
            .success { color: #00e676; }
            .error { color: #ff1744; }
            hr { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 25px 0; }
            ul { list-style: none; padding: 0; }
            ul li { padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }
            ul li:last-child { border-bottom: none; }
            .footer {
                text-align: center;
                color: #444;
                font-size: 0.8em;
                margin-top: 30px;
            }
            .badge {
                display: inline-block;
                background: rgba(0,230,118,0.1);
                color: #00e676;
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 0.8em;
                border: 1px solid rgba(0,230,118,0.2);
            }
            .troubleshoot {
                background: rgba(255,215,0,0.05);
                border: 1px solid rgba(255,215,0,0.1);
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
            }
            .troubleshoot h3 { color: #ffd700; margin-bottom: 10px; }
            .troubleshoot li { color: #aaa; }
            @media (max-width: 600px) {
                .container { padding: 20px; }
                h1 { font-size: 1.6em; }
                .endpoint code { font-size: 0.9em; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 Free Fire JWT Generator</h1>
            <p class="subtitle">Generate JWT tokens for Free Fire accounts</p>
            
            <div style="text-align:center;margin-bottom:20px;">
                <span class="badge">● API v1.1</span>
                <span class="badge" style="background:rgba(255,0,102,0.1);color:#ff0066;border-color:rgba(255,0,102,0.2);">● Enhanced Parsing</span>
            </div>
            
            <hr>
            
            <h2 style="color:#ffd700;font-size:1.2em;margin-bottom:15px;">📡 API Endpoint</h2>
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/token?uid={uid}&password={password}</code>
            </div>
            
            <h2 style="color:#ffd700;font-size:1.2em;margin:20px 0 15px;">📝 Parameters</h2>
            <ul>
                <li>🔑 <span class="param">uid</span> — Free Fire Account UID <span style="color:#666;font-size:0.85em;">(required)</span></li>
                <li>🔒 <span class="param">password</span> — Account Password <span style="color:#666;font-size:0.85em;">(required)</span></li>
            </ul>
            
            <div class="troubleshoot">
                <h3>⚠️ Troubleshooting</h3>
                <ul>
                    <li>❌ <strong>"No JWT token received"</strong> — Account may be banned or password is incorrect</li>
                    <li>❌ <strong>"Invalid UID or Password"</strong> — Check credentials and try again</li>
                    <li>✅ <strong>Success</strong> — JWT token generated and ready to use</li>
                </ul>
            </div>
            
            <h2 style="color:#ffd700;font-size:1.2em;margin:20px 0 15px;">📤 Example Request</h2>
            <div class="endpoint" style="border-left-color:#448aff;">
                <code>GET /token?uid=123456789&password=yourpassword</code>
            </div>
            
            <h2 style="color:#ffd700;font-size:1.2em;margin:20px 0 15px;">📥 Example Response (Success)</h2>
            <div class="response">
                <pre>{
    <span class="success">"success"</span>: true,
    "uid": "123456789",
    <span class="success">"jwt_token"</span>: "eyJhbGciOiJIUzI1NiIs...",
    "account_uid": "987654321",
    "region": "IND",
    <span class="success">"message"</span>: "JWT generated successfully!",
    "timestamp": "2026-08-27T12:34:56"
}</pre>
            </div>
            
            <hr>
            
            <div style="background:rgba(255,0,102,0.05);padding:15px;border-radius:10px;border:1px solid rgba(255,0,102,0.1);">
                <p style="color:#ffd700;font-weight:bold;">💡 Quick Test</p>
                <p style="color:#888;font-size:0.9em;">Try it now with curl:</p>
                <div style="background:#0a0a1a;padding:12px;border-radius:6px;margin-top:8px;">
                    <code style="color:#00e676;font-size:0.85em;">curl "https://your-app.vercel.app/token?uid=YOUR_UID&password=YOUR_PASSWORD"</code>
                </div>
            </div>
            
            <div class="footer">
                Made with ❤️ by XANAF • Free Fire JWT Generator v1.1
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/token', methods=['GET'])
def token_endpoint():
    """
    Generate JWT token for Free Fire account
    GET /token?uid={uid}&password={password}
    """
    uid = request.args.get('uid')
    password = request.args.get('password')
    
    if not uid or not password:
        return jsonify({
            "success": False,
            "message": "Missing parameters. Required: uid, password",
            "timestamp": datetime.now().isoformat()
        }), 400
    
    result = generate_jwt(uid, password)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Free Fire JWT Generator",
        "version": "1.0.1",
        "timestamp": datetime.now().isoformat()
    }), 200

# Vercel handler
def handler(request, context):
    return app(request, context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
