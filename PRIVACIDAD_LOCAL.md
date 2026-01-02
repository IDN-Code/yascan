# Privacidad Total: Almacenamiento 100% Local

## 🔒 GARANTÍA DE PRIVACIDAD

**DeepChat Secure NO guarda NADA en servidores externos.**  
**CERO datos en la nube.**  
**TODO permanece ÚNICAMENTE en tu dispositivo.**

---

## ✅ QUÉ SE GUARDA (Solo en TU dispositivo)

### 📱 Ubicación de Datos:

```
Android: /data/data/org.deepchat.deepchatsecure/files/.deepchat/
Linux:   ~/.deepchat/

├── private_key.pem           🔐 Tu clave privada (ENCRIPTADA)
├── public_key.pem            🔑 Tu clave pública
├── identity.json             👤 Tu identidad (.onion)
├── contacts.json             📇 Lista de contactos
│
├── messages/                 💬 Historial de chats
│   ├── [contacto1].json
│   └── [contacto2].json
│
├── groups/                   👥 Datos de grupos
│   ├── [grupo_id].json
│   └── [grupo_id]_messages.json
│
└── file_transfers/           📎 Archivos recibidos
    ├── documento.pdf
    └── imagen.jpg
```

### 🚫 Lo que NO se guarda en ningún lado:

❌ **Servidores centrales:** NO EXISTEN  
❌ **Base de datos en la nube:** NO HAY  
❌ **Backups automáticos:** NO SE HACEN  
❌ **Logs en servidor:** NO HAY SERVIDOR  
❌ **Metadatos remotos:** CERO  
❌ **Analytics/tracking:** NINGUNO  

---

## 🏠 Arquitectura: TODO es Local

### Modelo Tradicional (WhatsApp, Telegram, Signal):
```
Tu celular
    ↓
📤 ENVÍA datos a servidor
    ↓
☁️ SERVIDOR almacena metadatos
    ↓
📥 ENTREGA a destinatario
    ↓
Celular del otro
```

**Problemas:**
- ❌ Servidor sabe QUIÉN habla con QUIÉN
- ❌ Servidor sabe CUÁNDO hablas
- ❌ Servidor tiene tu número/email
- ❌ Pueden hackear/intervenir el servidor
- ❌ Gobierno puede pedir datos al servidor

### Modelo DeepChat (P2P Puro):
```
Tu celular ⟷ TOR (anónimo) ⟷ Celular del otro
    ↓                              ↓
GUARDA local              GUARDA local
```

**Ventajas:**
- ✅ NO hay servidor que sepa nada
- ✅ NO hay base de datos centralizada
- ✅ NO hay punto único de fallo
- ✅ NO pueden intervenir un servidor (no existe)
- ✅ NO hay qué hackear centralmente

---

## 🔐 Encriptación de Datos Locales

### Claves Privadas (Protección Extra):

```python
# Tu clave privada SE GUARDA ENCRIPTADA
private_key.pem ← Encriptada con tu contraseña

# Para leer la clave privada:
1. Necesitas el archivo (en TU dispositivo)
2. Necesitas la contraseña (en TU cabeza)

# Si pierdes el celular:
→ Tienen el archivo pero NO la contraseña
→ Encriptación: AES-256 con PBKDF2
→ Imposible de romper sin contraseña
```

### Mensajes (Encriptación Doble):

```
Mensaje guardado localmente:
1. Encriptado E2E (cuando lo recibiste)
2. Protegido por encriptación del dispositivo (Android)

Para leer tus mensajes se necesita:
- Acceso físico a tu celular
- PIN/contraseña de desbloqueo
- (Opcional) Contraseña de la app
```

---

## 🗑️ Borrado de Datos

### Tú controlas TODO:

```python
# Borrar conversación individual
def delete_conversation(contact_address):
    messages_file = f'~/.deepchat/messages/{contact_address}.json'
    os.remove(messages_file)
    # ELIMINADO PERMANENTEMENTE
    # NO hay copia en servidor (no hay servidor!)
```

### Opciones de Privacidad:

#### 1. Borrar Conversación:
```
Settings → Chat → Borrar conversación
→ Eliminado solo de TU dispositivo
→ El otro usuario conserva SU copia (en SU dispositivo)
```

#### 2. Borrar Mensajes Automáticamente:
```python
# En config.py
PRIVACY_CONFIG = {
    'auto_delete_messages': True,
    'delete_after_days': 7,  # Borrar después de 7 días
}
```

