import json
import random
import ssl
import gzip
import http.client
from io import BytesIO
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import protobuf modules
try:
    import MajoRLoGinrEq_pb2
    import MajoRLoGinrEs_pb2
except ImportError:
    # Fallback for Vercel environment
    from . import MajoRLoGinrEq_pb2
    from . import MajoRLoGinrEs_pb2

# Constants
KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'


def encrypt_proto(data: bytes) -> bytes:
    """Encrypt data using AES-CBC"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded = pad(data, AES.block_size)
    return cipher.encrypt(padded)


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
            return j.get('access_token'), j.get('open_id')
        return None, None
    except:
        return None, None


def major_login_protobuf(access_token, open_id):
    """Create and send MajorLogin request"""
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
        encrypted = encrypt_proto(serialized)
        
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
        conn.request("POST", "/MajorLogin", body=encrypted, headers=headers)
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


def decrypt_major_response(hex_data):
    """Decrypt MajorLogin response"""
    try:
        proto = MajoRLoGinrEs_pb2.MajorLoginRes()
        proto.ParseFromString(bytes.fromhex(hex_data))
        return proto
    except:
        return None


def generate_jwt(uid, password):
    """Generate JWT token for a single account"""
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
    
    access_token, open_id = get_access_token(uid, password)
    if not access_token or not open_id:
        result["message"] = "Invalid UID or Password."
        return result
    
    response_hex = major_login_protobuf(access_token, open_id)
    if not response_hex:
        result["message"] = "Account may be banned or invalid."
        return result
    
    login_data = decrypt_major_response(response_hex)
    if not login_data:
        result["message"] = "Failed to decrypt response."
        return result
    
    jwt_token = login_data.token
    if not jwt_token:
        result["message"] = "No JWT token received."
        return result
    
    result["success"] = True
    result["jwt_token"] = jwt_token
    result["account_uid"] = str(login_data.account_uid)
    result["region"] = getattr(login_data, 'region', 'IND')
    result["message"] = "JWT generated successfully!"
    
    return result


def handler(request):
    """Vercel serverless function handler"""
    
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    # Handle preflight
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # GET endpoints
    if request.method == 'GET':
        if request.path == '/':
            return {
                'statusCode': 200,
                'headers': {**headers, 'Content-Type': 'application/json'},
                'body': json.dumps({
                    "service": "JWT Generator API",
                    "version": "1.0",
                    "endpoints": {
                        "/": "GET - API info",
                        "/health": "GET - Health check",
                        "/generate": "POST - Generate JWT for single account",
                        "/generate_batch": "POST - Generate JWT for multiple accounts"
                    },
                    "deployed_on": "Vercel"
                })
            }
        
        if request.path == '/health':
            return {
                'statusCode': 200,
                'headers': {**headers, 'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat()
                })
            }
        
        return {
            'statusCode': 404,
            'headers': {**headers, 'Content-Type': 'application/json'},
            'body': json.dumps({"error": "Endpoint not found"})
        }
    
    # POST endpoints
    if request.method == 'POST':
        try:
            body = json.loads(request.body) if request.body else {}
        except:
            body = {}
        
        # Generate single
        if request.path == '/generate' or request.path == '/api/generate':
            uid = body.get('uid', '').strip()
            password = body.get('password', '').strip()
            
            if not uid or not password:
                return {
                    'statusCode': 400,
                    'headers': {**headers, 'Content-Type': 'application/json'},
                    'body': json.dumps({"error": "UID and password are required"})
                }
            
            result = generate_jwt(uid, password)
            status_code = 200 if result["success"] else 400
            
            return {
                'statusCode': status_code,
                'headers': {**headers, 'Content-Type': 'application/json'},
                'body': json.dumps(result)
            }
        
        # Generate batch
        if request.path == '/generate_batch' or request.path == '/api/generate_batch':
            accounts = body.get('accounts', [])
            
            if not accounts:
                return {
                    'statusCode': 400,
                    'headers': {**headers, 'Content-Type': 'application/json'},
                    'body': json.dumps({"error": "No accounts provided"})
                }
            
            results = []
            success_count = 0
            failed_count = 0
            
            for account in accounts:
                uid = account.get('uid', '').strip()
                password = account.get('password', '').strip()
                
                result = generate_jwt(uid, password)
                if result["success"]:
                    success_count += 1
                else:
                    failed_count += 1
                results.append(result)
            
            return {
                'statusCode': 200,
                'headers': {**headers, 'Content-Type': 'application/json'},
                'body': json.dumps({
                    "total": len(accounts),
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "results": results,
                    "timestamp": datetime.now().isoformat()
                })
            }
        
        return {
            'statusCode': 404,
            'headers': {**headers, 'Content-Type': 'application/json'},
            'body': json.dumps({"error": "Endpoint not found"})
        }
    
    return {
        'statusCode': 405,
        'headers': {**headers, 'Content-Type': 'application/json'},
        'body': json.dumps({"error": "Method not allowed"})
      }
