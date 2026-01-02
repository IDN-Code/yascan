"""
Utilidades para DeepChat Secure
Funciones auxiliares y helpers
"""

import hashlib
import base64
import qrcode
from io import BytesIO
import json
import os
from datetime import datetime
import re


class Utils:
    """Clase con métodos de utilidad"""
    
    @staticmethod
    def generate_qr_code(data, size=10):
        """
        Generar código QR
        
        Args:
            data: Datos a codificar
            size: Tamaño del QR
            
        Returns:
            Imagen PIL del QR code
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        return qr.make_image(fill_color="black", back_color="white")
    
    @staticmethod
    def qr_to_base64(qr_image):
        """
        Convertir imagen QR a base64
        
        Args:
            qr_image: Imagen PIL del QR
            
        Returns:
            String base64 de la imagen
        """
        buffer = BytesIO()
        qr_image.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    @staticmethod
    def format_fingerprint(fingerprint):
        """
        Formatear fingerprint en grupos legibles
        
        Args:
            fingerprint: String del fingerprint
            
        Returns:
            Fingerprint formateado (ej: AA:BB:CC:DD)
        """
        # Si ya está formateado, retornar
        if ':' in fingerprint:
            return fingerprint
        
        # Formatear en pares separados por :
        return ':'.join([fingerprint[i:i+2] for i in range(0, len(fingerprint), 2)])
    
    @staticmethod
    def validate_onion_address(address):
        """
        Validar formato de dirección .onion v3
        
        Args:
            address: Dirección .onion a validar
            
        Returns:
            True si es válida, False si no
        """
        # v3 onion: 56 caracteres + .onion
        pattern = r'^[a-z2-7]{56}\.onion$'
        return bool(re.match(pattern, address))
    
    @staticmethod
    def truncate_address(address, length=20):
        """
        Truncar dirección .onion para mostrar
        
        Args:
            address: Dirección .onion
            length: Longitud a mostrar
            
        Returns:
            Dirección truncada con ...
        """
        if len(address) <= length:
            return address
        
        return address[:length] + '...'
    
    @staticmethod
    def format_timestamp(timestamp):
        """
        Formatear timestamp para mostrar
        
        Args:
            timestamp: ISO timestamp o datetime
            
        Returns:
            String formateado (ej: "14:30" o "Ayer 14:30")
        """
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp)
        else:
            dt = timestamp
        
        now = datetime.now()
        
        # Si es hoy
        if dt.date() == now.date():
            return dt.strftime('%H:%M')
        
        # Si es ayer
        yesterday = now.date() - timedelta(days=1)
        if dt.date() == yesterday:
            return f"Ayer {dt.strftime('%H:%M')}"
        
        # Si es esta semana
        if (now - dt).days < 7:
            return dt.strftime('%a %H:%M')
        
        # Más antiguo
        return dt.strftime('%d/%m/%Y')
    
    @staticmethod
    def format_file_size(bytes_size):
        """
        Formatear tamaño de archivo
        
        Args:
            bytes_size: Tamaño en bytes
            
        Returns:
            String formateado (ej: "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        
        return f"{bytes_size:.1f} TB"
    
    @staticmethod
    def generate_message_id():
        """
        Generar ID único para mensaje
        
        Returns:
            String único basado en timestamp y random
        """
        import random
        timestamp = int(datetime.now().timestamp() * 1000)
        random_part = random.randint(1000, 9999)
        
        return f"{timestamp}_{random_part}"
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash de contraseña con salt
        
        Args:
            password: Contraseña a hashear
            salt: Salt (se genera si no se provee)
            
        Returns:
            Tuple (hash, salt)
        """
        if salt is None:
            salt = os.urandom(32)
        
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        return key, salt
    
    @staticmethod
    def verify_password(password, stored_hash, salt):
        """
        Verificar contraseña
        
        Args:
            password: Contraseña a verificar
            stored_hash: Hash almacenado
            salt: Salt usado
            
        Returns:
            True si coincide, False si no
        """
        key, _ = Utils.hash_password(password, salt)
        return key == stored_hash
    
    @staticmethod
    def sanitize_filename(filename):
        """
        Sanitizar nombre de archivo
        
        Args:
            filename: Nombre de archivo
            
        Returns:
            Nombre sanitizado
        """
        # Remover caracteres peligrosos
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Limitar longitud
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
    
    @staticmethod
    def calculate_checksum(data):
        """
        Calcular checksum SHA-256 de datos
        
        Args:
            data: Datos (bytes o string)
            
        Returns:
            Checksum hexadecimal
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def split_data_chunks(data, chunk_size=4096):
        """
        Dividir datos en chunks
        
        Args:
            data: Datos a dividir
            chunk_size: Tamaño de cada chunk
            
        Yields:
            Chunks de datos
        """
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]
    
    @staticmethod
    def merge_chunks(chunks):
        """
        Unir chunks de datos
        
        Args:
            chunks: Lista de chunks
            
        Returns:
            Datos unidos
        """
        if isinstance(chunks[0], bytes):
            return b''.join(chunks)
        else:
            return ''.join(chunks)


