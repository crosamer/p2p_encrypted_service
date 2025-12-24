import os, json, time, hmac, hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def generate_keypair():
    priv = ec.generate_private_key(ec.SECP384R1())
    return priv, priv.public_key()

def serialize_public_key(pub):
    return pub.public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    )

def deserialize_public_key(data):
    return serialization.load_pem_public_key(data)

def fingerprint(pubkey_bytes):
    return hashlib.sha256(pubkey_bytes).hexdigest()

def derive_shared_key(priv, pub):
    shared = priv.exchange(ec.ECDH(), pub)
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'p2p-chat',
    ).derive(shared)

def encrypt(key, payload: dict):
    aes = AESGCM(key)
    nonce = os.urandom(12)
    data = json.dumps(payload).encode()
    return nonce + aes.encrypt(nonce, data, None)

def decrypt(key, data):
    aes = AESGCM(key)
    nonce, ct = data[:12], data[12:]
    return json.loads(aes.decrypt(nonce, ct, None).decode())
