import random
from datetime import datetime
from utils.crypto import encrypt_proto

# Import protobuf classes
try:
    import MajoRLoGinrEq_pb2
    import MajoRLoGinrEs_pb2
except ImportError:
    # Fallback for Vercel deployment
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import MajoRLoGinrEq_pb2
    import MajoRLoGinrEs_pb2

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
        return None