class ContactVerifier:
    """Verificador de contactos"""
    
    @staticmethod
    def create_verification_code(public_key1, public_key2):
        """
        Crear código de verificación de contacto
        
        Args:
            public_key1: Clave pública usuario 1
            public_key2: Clave pública usuario 2
            
        Returns:
            Código de verificación de 6 dígitos
        """
        # Concatenar claves en orden alfabético
        keys = sorted([public_key1, public_key2])
        combined = ''.join(keys)
        
        # Hash
        digest = hashlib.sha256(combined.encode()).digest()
        
        # Tomar primeros 4 bytes y convertir a número de 6 dígitos
        num = int.from_bytes(digest[:4], byteorder='big')
        code = num % 1000000
        
        return f"{code:06d}"
    
    @staticmethod
    def format_verification_code(code):
        """
        Formatear código de verificación
        
        Args:
            code: Código de 6 dígitos
            
        Returns:
            Código formateado (ej: "123-456")
        """
        return f"{code[:3]}-{code[3:]}"


class NetworkMonitor:
    """Monitor de estado de red"""
    
    def __init__(self):
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'connection_attempts': 0,
            'successful_connections': 0,
            'failed_connections': 0,
        }
    
    def record_message_sent(self, size):
        """Registrar mensaje enviado"""
        self.stats['messages_sent'] += 1
        self.stats['bytes_sent'] += size
    
    def record_message_received(self, size):
        """Registrar mensaje recibido"""
        self.stats['messages_received'] += 1
        self.stats['bytes_received'] += size
    
    def record_connection_attempt(self, success=True):
        """Registrar intento de conexión"""
        self.stats['connection_attempts'] += 1
        if success:
            self.stats['successful_connections'] += 1
        else:
            self.stats['failed_connections'] += 1
    
    def get_stats(self):
        """Obtener estadísticas"""
        return self.stats.copy()
    
    def get_success_rate(self):
        """Calcular tasa de éxito de conexiones"""
        attempts = self.stats['connection_attempts']
        if attempts == 0:
            return 0.0
        
        return self.stats['successful_connections'] / attempts * 100
    
    def reset_stats(self):
        """Resetear estadísticas"""
        for key in self.stats:
            self.stats[key] = 0


class Logger:
    """Sistema de logging seguro"""
    
    def __init__(self, log_file='~/.deepchat/app.log'):
        self.log_file = os.path.expanduser(log_file)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log(self, level, message):
        """
        Escribir log (nunca loggear datos sensibles)
        
        Args:
            level: Nivel (INFO, WARNING, ERROR)
            message: Mensaje a loggear
        """
        timestamp = datetime.now().isoformat()
        
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def info(self, message):
        """Log nivel INFO"""
        self.log('INFO', message)
    
    def warning(self, message):
        """Log nivel WARNING"""
        self.log('WARNING', message)
    
    def error(self, message):
        """Log nivel ERROR"""
        self.log('ERROR', message)


if __name__ == '__main__':
    # Tests
    print("=== Test de Utils ===\n")
    
    # Test validación de dirección .onion
    valid_onion = "thehiddenwiki3iyn5rw4mafvvhvjz6lqj5qzxqbhz5jgyd7s5jbqfqd.onion"
    invalid_onion = "invalid.onion"
    
    print(f"Dirección válida: {Utils.validate_onion_address(valid_onion)}")
    print(f"Dirección inválida: {Utils.validate_onion_address(invalid_onion)}")
    
    # Test código de verificación
    from crypto_manager import CryptoManager
    
    alice = CryptoManager()
    alice.generate_keypair()
    
    bob = CryptoManager()
    bob.generate_keypair()
    
    code = ContactVerifier.create_verification_code(
        alice.export_public_key(),
        bob.export_public_key()
    )
    
    print(f"\nCódigo de verificación: {ContactVerifier.format_verification_code(code)}")
    
    # Test QR
    print("\nGenerando QR code...")
    qr = Utils.generate_qr_code("thehiddenwiki3iyn5rw4mafvvhvjz6lqj5qzxqbhz5jgyd7s5jbqfqd.onion")
    print("QR generado exitosamente")
