"""
Yascan - Crypto Manager (Versión Ligera)
Encriptación AES-256 + ECDSA para firmas digitales
"""

import pyaes
import hashlib
import os
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import json

class CryptoManager:
    """Gestor de criptografía usando AES-256 y ECDSA"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        
    def generate_keypair(self):
        """Genera par de claves ECDSA"""
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
        return self.get_public_key_hex()
    
    def get_public_key_hex(self):
        """Obtiene clave pública en formato hex"""
        if self.public_key:
            return self.public_key.to_string().hex()
        return None
    
    def save_keys(self, filepath, password):
        """Guarda claves encriptadas"""
        if not self.private_key:
            raise ValueError("No hay claves para guardar")
        
        # Derivar clave de encriptación del password
        key = hashlib.sha256(password.encode()).digest()
        
        # Obtener clave privada como bytes
        private_key_bytes = self.private_key.to_string()
        
        # Encriptar con AES-256
        aes = pyaes.AESModeOfOperationCTR(key)
        encrypted = aes.encrypt(private_key_bytes)
        
        # Guardar
        with open(filepath, 'wb') as f:
            f.write(encrypted)
    
    def load_keys(self, filepath, password):
        """Carga claves desde archivo"""
        # Derivar clave de desencriptación
        key = hashlib.sha256(password.encode()).digest()
        
        # Leer archivo
        with open(filepath, 'rb') as f:
            encrypted = f.read()
        
        # Desencriptar
        aes = pyaes.AESModeOfOperationCTR(key)
        private_key_bytes = aes.decrypt(encrypted)
        
        # Restaurar claves
        self.private_key = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()
    
    def encrypt_message(self, message, shared_secret):
        """Encripta mensaje con AES-256"""
        # Derivar clave de 32 bytes del secreto compartido
        key = hashlib.sha256(shared_secret.encode()).digest()
        
        # Generar IV aleatorio
        iv = os.urandom(16)
        
        # Encriptar con AES-256-CTR
        aes = pyaes.AESModeOfOperationCTR(key, counter=pyaes.Counter(int.from_bytes(iv, 'big')))
        
        message_bytes = message.encode('utf-8')
        encrypted = aes.encrypt(message_bytes)
        
        # Retornar IV + mensaje encriptado en base64
        result = iv + encrypted
        return base64.b64encode(result).decode('utf-8')
    
    def decrypt_message(self, encrypted_message, shared_secret):
        """Desencripta mensaje AES-256"""
        # Derivar clave
        key = hashlib.sha256(shared_secret.encode()).digest()
        
        # Decodificar base64
        data = base64.b64decode(encrypted_message.encode('utf-8'))
        
        # Extraer IV y mensaje
        iv = data[:16]
        encrypted = data[16:]
        
        # Desencriptar
        aes = pyaes.AESModeOfOperationCTR(key, counter=pyaes.Counter(int.from_bytes(iv, 'big')))
        decrypted = aes.decrypt(encrypted)
        
        return decrypted.decode('utf-8')
    
    def sign_message(self, message):
        """Firma mensaje con ECDSA"""
        if not self.private_key:
            raise ValueError("No hay clave privada para firmar")
        
        message_hash = hashlib.sha256(message.encode()).digest()
        signature = self.private_key.sign(message_hash)
        return base64.b64encode(signature).decode('utf-8')
    
    def verify_signature(self, message, signature, public_key_hex):
        """Verifica firma ECDSA"""
        try:
            # Reconstruir clave pública
            public_key_bytes = bytes.fromhex(public_key_hex)
            vk = VerifyingKey.from_string(public_key_bytes, curve=SECP256k1)
            
            # Verificar
            message_hash = hashlib.sha256(message.encode()).digest()
            signature_bytes = base64.b64decode(signature.encode('utf-8'))
            
            return vk.verify(signature_bytes, message_hash)
        except:
            return False
    
    def derive_shared_secret(self, peer_public_key_hex):
        """Deriva secreto compartido simple (no ECDH completo, versión simplificada)"""
        # En versión completa usaríamos ECDH, aquí usamos hash simple
        my_public = self.get_public_key_hex()
        combined = sorted([my_public, peer_public_key_hex])
        secret = hashlib.sha256(''.join(combined).encode()).hexdigest()
        return secret

# Utilidad para generar IDs únicos
def generate_identity_id():
    """Genera ID único para identidad"""
    return hashlib.sha256(os.urandom(32)).hexdigest()[:16]
