# Arquitectura de Seguridad - DeepChat Secure

## 🔒 Modelo de Amenazas

### Amenazas Consideradas

1. **Interceptación de Comunicaciones**
   - Protección: Tor (3 saltos) + Encriptación E2E
   - Resultado: Tráfico anónimo e incomprensible para observadores

2. **Compromiso del Servidor**
   - Protección: No hay servidores centrales (P2P)
   - Resultado: Sin punto único de fallo

3. **Análisis de Metadatos**
   - Protección: Servicios ocultos Tor + Sin almacenamiento en la nube
   - Resultado: Metadatos mínimos expuestos

4. **Ataques de Fuerza Bruta**
   - Protección: RSA-4096 + Contraseñas fuertes
   - Resultado: Computacionalmente infeasible

5. **Compromiso del Dispositivo**
   - Protección: Encriptación en reposo + Auto-bloqueo
   - Resultado: Datos protegidos incluso con acceso físico

### Amenazas NO Consideradas

⚠️ Esta aplicación NO protege contra:
- Malware en el dispositivo
- Ataques de correlación de tiempo avanzados
- Adversarios con recursos ilimitados (estado-nación)
- Compromisos de la red Tor misma
- Ingeniería social

## 🛡️ Capas de Seguridad

### Capa 1: Transporte Anónimo (Tor)

```
Usuario A → Guardia → Nodo Medio → Nodo Salida → Usuario B
          [Encript1]  [Encript2]   [Encript3]
```

**Características:**
- 3 saltos de enrutamiento cebolla
- Cada nodo solo conoce el anterior y siguiente
- Circuitos rotan periódicamente
- Direcciones .onion v3 (56 caracteres)

**Configuración:**
```python
# tor_manager.py
HiddenServiceDir /path/to/hidden_service
HiddenServicePort 80 127.0.0.1:9999
ConnectionPadding 1
CircuitPadding 1
```

### Capa 2: Encriptación End-to-End

#### 2.1 Generación de Claves

```python
# Generación RSA-4096
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096
)
```

**Entropía:** 4096 bits (equivale a ~2^4096 posibilidades)
**Resistencia:** Seguro hasta 2030+ según NIST

#### 2.2 Protocolo de Encriptación Híbrida

```
1. Generar clave simétrica Fernet (AES-256)
2. Encriptar mensaje con Fernet
3. Encriptar clave Fernet con RSA público del destinatario
4. Enviar: {clave_encriptada, mensaje_encriptado}
```

**Ejemplo de flujo:**

```python
# Encriptación
symmetric_key = Fernet.generate_key()  # 256 bits
fernet = Fernet(symmetric_key)
encrypted_msg = fernet.encrypt(mensaje)
encrypted_key = rsa_public.encrypt(symmetric_key)

# Paquete final
package = {
    'encrypted_key': base64(encrypted_key),
    'encrypted_message': base64(encrypted_msg)
}
```

**Ventajas:**
- RSA para seguridad (intercambio de claves)
- Fernet para velocidad (encriptación de datos)
- Clave simétrica única por mensaje (forward secrecy parcial)

### Capa 3: Autenticación de Identidad

#### 3.1 Firmas Digitales

```python
# Firma
signature = private_key.sign(
    mensaje,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Verificación
public_key.verify(signature, mensaje, ...)
```

**Propiedades:**
- No repudio: Solo el poseedor de la clave privada puede firmar
- Integridad: Cualquier alteración invalida la firma
- Autenticación: Verifica la identidad del remitente

#### 3.2 Fingerprints

```python
# Generar fingerprint único
public_bytes = public_key.public_bytes(...)
digest = hashes.Hash(hashes.SHA256())
digest.update(public_bytes)
fingerprint = digest.finalize()

# Formato legible: AA:BB:CC:DD:...
```

**Uso:** Verificación out-of-band de identidad (ej: llamada telefónica, QR en persona)

### Capa 4: Protección de Datos en Reposo

```python
# Claves privadas encriptadas con contraseña
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(password)
)
```

**Almacenamiento:**
```
~/.deepchat/
├── private_key.pem    # Encriptado con contraseña del usuario
├── public_key.pem     # No sensible
├── identity.json      # Metadatos (no sensibles)
└── messages/
    └── [contacto].json  # Mensajes almacenados localmente
```

## 🔐 Análisis de Fortaleza Criptográfica

### RSA-4096

**Bits de seguridad:** ~140 bits
**Equivalente simétrico:** AES-192

**Resistencia estimada:**
- Fuerza bruta: 2^4096 operaciones (físicamente imposible)
- Factorización clásica: Infeasible con tecnología actual
- Computadoras cuánticas (Algoritmo de Shor): Vulnerable (futuro)

**Tiempo para romper:**
- Con computadora personal: Más de la edad del universo
- Con supercomputadora: Millones de años
- Con computadora cuántica (futura): Años a décadas

### AES-256 (Fernet)

**Bits de seguridad:** 256 bits
**Posibles claves:** 2^256 (~10^77)

**Resistencia:**
- Fuerza bruta: Computacionalmente imposible
- Ataques conocidos: Ninguno práctico
- Computadoras cuánticas (Algoritmo de Grover): Reducido a ~2^128 (aún seguro)

**Tiempo para romper:**
- Con toda la potencia computacional del planeta: Billones de años

### SHA-256

**Resistencia a colisiones:** 2^128 operaciones
**Resistencia a preimagen:** 2^256 operaciones

**Estado:** No se conocen vulnerabilidades prácticas

## 🚨 Vectores de Ataque Residuales

