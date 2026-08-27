import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

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
