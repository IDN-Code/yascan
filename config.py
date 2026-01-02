"""
Configuración de DeepChat Secure
"""

# Configuración de Red
NETWORK_CONFIG = {
    # Tor
    'tor_socks_port': 9050,
    'tor_control_port': 9051,
    'hidden_service_port': 9999,
    
    # Timeouts (en segundos)
    'connection_timeout': 30,
    'message_timeout': 10,
    'call_timeout': 60,
    
    # Reintentos
    'max_retries': 3,
    'retry_delay': 5,
}

# Configuración de Encriptación
CRYPTO_CONFIG = {
    # RSA
    'rsa_key_size': 4096,
    'rsa_exponent': 65537,
    
    # Opciones de serialización
    'key_format': 'PEM',
    
    # Password para claves (cambiar en producción)
    'key_password': 'change_this_in_production',
}

# Configuración de Video
VIDEO_CONFIG = {
    # Resolución
    'default_width': 640,
    'default_height': 480,
    
    # FPS
    'default_fps': 15,
    'min_fps': 5,
    'max_fps': 30,
    
    # Calidad JPEG (1-100)
    'default_quality': 50,
    'low_quality': 30,
    'high_quality': 80,
    
    # Buffer
    'frame_buffer_size': 5,
    'output_buffer_size': 10,
    
    # Cámara
    'default_camera_index': 0,
}

# Configuración de Audio
AUDIO_CONFIG = {
    'sample_rate': 44100,
    'channels': 1,  # Mono
    'chunk_size': 1024,
}

# Configuración de UI
UI_CONFIG = {
    'theme': 'dark',
    'font_size': 14,
    'show_timestamps': True,
    'show_read_receipts': True,
    'enable_notifications': True,
}

# Configuración de Almacenamiento
STORAGE_CONFIG = {
    'data_directory': '~/.deepchat',
    'max_message_history': 10000,
    'enable_auto_backup': True,
    'backup_interval_days': 7,
}

# Configuración de Seguridad
SECURITY_CONFIG = {
    # Auto-bloqueo
    'enable_auto_lock': True,
    'auto_lock_timeout': 300,  # 5 minutos
    
    # Mensajes
    'enable_self_destruct': False,
    'default_self_destruct_time': 3600,  # 1 hora
    
    # Verificación
    'require_fingerprint_verification': True,
    'enable_screenshot_protection': True,
}

# Configuración de Desarrollo
DEV_CONFIG = {
    'debug_mode': False,
    'verbose_logging': False,
    'enable_profiling': False,
    'mock_tor': False,  # Usar mock en lugar de Tor real (solo desarrollo)
}

# Constantes
APP_NAME = "DeepChat Secure"
APP_VERSION = "1.0.0"
MIN_ANDROID_API = 21
TARGET_ANDROID_API = 33