### 1. Análisis de Tráfico

**Amenaza:** Adversario correlaciona tiempos de envío/recepción

**Mitigación:**
- Padding de mensajes
- Timing aleatorio
- Cover traffic (ruido)

**Implementación sugerida:**
```python
# Agregar delay aleatorio
import random
delay = random.uniform(0.5, 3.0)
time.sleep(delay)
```

### 2. Ataques de Canal Lateral

**Amenaza:** Análisis de consumo de energía, emisiones EM

**Mitigación:**
- Limitada en software
- Requiere protección física del dispositivo

### 3. Malware en el Dispositivo

**Amenaza:** Keylogger, screenshot, acceso a memoria

**Mitigación:**
- Detección de root/jailbreak
- Ofuscación de código
- Verificación de integridad

**Implementación sugerida:**
```python
# Detectar root en Android
from jnius import autoclass
def is_rooted():
    File = autoclass('java.io.File')
    paths = ['/system/app/Superuser.apk', '/system/xbin/su']
    return any(File(p).exists() for p in paths)
```

### 4. Compromiso de Red Tor

**Amenaza:** Adversario controla múltiples nodos Tor

**Probabilidad:**
- Control de guardia: ~5-10% de nodos
- Correlación de tiempo: Requiere control de guardia + salida
- Para servicios ocultos: Más difícil (no hay nodo de salida)

**Mitigación:**
- Usar guardas específicos (EntryNodes)
- Rotación frecuente de circuitos
- Evitar patrones de uso predecibles

## 📊 Comparación con Otras Apps

| Característica | DeepChat | Signal | WhatsApp | Telegram |
|---------------|----------|--------|----------|----------|
| E2E Encryption | ✅ RSA+AES | ✅ Signal Protocol | ✅ Signal Protocol | ⚠️ Opcional |
| Anonimato | ✅ Tor | ❌ | ❌ | ❌ |
| P2P | ✅ | ❌ | ❌ | ❌ |
| Sin metadatos | ✅ | ⚠️ | ❌ | ❌ |
| Open Source | ✅ | ✅ | ❌ | ⚠️ Parcial |
| Almacenamiento | 📱 Local | 📱 Local + ☁️ | ☁️ | ☁️ |

**Ventajas de DeepChat:**
- ✅ Máximo anonimato (Tor)
- ✅ Sin servidores centrales
- ✅ Sin metadatos

**Desventajas:**
- ❌ Latencia más alta (Tor)
- ❌ Menor ancho de banda
- ❌ Requiere más configuración

## 🔄 Forward Secrecy

**Estado actual:** Parcial (clave simétrica única por mensaje)

**Mejora futura:** Implementar Double Ratchet (Signal Protocol)

```python
# Concepto de Double Ratchet
class RatchetState:
    def __init__(self):
        self.dh_self = generate_dh_keypair()
        self.dh_remote = None
        self.root_key = None
        self.chain_keys = {}
    
    def rotate_keys(self):
        # Generar nuevo par DH
        self.dh_self = generate_dh_keypair()
        # Derivar nueva root key
        self.root_key = kdf(dh(self.dh_self, self.dh_remote))
```

## 🛠️ Recomendaciones de Hardening

### 1. Para Usuarios

✅ **Hacer:**
- Usar contraseña fuerte (12+ caracteres, alfanumérica)
- Verificar fingerprints de contactos
- Actualizar la app regularmente
- Usar modo incógnito en navegador
- Deshabilitar backups en la nube

❌ **No hacer:**
- Hacer root/jailbreak del dispositivo
- Instalar apps de fuentes desconocidas
- Compartir capturas de pantalla
- Usar en redes WiFi públicas sin VPN adicional

### 2. Para Desarrolladores

```python
# Limpiar memoria sensible
import ctypes
def secure_delete(data):
    """Sobrescribir datos en memoria"""
    ctypes.memset(id(data), 0, len(data))

# Verificar integridad de código
import hashlib
def verify_integrity():
    """Verificar que el código no ha sido modificado"""
    # Implementar verificación de checksums
```

### 3. Configuración Avanzada de Tor

```
# torrc personalizado
EntryNodes {COUNTRY_CODES}
ExitNodes {COUNTRY_CODES}
StrictNodes 1
UseEntryGuards 1
NumEntryGuards 3
```

## 📈 Auditoría y Cumplimiento

### Logs de Seguridad

```python
# Nunca loggear:
# - Claves privadas
# - Contraseñas
# - Contenido de mensajes
# - Direcciones .onion de contactos

# Sí loggear:
# - Intentos de conexión fallidos
# - Errores de desencriptación
# - Cambios de configuración
```

### Retención de Datos

**Política:** Mínima retención necesaria

- Claves: Hasta que el usuario las elimine
- Mensajes: Locales, usuario controla
- Logs: Máximo 7 días
- Metadatos: Solo lo esencial

## 🔮 Próximas Mejoras de Seguridad

1. **Perfect Forward Secrecy**
   - Implementar Double Ratchet
   - Rotación automática de claves

2. **Post-Quantum Cryptography**
   - Migrar a CRYSTALS-Kyber (KEM)
   - Mantener compatibilidad con RSA

3. **Canary de Seguridad**
   - Publicar mensualmente
   - Alertar sobre compromisos

4. **Reproducibilidad de Builds**
   - Builds determinísticos
   - Verificación independiente

5. **Auditoría Externa**
   - Code review por expertos
   - Pentesting profesional

---

**Última revisión:** Enero 2025
**Versión del documento:** 1.0
**Mantenedor:** Equipo de Seguridad DeepChat
