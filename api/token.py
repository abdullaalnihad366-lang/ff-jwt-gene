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
import http.client
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Import protobuf classes
try:
    import MajoRLoGinrEq_pb2
    import MajoRLoGinrEs_pb2
except ImportError:
    # Try to find the files in the root directory
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    import MajoRLoGinrEq_pb2
    import MajoRLoGinrEs_pb2

app = Flask(__name__)

# Constants
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

def encrypt_proto(data: bytes) -> bytes:
    """Encrypt protobuf data using AES-CBC"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(data, AES.block_size)
    return cipher.encrypt(padded)

def decrypt_response(encrypted_data: bytes) -> bytes:
    """Decrypt AES-CBC encrypted data"""
    try:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted = cipher.decrypt(encrypted_data)
        return unpad(decrypted, AES.block_size)
    except:
        return None

def get_access_token(uid, password):
    """Get access token from Garena"""
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }
    data = {
        "uid": str(uid),
        "password": str(password),
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    try:
        r = requests.post(url, headers=headers, data=data, timeout=15)
        if r.status_code == 200:
            j = r.json()
            access_token = j.get('access_token')
            open_id = j.get('open_id')
            if access_token and open_id:
                return access_token, open_id
        return None, None
    except Exception as e:
        return None, None

def create_major_login(access_token, open_id):
    """Create encrypted MajorLogin request"""
    try:
        major_login = MajoRLoGinrEq_pb2.MajorLogin()
        major_login.event_time = str(datetime.now())[:-7]
        major_login.game_name = "free fire"
        major_login.platform_id = 2
        major_login.client_version = "1.126.2"
        major_login.client_version_code = "2024010012"
        major_login.system_software = "Android OS 11 / API-30 (RQ3A.210805.001)"
        major_login.system_hardware = "Handheld"
        major_login.device_type = "Handheld"
        major_login.telecom_operator = "Verizon"
        major_login.network_operator_a = "Verizon"
        major_login.network_type = "WIFI"
        major_login.network_type_a = "WIFI"
        major_login.screen_width = 1080
        major_login.screen_height = 2400
        major_login.screen_dpi = "440"
        major_login.processor_details = "ARMv8"
        major_login.cpu_type = 2
        major_login.cpu_architecture = "64"
        major_login.memory = 6144
        major_login.gpu_renderer = "Adreno (TM) 650"
        major_login.gpu_version = "OpenGL ES 3.2 V@1.50"
        major_login.graphics_api = "OpenGLES3"
        major_login.unique_device_id = f"Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c{random.randint(10,99)}"
        major_login.client_ip = ""
        major_login.language = "en"
        major_login.open_id = open_id
        major_login.open_id_type = "4"
        major_login.login_open_id_type = 4
        major_login.access_token = access_token
        major_login.login_by = 3
        major_login.platform_sdk_id = 2
        major_login.origin_platform_type = "4"
        major_login.primary_platform_type = "4"
        
        memory_available = major_login.memory_available
        memory_available.version = 55
        memory_available.hidden_value = 81
        
        major_login.external_storage_total = 128512
        major_login.external_storage_available = random.randint(38000, 52000)
        major_login.internal_storage_total = 110731
        major_login.internal_storage_available = random.randint(18000, 32000)
        major_login.game_disk_storage_total = 26628
        major_login.game_disk_storage_available = random.randint(18000, 25000)
        major_login.external_sdcard_total_storage = 119234
        major_login.external_sdcard_avail_storage = random.randint(25000, 60000)
        major_login.library_path = f"/data/app/~~{random.randint(100,999)}/base.apk"
        major_login.library_token = "hash|base.apk"
        major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
        major_login.supported_astc_bitset = 16383
        major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
        major_login.loading_time = random.randint(9000, 18000)
        major_login.release_channel = "android"
        major_login.channel_type = 3
        major_login.reg_avatar = 1
        major_login.if_push = 1
        major_login.is_vpn = 0
        major_login.android_engine_init_flag = 110009
        
        serialized = major_login.SerializeToString()
        return encrypt_proto(serialized)
    except Exception as e:
        print(f"Error creating major login: {e}")
        return None

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
        print(f"Error sending major login: {e}")
        return None

def parse_major_response(hex_data):
    """Parse MajorLogin response using protobuf"""
    try:
        proto = MajoRLoGinrEs_pb2.MajorLoginRes()
        proto.ParseFromString(bytes.fromhex(hex_data))
        
        result = {}
        if hasattr(proto, 'token'):
            result['token'] = proto.token
        if hasattr(proto, 'account_uid'):
            result['account_uid'] = str(proto.account_uid)
        if hasattr(proto, 'region'):
            result['region'] = proto.region
            
        return result
    except Exception as e:
        print(f"Error parsing response: {e}")
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
        if not major_login_data:
            result["message"] = "Failed to create MajorLogin request."
            return result
            
        response_hex = send_major_login(major_login_data)
        
        if not response_hex:
            result["message"] = "Failed to get response from MajorLogin. Account may be banned or invalid."
            return result
        
        # Step 3: Parse response using protobuf
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

@app.route('/')
def index():
    """Simple HTML interface"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Free Fire JWT Generator</title>
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
            .test-form {
                background: rgba(255,255,255,0.03);
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
            .test-form input {
                width: 100%;
                padding: 10px 15px;
                margin: 8px 0;
                background: #0a0a1a;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 6px;
                color: #e0e0e0;
                font-size: 1em;
            }
            .test-form input:focus {
                outline: none;
                border-color: #ff0066;
            }
            .test-form button {
                width: 100%;
                padding: 12px;
                background: #ff0066;
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 1.1em;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }
            .test-form button:hover {
                background: #cc0055;
            }
            .result-box {
                display: none;
                margin-top: 15px;
                padding: 15px;
                border-radius: 8px;
                background: #0a0a1a;
                border: 1px solid rgba(255,255,255,0.05);
            }
            .result-box.show {
                display: block;
            }
            .result-box .label {
                color: #888;
                font-size: 0.85em;
            }
            .result-box .value {
                color: #00e676;
                word-break: break-all;
                font-size: 0.9em;
            }
            .result-box .value.error {
                color: #ff1744;
            }
            .copy-btn {
                background: rgba(0,230,118,0.1);
                border: 1px solid rgba(0,230,118,0.2);
                color: #00e676;
                padding: 4px 12px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.8em;
                margin-left: 10px;
            }
            .copy-btn:hover {
                background: rgba(0,230,118,0.2);
            }
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

            <div class="test-form">
                <h3 style="color:#ffd700;margin-bottom:15px;">🧪 Test Generator</h3>
                <input type="text" id="uid" placeholder="UID (e.g., 123456789)" required>
                <input type="password" id="password" placeholder="Password" required>
                <button onclick="generateToken()">Generate JWT Token</button>
                <div id="result" class="result-box">
                    <div class="label">Status:</div>
                    <div id="status" class="value"></div>
                    <div class="label" style="margin-top:10px;">JWT Token:</div>
                    <div id="token" class="value" style="font-size:0.8em;"></div>
                    <div class="label" style="margin-top:10px;">Account UID:</div>
                    <div id="account-uid" class="value"></div>
                    <div class="label" style="margin-top:10px;">Region:</div>
                    <div id="region" class="value"></div>
                </div>
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

            <div class="footer">
                Made with ❤️ by XANAF • Free Fire JWT Generator v1.1
            </div>
        </div>

        <script>
            async function generateToken() {
                const uid = document.getElementById('uid').value.trim();
                const password = document.getElementById('password').value.trim();
                const resultDiv = document.getElementById('result');
                const statusEl = document.getElementById('status');
                const tokenEl = document.getElementById('token');
                const accountUidEl = document.getElementById('account-uid');
                const regionEl = document.getElementById('region');

                if (!uid || !password) {
                    alert('Please enter both UID and Password');
                    return;
                }

                resultDiv.classList.add('show');
                statusEl.textContent = 'Generating...';
                statusEl.className = 'value';
                tokenEl.textContent = '';
                accountUidEl.textContent = '';
                regionEl.textContent = '';

                try {
                    const response = await fetch(`/token?uid=${encodeURIComponent(uid)}&password=${encodeURIComponent(password)}`);
                    const data = await response.json();

                    if (data.success) {
                        statusEl.textContent = '✅ Success';
                        statusEl.className = 'value success';
                        tokenEl.textContent = data.jwt_token || 'Not found';
                        if (data.jwt_token) {
                            tokenEl.innerHTML = `<span style="word-break:break-all;">${data.jwt_token}</span> <button class="copy-btn" onclick="copyText('${data.jwt_token}')">Copy</button>`;
                        }
                        accountUidEl.textContent = data.account_uid || 'N/A';
                        regionEl.textContent = data.region || 'N/A';
                    } else {
                        statusEl.textContent = `❌ ${data.message}`;
                        statusEl.className = 'value error';
                        tokenEl.textContent = 'None';
                        accountUidEl.textContent = 'N/A';
                        regionEl.textContent = 'N/A';
                    }
                } catch (error) {
                    statusEl.textContent = '❌ Network error. Please try again.';
                    statusEl.className = 'value error';
                }
            }

            function copyText(text) {
                navigator.clipboard.writeText(text).then(() => {
                    alert('Token copied to clipboard!');
                }).catch(() => {
                    const input = document.createElement('input');
                    input.value = text;
                    document.body.appendChild(input);
                    input.select();
                    document.execCommand('copy');
                    document.body.removeChild(input);
                    alert('Token copied to clipboard!');
                });
            }
        </script>
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
