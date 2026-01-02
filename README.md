# DeepChat Secure

Aplicación de chat y videollamadas encriptadas para Android que funciona completamente a través de la red Tor (Deep Web).

## 🔐 Características

- ✅ **Comunicación anónima**: Todo el tráfico pasa por Tor
- ✅ **Encriptación end-to-end**: RSA-4096 + Fernet (AES-256)
- ✅ **Sin APIs externas**: Completamente P2P
- ✅ **Chat seguro 1-a-1**: Mensajes encriptados individuales
- ✅ **Grupos**: Chat y llamadas grupales hasta 100+ miembros
- ✅ **Transferencia de archivos**: Envío encriptado de archivos hasta 100 MB
- ✅ **Videollamadas 1-a-1**: Streaming de video encriptado
- ✅ **Videollamadas grupales**: Múltiples participantes simultáneos
- ✅ **Identidad anónima**: Direcciones .onion únicas
- ✅ **Sin metadatos**: No hay servidores centrales
- ✅ **Almacenamiento 100% local**: CERO datos en la nube
- ✅ **Auto-destructivo**: Mensajes temporales opcionales
- ✅ **Procesamiento paralelo**: Envíos masivos optimizados
- ✅ **Sin timeouts**: Manejo eficiente de conexiones largas

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Kivy UI       │  Interfaz de usuario Android
├─────────────────┤
│ Crypto Manager  │  Encriptación E2E (RSA + Fernet)
├─────────────────┤
│ Tor Manager     │  Servicios ocultos y enrutamiento
├─────────────────┤
│ P2P Network     │  Protocolo de mensajería P2P
├─────────────────┤
│ Video Stream    │  Captura y codificación de video
└─────────────────┘
```

## 🔧 Tecnologías

- **Python 3.10+**
- **Kivy** - Framework UI Android
- **Cryptography** - Encriptación robusta
- **Tor** - Red anónima
- **OpenCV** - Procesamiento de video
- **PySocks** - Proxy SOCKS5 para Tor

## 📦 Instalación

### En Linux/PC (Desarrollo y Testing)

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/deepchat-secure.git
cd deepchat-secure

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar Tor
sudo apt-get install tor

# 5. Ejecutar aplicación
python main.py
```

### En Android

```bash
# 1. Instalar buildozer
pip install buildozer

# 2. Instalar dependencias del sistema
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    ffmpeg \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libswscale-dev \
    libavformat-dev \
    libavcodec-dev \
    zlib1g-dev \
    libgstreamer1.0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good

# 3. Inicializar buildozer
buildozer init

# 4. Compilar APK
buildozer android debug

# 5. Desplegar en dispositivo
buildozer android deploy run
```

### Nota para Android

En Android, la app necesita **Orbot** (implementación oficial de Tor para Android):

1. Instalar Orbot desde F-Droid o Google Play
2. Iniciar Orbot antes de usar DeepChat
3. DeepChat se conectará automáticamente al proxy de Orbot

## 🚀 Uso

### 1. Primera vez - Crear identidad

```
1. Abrir la app
2. Ingresar nombre de usuario
3. Presionar "Nueva Identidad"
4. Esperar generación de claves (30-60 segundos)
5. Se mostrará tu dirección .onion única
```

### 2. Agregar contactos

```
1. En pantalla principal, presionar botón "+"
2. Ingresar nombre del contacto
3. Ingresar su dirección .onion
4. Guardar
```

### 3. Chatear (1-a-1)

```
1. Seleccionar contacto
2. Escribir mensaje
3. Presionar "Enviar"
4. Los mensajes se encriptan automáticamente
```

### 4. Crear grupo

```
1. En pantalla principal, ir a "Grupos"
2. Presionar botón "+"
3. Ingresar nombre del grupo
4. Seleccionar contactos a agregar
5. Crear grupo
6. Enviar mensaje al grupo (broadcast paralelo a todos)
```

### 5. Enviar archivos

**A un contacto:**
```
1. Abrir chat con contacto
2. Presionar icono de archivo 📎
3. Seleccionar archivo (máx 100 MB)
4. Confirmar envío
5. Ver progreso en tiempo real
```

**A un grupo:**
```
1. Abrir chat de grupo
2. Presionar icono de archivo 📎
3. Seleccionar archivo
4. El archivo se envía a TODOS los miembros en paralelo
5. Ver progreso global
```

### 6. Videollamada (1-a-1)

```
1. Abrir chat con contacto
2. Presionar icono de cámara 📹
3. Esperar conexión (puede tomar 30-60 segundos por Tor)
4. Disfrutar de videollamada segura
```

### 7. Videollamada grupal

```
1. Abrir chat de grupo
2. Presionar icono de cámara 📹
3. Esperar a que otros miembros se unan
4. Ver múltiples streams simultáneamente
```

## 🔒 Seguridad

### Encriptación

- **RSA-4096**: Para intercambio de claves
- **Fernet (AES-256)**: Para mensajes y archivos
- **SHA-256**: Para hashing y firmas digitales

### Anonimato

