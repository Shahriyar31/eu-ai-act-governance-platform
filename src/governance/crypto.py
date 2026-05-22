import os
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

KEYS_DIR = "keys"
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")

def init_keys():
    """
    Generates a secure 2048-bit RSA private/public key pair if it does not already exist.
    Stores the keys in the local directory 'keys/' as PEM files.
    """
    if not os.path.exists(KEYS_DIR):
        os.makedirs(KEYS_DIR)
        
    if not os.path.exists(PRIVATE_KEY_PATH) or not os.path.exists(PUBLIC_KEY_PATH):
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Serialize and write private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(pem_private)
            
        # Generate public key
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(pem_public)
        
        print("[*] Generated a new secure 2048-bit RSA key pair for audit log signing.")

def sign_data(data_bytes: bytes) -> str:
    """
    Signs bytes of data using our private key and PSS padding.
    Returns the signature as a hex-encoded string.
    """
    init_keys()  # Ensure keys exist
    
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
        
    # Generate signature using modern PSS padding and SHA-256
    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature.hex()

def verify_signature(data_bytes: bytes, signature_hex: str) -> bool:
    """
    Verifies a hex-encoded signature against data_bytes using our public key.
    Returns True if valid, False otherwise.
    """
    init_keys()  # Ensure keys exist
    
    try:
        with open(PUBLIC_KEY_PATH, "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read()
            )
            
        signature = bytes.fromhex(signature_hex)
        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        # If the signature does not match or key is corrupt, verification fails
        return False

def calculate_record_hash(action: str, system_name: str, payload: str, previous_hash: str) -> str:
    """
    Calculates a highly secure and deterministic SHA-256 hash representing a ledger record.
    Uses pipe delimiters to prevent 'hash collision' attacks.
    """
    input_str = f"{action}|{system_name}|{payload}|{previous_hash}"
    return hashlib.sha256(input_str.encode("utf-8")).hexdigest()
