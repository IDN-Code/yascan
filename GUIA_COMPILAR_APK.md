# 📱 GUÍA COMPLETA: Convertir Yascan a APK para Android

## 🎯 OBJETIVO
Crear un archivo **yascan-1.0.0.apk** descargable para instalar en cualquier Android.

---

## 📋 ÍNDICE
1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación del Entorno](#instalación-del-entorno)
3. [Preparación del Proyecto](#preparación-del-proyecto)
4. [Compilación del APK](#compilación-del-apk)
5. [Firma del APK (Opcional)](#firma-del-apk)
6. [Distribución](#distribución)
7. [Requisitos de Celulares](#requisitos-de-celulares)
8. [Troubleshooting](#troubleshooting)

---

# PARTE 1: PREPARACIÓN

## 1️⃣ Requisitos del Sistema

### Opción A: Linux (Ubuntu/Debian) - RECOMENDADO ✅

**Sistema operativo recomendado:**
- Ubuntu 20.04 LTS o superior
- Debian 11 o superior
- Linux Mint 20 o superior

**Espacio en disco:**
- Mínimo: 20 GB libres
- Recomendado: 30 GB libres

**RAM:**
- Mínimo: 8 GB
- Recomendado: 16 GB

**Tiempo de compilación:**
- Primera vez: 30-60 minutos
- Siguientes veces: 5-10 minutos

### Opción B: Windows con WSL2

Si estás en Windows, necesitas WSL2 (Windows Subsystem for Linux):

```bash
# En PowerShell como Administrador:
wsl --install -d Ubuntu-22.04
```

Luego sigue los pasos de Linux.

### Opción C: macOS

Buildozer funciona en macOS pero es más complicado. Se recomienda Linux.

---

## 2️⃣ Instalación del Entorno

### PASO 1: Actualizar el Sistema

```bash
# Actualizar paquetes
sudo apt-get update
sudo apt-get upgrade -y
```

### PASO 2: Instalar Dependencias Básicas

```bash
# Instalar herramientas de desarrollo
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-11-jdk \
    wget \
    curl \
    autoconf \
    automake \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev
```

### PASO 3: Instalar Dependencias de Buildozer

```bash
# Dependencias para compilar Python en Android
sudo apt-get install -y \
    build-essential \
    ccache \
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
```

### PASO 4: Instalar Buildozer y Cython

```bash
# Actualizar pip
pip3 install --upgrade pip

# Instalar buildozer
pip3 install --upgrade buildozer

# Instalar Cython (necesario)
pip3 install --upgrade Cython==0.29.33

# Verificar instalación
buildozer --version
# Debe mostrar: Buildozer 1.5.0 o superior
```

---

## 3️⃣ Preparación del Proyecto

### PASO 1: Descargar y Extraer Yascan

```bash
# Descargar el proyecto
cd ~
unzip yascan.zip
cd yascan

# O si lo tienes en otra ubicación:
cd /ruta/a/yascan
```

### PASO 2: Verificar Estructura

```bash
# Verificar que existen estos archivos:
ls -la

# Debes ver:
# - main.py
# - buildozer.spec
# - requirements.txt
# - crypto_manager.py
# - tor_manager.py
# - etc...
```

### PASO 3: Revisar buildozer.spec

```bash
# Abrir y revisar configuración
nano buildozer.spec

# Verificar que diga:
# title = Yascan
# package.name = yascan
# package.domain = com.yascan
```

**Configuraciones importantes en buildozer.spec:**

```ini
[app]
title = Yascan
package.name = yascan
package.domain = com.yascan

# Versión de la app
version = 1.0.0

# Permisos necesarios
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# API de Android
android.api = 33
android.minapi = 21

# Arquitecturas (ARM para mayoría de celulares)
android.archs = arm64-v8a,armeabi-v7a
```

---

# PARTE 2: COMPILACIÓN

## 4️⃣ Compilación del APK

### PASO 1: Inicializar Buildozer (Primera Vez)

```bash
# Dentro de la carpeta yascan/
buildozer init

# Esto ya está hecho, pero si no existe buildozer.spec, lo crea
```

### PASO 2: Compilar en Modo Debug (Primera Compilación)

```bash
# IMPORTANTE: Primera vez tarda 30-60 minutos
# Descarga Android SDK, NDK, y compila todo

buildozer android debug

# Verás muchos mensajes, es normal. Espera pacientemente.
```

**Lo que hace buildozer:**

1. ✅ Descarga Android SDK (~500 MB)
2. ✅ Descarga Android NDK (~1 GB)
3. ✅ Compila Python para Android
4. ✅ Compila todas las dependencias (cryptography, kivy, opencv, etc.)
5. ✅ Empaqueta tu código Python
6. ✅ Crea el APK final

**Progreso típico:**

```
# Buildozer comprobando configuración...
# Downloading Android SDK...
# [################] 100%
# Downloading Android NDK...
# [################] 100%
# Building recipes...
# - python3
# - kivy
# - cryptography
# - opencv
# ...
# Packaging APK...
# APK created!
```

### PASO 3: Ubicación del APK

```bash
# El APK estará en:
cd bin/

# Verás:
# yascan-1.0.0-armeabi-v7a-debug.apk

# Renombrar para simplificar (opcional)
mv yascan-1.0.0-armeabi-v7a-debug.apk yascan-debug.apk
```

---

## 5️⃣ Compilación en Modo Release (Para Distribución)

### ¿Cuándo usar Release?

- ✅ Para publicar en tiendas (Google Play, F-Droid)
- ✅ Para distribución masiva
- ✅ Para versión final optimizada

### PASO 1: Compilar Release

```bash
buildozer android release
```

### PASO 2: Firmar el APK

**Para distribuir, el APK DEBE estar firmado.**

#### Crear Keystore (Primera Vez):

```bash
# Crear carpeta para keystore
mkdir -p ~/.android

# Generar keystore
keytool -genkey -v \
  -keystore ~/.android/yascan.keystore \
  -alias yascan \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Te pedirá:
# - Contraseña del keystore (guárdala!)
# - Nombre, organización, etc.
```

**⚠️ IMPORTANTE: Guarda el keystore y contraseña en lugar seguro!**

```bash
# Backup del keystore
cp ~/.android/yascan.keystore ~/yascan-keystore-backup.keystore

# Guarda también la contraseña en un gestor de contraseñas
```

#### Firmar el APK:

```bash
# Ir a carpeta bin/
cd bin/

# Firmar APK
jarsigner -verbose \
  -sigalg SHA256withRSA \
  -digestalg SHA-256 \
  -keystore ~/.android/yascan.keystore \
  yascan-1.0.0-armeabi-v7a-release-unsigned.apk \
  yascan

# Te pedirá la contraseña del keystore
```

#### Alinear el APK (Opcional pero Recomendado):

```bash
# Descargar zipalign si no lo tienes
# (viene con Android SDK que buildozer descargó)

# Alinear APK
~/.buildozer/android/platform/android-sdk/build-tools/*/zipalign -v 4 \
  yascan-1.0.0-armeabi-v7a-release-unsigned.apk \
  yascan-1.0.0-release-signed.apk

# Renombrar para simplificar
mv yascan-1.0.0-release-signed.apk yascan.apk
```

---

## 6️⃣ Distribución

### Opción A: Distribución Directa (APK)

**Ventajas:**
- ✅ No requiere Google Play
- ✅ Distribución inmediata
- ✅ Sin restricciones de tiendas
- ✅ Gratis

**Desventajas:**
- ⚠️ Usuarios deben habilitar "Orígenes desconocidos"
- ⚠️ Sin actualizaciones automáticas
- ⚠️ Menos confianza del usuario

#### Paso 1: Subir APK a la Nube

```bash
# Opciones para compartir:
# 1. Google Drive (público)
# 2. Dropbox (link público)
# 3. GitHub Releases
# 4. Tu propio servidor
# 5. Transfer.sh (temporal)

# Ejemplo con transfer.sh:
curl --upload-file yascan.apk https://transfer.sh/yascan.apk

# Te da un link: https://transfer.sh/abc123/yascan.apk
```

#### Paso 2: Crear Página de Descarga

```html
<!-- Ejemplo: index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Descargar Yascan</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>Yascan - Chat Seguro</h1>
    <p>Aplicación de mensajería ultra-segura</p>
    
    <a href="yascan.apk" download>
        <button>Descargar Yascan v1.0.0 (APK)</button>
    </a>
    
    <h2>Instrucciones:</h2>
    <ol>
        <li>Descargar yascan.apk</li>
        <li>Permitir instalación desde orígenes desconocidos</li>
        <li>Instalar aplicación</li>
        <li>¡Listo!</li>
    </ol>
    
    <h2>Requisitos:</h2>
    <ul>
        <li>Android 5.0 o superior</li>
        <li>100 MB espacio libre</li>
        <li>Conexión a internet</li>
    </ul>
</body>
</html>
```

### Opción B: F-Droid (Tienda Open Source)

**Ventajas:**
- ✅ Tienda de apps de código abierto
- ✅ Audiencia técnica/privacidad
- ✅ Actualizaciones automáticas
- ✅ Gratis

**Proceso:**
1. Subir código a GitHub
2. Aplicar a F-Droid: https://f-droid.org/docs/Inclusion_Policy/
3. Esperar aprobación

### Opción C: Google Play Store

**Ventajas:**
- ✅ Mayor alcance
- ✅ Actualizaciones automáticas
- ✅ Más confianza de usuarios

**Desventajas:**
- ❌ Cuesta $25 USD (una vez)
- ❌ Proceso de revisión
- ❌ Políticas estrictas

**Proceso:**
1. Crear cuenta de desarrollador: https://play.google.com/console
2. Pagar $25 USD
3. Subir APK firmado
4. Completar ficha de la app
5. Esperar revisión (1-7 días)

---

# PARTE 3: REQUISITOS DE DISPOSITIVOS

## 7️⃣ Requisitos de Celulares para Instalar Yascan

### ✅ Requisitos MÍNIMOS

```
Sistema Operativo:    Android 5.0 (Lollipop) o superior
Procesador:           ARM 32-bit o ARM 64-bit
RAM:                  2 GB mínimo
Almacenamiento:       100 MB libres
Cámara:               Opcional (para videollamadas)
Micrófono:            Opcional (para llamadas de audio)
Conexión:             WiFi o Datos móviles
```

### ✅ Requisitos RECOMENDADOS

```
Sistema Operativo:    Android 8.0 (Oreo) o superior
Procesador:           ARM 64-bit (arm64-v8a)
RAM:                  4 GB o más
Almacenamiento:       500 MB libres
Cámara:               8 MP o superior
Conexión:             WiFi estable o 4G/5G
```

### 📱 Compatibilidad por Marca

| Marca | Modelos Compatibles | Notas |
|-------|-------------------|-------|
| **Samsung** | Galaxy S6 en adelante | ✅ Totalmente compatible |
| **Xiaomi** | Redmi Note 4 en adelante | ✅ Compatible, requiere Orbot |
| **Huawei** | P9 en adelante | ✅ Compatible (sin Google Play) |
| **Motorola** | Moto G5 en adelante | ✅ Totalmente compatible |
| **OnePlus** | OnePlus 3 en adelante | ✅ Excelente rendimiento |
| **Google** | Pixel 1 en adelante | ✅ Rendimiento óptimo |
| **LG** | G5 en adelante | ✅ Compatible |
| **Sony** | Xperia XZ en adelante | ✅ Compatible |

### ⚠️ Dispositivos NO Recomendados

```
❌ Android Go (muy limitados de RAM)
❌ Tabletas muy antiguas (< Android 5.0)
❌ Dispositivos con < 1 GB RAM
❌ Procesadores x86 (Intel Atom) - no soportados
```

### 🔒 Requisitos de Seguridad

Para máxima seguridad:
```
✅ Android sin root/jailbreak
✅ Actualizaciones de seguridad recientes
✅ Sin spyware/malware
✅ Pantalla de bloqueo configurada
```

---

## 8️⃣ Instrucciones para Usuarios Finales

### Crear archivo: INSTRUCCIONES_INSTALACION.txt

```
═══════════════════════════════════════════════════════
    YASCAN - Instrucciones de Instalación
═══════════════════════════════════════════════════════

PASO 1: DESCARGAR
─────────────────
1. Abre este link en tu celular: [TU_LINK_AQUÍ]
2. Descarga el archivo: yascan.apk
3. Espera a que termine la descarga

PASO 2: PERMITIR INSTALACIÓN
────────────────────────────
1. Ve a Configuración → Seguridad
2. Activa "Orígenes desconocidos" o "Instalar apps desconocidas"
3. Permite instalar desde el navegador/descargador

   En Android 8+:
   Configuración → Apps → Acceso especial → 
   Instalar apps desconocidas → Chrome/Navegador → Permitir

PASO 3: INSTALAR
────────────────
1. Abre el archivo yascan.apk descargado
2. Presiona "Instalar"
3. Espera a que termine (30-60 segundos)
4. Presiona "Abrir"

PASO 4: CONFIGURAR PERMISOS
──────────────────────────
Al abrir Yascan, te pedirá permisos:
✅ Cámara - Para videollamadas
✅ Micrófono - Para llamadas de audio
✅ Almacenamiento - Para enviar archivos
✅ Internet - Para comunicación

PASO 5: INSTALAR ORBOT
──────────────────────
Yascan requiere Orbot (Tor para Android):

1. Abre Google Play Store o F-Droid
2. Busca "Orbot"
3. Instala "Orbot: Tor for Android"
4. Abre Orbot
5. Presiona "Start VPN"
6. Espera a que se conecte

PASO 6: CREAR IDENTIDAD
───────────────────────
1. Abre Yascan
2. Ingresa tu nombre de usuario
3. Presiona "Nueva Identidad"
4. Espera 30-60 segundos
5. ¡Listo! Ya tienes tu dirección .onion

═══════════════════════════════════════════════════════
    PROBLEMAS COMUNES
═══════════════════════════════════════════════════════

❌ "No se puede instalar la app"
   → Verifica que permitiste "Orígenes desconocidos"

❌ "La app no abre"
   → Verifica que tienes Android 5.0 o superior
   → Verifica que tienes espacio libre (100 MB+)

❌ "No conecta"
   → Asegúrate de tener Orbot instalado e iniciado
   → Verifica conexión a internet

❌ "Muy lento"
   → Tor es más lento que internet normal
   → Espera 1-2 minutos para conexiones iniciales

═══════════════════════════════════════════════════════
    SOPORTE
═══════════════════════════════════════════════════════

Email: soporte@yascan.com
Telegram: @YascanSupport
GitHub: github.com/yascan/yascan

═══════════════════════════════════════════════════════
```

---

# PARTE 4: TROUBLESHOOTING

## 9️⃣ Problemas Comunes y Soluciones

### ❌ Error: "Command failed: python3 -m pip install..."

**Causa:** Dependencias faltantes

**Solución:**
```bash
# Reinstalar pip y dependencias
sudo apt-get install --reinstall python3-pip
pip3 install --upgrade pip setuptools wheel
```

### ❌ Error: "NDK not found"

**Causa:** Android NDK no descargado correctamente

**Solución:**
```bash
# Limpiar cache de buildozer
buildozer android clean

# Volver a compilar
buildozer android debug
```

### ❌ Error: "Build failed: Cython"

**Causa:** Versión incorrecta de Cython

**Solución:**
```bash
# Instalar versión específica
pip3 install Cython==0.29.33
```

### ❌ Error: "No space left on device"

**Causa:** Disco lleno

**Solución:**
```bash
# Limpiar buildozer cache
rm -rf .buildozer/

# Liberar espacio
sudo apt-get autoclean
sudo apt-get autoremove
```

### ❌ APK instalado pero no abre en Android

**Causas posibles:**
1. Falta Orbot
2. Permisos no otorgados
3. Android muy antiguo

**Solución:**
```bash
# Ver logs del dispositivo
adb logcat | grep yascan

# Verificar permisos
adb shell pm list permissions -g com.yascan.yascan
```

### ❌ App muy pesada (>50 MB)

**Causa:** Todas las arquitecturas incluidas

**Solución:**
```ini
# En buildozer.spec, cambiar a solo arm64:
android.archs = arm64-v8a

# Recompilar
buildozer android clean
buildozer android debug
```

---

# PARTE 5: OPTIMIZACIONES

## 🔟 Reducir Tamaño del APK

### Método 1: Compilar Solo ARM64

```ini
# buildozer.spec
android.archs = arm64-v8a
```

Reduce tamaño ~40%

### Método 2: Remover Dependencias No Usadas

```txt
# requirements.txt - Comentar lo que no uses
kivy==2.2.1
cryptography==41.0.7
PySocks==1.7.1
# opencv-python==4.8.1.78  # Si no usas video
```

### Método 3: ProGuard (Avanzado)

```ini
# buildozer.spec
android.add_gradle_repositories = google(), mavenCentral()
android.gradle_dependencies = com.android.tools.build:gradle:7.0.0
```

---

# RESUMEN RÁPIDO

## ✅ Checklist Completo

### Preparación:
- [ ] Sistema Linux/WSL instalado
- [ ] Dependencias instaladas
- [ ] Buildozer instalado
- [ ] Proyecto Yascan descargado

### Compilación:
- [ ] buildozer.spec configurado
- [ ] Primera compilación (30-60 min)
- [ ] APK generado en bin/

### Distribución:
- [ ] APK firmado (para release)
- [ ] APK subido a internet
- [ ] Link de descarga creado
- [ ] Instrucciones para usuarios

### Testing:
- [ ] APK instalado en dispositivo de prueba
- [ ] Orbot instalado y funcionando
- [ ] Identidad creada exitosamente
- [ ] Chat funcional

---

# 📝 COMANDOS RÁPIDOS DE REFERENCIA

```bash
# COMPILAR DEBUG (DESARROLLO)
buildozer android debug

# COMPILAR RELEASE (PRODUCCIÓN)
buildozer android release

# LIMPIAR Y RECOMPILAR
buildozer android clean
buildozer android debug

# COMPILAR E INSTALAR EN DISPOSITIVO CONECTADO
buildozer android debug deploy run

# VER LOGS DEL DISPOSITIVO
buildozer android adb -- logcat

# UBICACIÓN DEL APK
ls -lh bin/yascan*.apk
```

---

# 🎯 PRÓXIMOS PASOS

1. **Compilar APK Debug** → Para testing
2. **Probar en 2-3 dispositivos** → Verificar compatibilidad
3. **Compilar APK Release** → Para distribución
4. **Firmar APK** → Seguridad
5. **Subir a internet** → Distribución
6. **Crear página de descarga** → Acceso fácil
7. **Compartir con usuarios** → ¡Lanzamiento!

---

**¡Listo! Con esta guía puedes convertir Yascan a APK y distribuirlo a usuarios de Android.** 🚀