- Todo el tráfico pasa por Tor (3 saltos)
- Direcciones .onion v3 (56 caracteres)
- No hay servidores centrales
- Sin DNS leaks
- Sin metadatos expuestos

### Mejores prácticas

✅ **SÍ hacer:**
- Usar contraseña fuerte para encriptar claves
- Exportar y guardar backup de identidad
- Verificar fingerprint de contactos
- Mantener la app actualizada

❌ **NO hacer:**
- Compartir tu clave privada
- Usar en redes públicas sin precaución
- Confiar en contactos no verificados
- Revelar información personal sensible

## 📁 Estructura del Proyecto

```
deepchat_secure/
│
├── main.py              # Aplicación principal Kivy
├── crypto_manager.py    # Gestión de encriptación
├── tor_manager.py       # Gestión de Tor
├── p2p_network.py       # Red peer-to-peer
├── video_stream.py      # Streaming de video
│
├── requirements.txt     # Dependencias Python
├── buildozer.spec       # Configuración Android
│
└── ~/.deepchat/         # Datos de usuario (creado automáticamente)
    ├── private_key.pem
    ├── public_key.pem
    ├── identity.json
    ├── contacts.json
    ├── messages/
    └── tor_data/
```

## 🧪 Testing

### Test de Encriptación

```bash
python crypto_manager.py
```

### Test de Tor

```bash
python tor_manager.py
```

### Test de P2P

```bash
# Terminal 1
python p2p_network.py

# Terminal 2
python p2p_network.py
```

### Test de Video

```bash
python video_stream.py
```

## 🐛 Troubleshooting

### Tor no conecta

```bash
# Verificar que Tor esté instalado
tor --version

# Verificar puertos
sudo netstat -tlnp | grep 9050

# Reiniciar Tor
sudo systemctl restart tor
```

### Cámara no funciona

```bash
# Verificar permisos
# En Android: Settings > Apps > DeepChat > Permissions > Camera

# En Linux
ls -l /dev/video*
```

### Error de encriptación

```bash
# Regenerar claves
rm -rf ~/.deepchat/
python main.py
# Crear nueva identidad
```

## 🔄 Roadmap

### v1.0 (Actual)
- [x] Chat encriptado básico
- [x] Identidad anónima
- [x] Integración con Tor
- [x] Videollamadas básicas

### v1.1 (Próximo)
- [ ] Llamadas de audio
- [ ] Compartir archivos
- [ ] Stickers encriptados
- [ ] Grupos de chat

### v1.2
- [ ] Mensajes auto-destructivos
- [ ] Verificación de identidad con QR
- [ ] Modo offline (almacenamiento local)
- [ ] Temas personalizables

### v2.0
- [ ] Red mesh P2P
- [ ] Sincronización multi-dispositivo
- [ ] Canales públicos anónimos
- [ ] Blockchain para registro de identidades

## 📊 Rendimiento

### Métricas típicas (Tor)

- **Latencia de mensaje**: 2-5 segundos
- **Establecimiento de llamada**: 30-60 segundos
- **Videollamada**: 15 FPS @ 640x480
- **Ancho de banda**: ~200 KB/s por videollamada

### Optimizaciones

```python
# Ajustar calidad de video para conexiones lentas
video_stream.set_quality(30)  # Menor calidad = menos datos
video_stream.set_fps(10)       # Menos FPS = más fluido en Tor
```

## ⚖️ Legal

Esta aplicación es solo para fines educativos y de investigación. Los usuarios son responsables de cumplir con las leyes locales sobre encriptación y comunicaciones anónimas.

**Disclaimer**: El uso de Tor puede estar restringido en algunas jurisdicciones. Verifica las leyes locales antes de usar.

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

```bash
# 1. Fork el repositorio
# 2. Crear branch
git checkout -b feature/nueva-funcionalidad

# 3. Commit cambios
git commit -m "Agregar nueva funcionalidad"

# 4. Push al branch
git push origin feature/nueva-funcionalidad

# 5. Crear Pull Request
```

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 👥 Autores

- Tu Nombre - Desarrollo inicial

## 🙏 Agradecimientos

- Tor Project
- Kivy Team
- Python Cryptography Team
- OpenCV Community

## 📞 Soporte

- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/deepchat-secure/issues)
- 📧 Email: support@deepchat.org
- 💬 Telegram: @deepchatsupport

## 🔗 Links útiles

- [Tor Project](https://www.torproject.org/)
- [Kivy Documentation](https://kivy.org/doc/stable/)
- [Cryptography Docs](https://cryptography.io/)
- [Orbot (Android Tor)](https://guardianproject.info/apps/org.torproject.android/)

---

**⚠️ IMPORTANTE**: Esta es una aplicación de seguridad. Mantén tu clave privada segura y nunca la compartas con nadie.

```
 ____                  ____ _           _   
|  _ \  ___  ___ _ __ / ___| |__   __ _| |_ 
| | | |/ _ \/ _ \ '_ \| |   | '_ \ / _` | __|
| |_| |  __/  __/ |_) | |___| | | | (_| | |_ 
|____/ \___|\___| .__/ \____|_| |_|\__,_|\__|
                |_|                          
    Secure • Anonymous • Encrypted
```