#### 3. Mensajes Auto-Destructivos:
```python
# Mensaje que se auto-borra después de leerse
send_self_destruct_message(
    text="Este mensaje se borrará en 1 hora",
    destroy_after_seconds=3600
)
```

#### 4. Modo Incógnito:
```python
# NO guardar NADA de esta conversación
Settings → Incognito Mode → ON
→ Mensajes se borran al cerrar el chat
→ Archivos se borran al salir
```

---

## 📲 Gestión de Archivos

### Archivos Recibidos:

```
Ubicación: ~/.deepchat/file_transfers/

Opciones:
1. Mantener en app (encriptados)
2. Exportar a galería/documentos
3. Borrar después de ver
```

### Control Total:

```python
# Ver archivos recibidos
ls ~/.deepchat/file_transfers/

# Borrar todos los archivos
rm -rf ~/.deepchat/file_transfers/*

# Borrar archivo específico
rm ~/.deepchat/file_transfers/documento.pdf
```

---

## 🌐 Comparación: DeepChat vs Otras Apps

| Aspecto | WhatsApp | Signal | Telegram | DeepChat |
|---------|----------|--------|----------|----------|
| **Servidor central** | ✅ Sí | ✅ Sí | ✅ Sí | ❌ NO |
| **Metadatos en servidor** | ✅ Muchos | ⚠️ Algunos | ✅ Muchos | ❌ CERO |
| **Tu número/email** | ✅ Requiere | ✅ Requiere | ✅ Requiere | ❌ NO |
| **Backup en nube** | ✅ Google Drive | ⚠️ Opcional | ✅ Nube Telegram | ❌ NO |
| **Logs del servidor** | ✅ Sí | ⚠️ Mínimos | ✅ Sí | ❌ NO HAY |
| **IP visible al servidor** | ✅ Sí | ✅ Sí | ✅ Sí | ❌ Tor (oculta) |
| **Pueden hackear servidor** | ✅ Posible | ✅ Posible | ✅ Posible | ❌ No hay qué hackear |
| **Gobierno puede pedir datos** | ✅ Sí | ⚠️ Mínimos | ✅ Sí | ❌ No hay datos |

---

## 🛡️ Protección en Capas

### Capa 1: Dispositivo Físico
```
Tu celular tiene:
- PIN/contraseña de desbloqueo
- Encriptación de Android (BitLocker móvil)
- Protección biométrica (huella/cara)
```

### Capa 2: Aplicación
```
DeepChat tiene:
- Contraseña de la app (opcional)
- Auto-bloqueo después de inactividad
- Protección de screenshots (opcional)
```

### Capa 3: Datos en Reposo
```
Archivos guardados:
- Claves privadas: Encriptadas con contraseña
- Mensajes: Protegidos por encriptación del sistema
- Archivos: Opcionalmente encriptados
```

### Capa 4: Datos en Tránsito
```
Comunicación:
- Tor: 3 capas de encriptación (cebolla)
- E2E: RSA-4096 + AES-256
- No revelan IP ni identidad
```

---

## 🔍 Auditoría de Privacidad

### ¿Qué puede ver cada uno?

#### Tu Proveedor de Internet (ISP):
```
❌ NO puede ver:
   - Con quién hablas
   - Qué dices
   - Tu identidad en DeepChat

✅ SÍ puede ver:
   - Que usas Tor (tráfico encriptado)
   - Solución: Usar VPN antes de Tor
```

#### Nodos de Tor:
```
❌ NO pueden ver:
   - Tu IP real (solo el guardia)
   - El destino final (solo el nodo de salida)
   - El contenido (encriptado E2E)

✅ SÍ pueden ver:
   - Tráfico encriptado pasando
```

#### Otros Usuarios de DeepChat:
```
❌ NO pueden ver:
   - Tus conversaciones con otros
   - Tu dirección IP
   - Tus contactos

✅ SÍ pueden ver:
   - Mensajes que LES envías
   - Tu dirección .onion (si la compartes)
```

#### Gobierno/Autoridades:
```
❌ NO pueden:
   - Pedir datos a un servidor (no existe)
   - Interceptar mensajes (E2E encryption)
   - Saber tu identidad (Tor)
   - Ver tu historial (está solo en tu celular)

✅ SÍ pueden:
   - Confiscar tu celular físicamente
   - Solución: Contraseña fuerte + borrado remoto
```

---

## 💡 Mejores Prácticas de Privacidad

### ✅ HACER:

1. **Contraseña Fuerte:**
```python
# Cambiar en config.py
CRYPTO_CONFIG = {
    'key_password': 'Contr4señ4-Muy-Fúerte-2025!#'
}
```

2. **Auto-Borrado:**
```python
# Borrar mensajes antiguos automáticamente
PRIVACY_CONFIG = {
    'auto_delete_messages': True,
    'delete_after_days': 30
}
```

3. **Backup Manual Seguro:**
```bash
# Exportar tu identidad (guardarlo en USB encriptado)
cp ~/.deepchat/private_key.pem /path/to/usb/seguro/

# NO subirlo a Google Drive, Dropbox, etc.
```

4. **Verificar Fingerprints:**
```
Antes de confiar en un contacto:
1. Obtener fingerprint: Settings → My Fingerprint
2. Verificar con contacto por otro medio (teléfono, en persona)
3. Si coincide → Marcar como "Verificado"
```

### ❌ NO HACER:

1. **NO hacer backup en la nube:**
```
❌ Google Drive backup
❌ iCloud backup
❌ Dropbox sync
→ Tu privacidad se pierde
```

2. **NO compartir tu .onion públicamente:**
```
❌ Postearlo en redes sociales
❌ Enviarlo por email sin encriptar
❌ Escribirlo en lugares públicos
→ Solo compartir con personas de confianza
```

3. **NO usar en dispositivo rooteado:**
```
❌ Root/Jailbreak
→ Malware puede acceder a todo
```

4. **NO usar en WiFi público sin VPN:**
```
❌ WiFi de café, aeropuerto sin protección
→ Usar VPN → Tor → DeepChat
```

---

## 🔐 Encriptación de Almacenamiento Android

### Encriptación Nativa de Android:

```
Android 6.0+:
- Full Disk Encryption (FDE) o File-Based Encryption (FBE)
- Todos los archivos de DeepChat están protegidos
- Se necesita PIN/contraseña para desencriptar

DeepChat aprovecha esta protección:
/data/data/org.deepchat.deepchatsecure/ ← Encriptado por Android
```

### Protección Adicional en DeepChat:

```python
# Además de la encriptación de Android:
1. Claves privadas → Encriptadas con TU contraseña
2. Archivos sensibles → Opcionalmente encriptados
3. Mensajes en BD → SQLite encriptado (opcional)
```

---

## 📊 Resumen de Privacidad

### ✅ LO QUE GARANTIZAMOS:

| Aspecto | Estado |
|---------|--------|
| Datos en servidor externo | ❌ CERO |
| Datos en la nube | ❌ NINGUNO |
| Backups automáticos | ❌ NO |
| Analytics/tracking | ❌ NO |
| Logs centralizados | ❌ NO |
| Metadatos compartidos | ❌ NO |
| Tu control total | ✅ 100% |
| Almacenamiento local | ✅ SÍ |
| Encriptación E2E | ✅ SÍ |
| Anonimato con Tor | ✅ SÍ |

---

## 🗂️ Borrado Completo de Datos

### Opción 1: Borrar Solo Mensajes
```bash
rm -rf ~/.deepchat/messages/
```

### Opción 2: Borrar Solo Archivos
```bash
rm -rf ~/.deepchat/file_transfers/
```

### Opción 3: Borrar Todo (Mantener Identidad)
```bash
rm -rf ~/.deepchat/messages/
rm -rf ~/.deepchat/groups/
rm -rf ~/.deepchat/file_transfers/
rm -rf ~/.deepchat/contacts.json
# Conserva: private_key.pem, public_key.pem, identity.json
```

### Opción 4: RESET TOTAL
```bash
# ⚠️ ADVERTENCIA: Pierdes tu identidad .onion
rm -rf ~/.deepchat/
# Ya no podrás usar la misma dirección .onion
# Tendrás que crear nueva identidad
```

### En la App:
```
Settings → Privacy → Delete All Data
→ Confirmación con contraseña
→ Todo borrado permanentemente
```

---

## 🎯 Conclusión

**DeepChat Secure es la ÚNICA app de mensajería donde:**

✅ **TÚ tienes control total** de tus datos  
✅ **NADA sale de tu dispositivo** sin tu permiso  
✅ **CERO servidores** que puedan ser hackeados  
✅ **CERO metadatos** para rastrear  
✅ **CERO vigilancia** posible  

**Tu privacidad, en TUS manos. Literalmente. 🔒📱**

---

**Actualizado:** Enero 2025  
**Versión:** 1.1.0  
**Garantía:** 100% Local, 0% Cloud
