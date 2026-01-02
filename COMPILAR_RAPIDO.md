# 🚀 INICIO RÁPIDO: Compilar Yascan a APK

## ⚡ 3 PASOS PARA TENER TU APK

### PASO 1: Preparar Ubuntu/Linux (10 minutos)

```bash
# Si estás en Windows, instala WSL2:
# En PowerShell (Administrador):
wsl --install -d Ubuntu-22.04

# Si ya tienes Linux, actualiza:
sudo apt-get update && sudo apt-get upgrade -y
```

### PASO 2: Usar el Script Automático (5 minutos)

```bash
# Extraer proyecto
unzip yascan.zip
cd yascan

# Instalar dependencias (primera vez)
./compilar_yascan.sh
# Selecciona opción 3: "Instalar dependencias del sistema"
```

### PASO 3: Compilar (30-60 min primera vez)

```bash
# Compilar APK
./compilar_yascan.sh
# Selecciona opción 1: "Debug APK"

# Tu APK estará en:
# bin/yascan-debug.apk
```

---

## 📱 PASO 4: Instalar en tu Celular

### Opción A: Por Cable USB

```bash
# Habilita "Depuración USB" en tu celular
# Conecta por USB

adb install bin/yascan-debug.apk
```

### Opción B: Manual

```bash
# Copia el APK a tu celular
# Abre el archivo yascan-debug.apk
# Permite "Orígenes desconocidos"
# Instala
```

---

## 🎯 COMANDOS RÁPIDOS

```bash
# Ver todas las opciones
./compilar_yascan.sh

# Opciones disponibles:
# 1) Debug APK (desarrollo)
# 2) Release APK (distribución)
# 3) Instalar dependencias
# 4) Limpiar cache
# 5) Instalar en dispositivo conectado
# 6) Ver logs
```

---

## 📋 REQUISITOS

### Tu Computadora (para compilar):
- Ubuntu 20.04+ o WSL2
- 20 GB espacio libre
- 8 GB RAM (16 GB recomendado)
- Conexión a internet

### Celulares (para instalar):
- Android 5.0 o superior
- 2 GB RAM o más
- 100 MB espacio libre
- Ver: COMPATIBILIDAD_ANDROID.md

---

## 🆘 PROBLEMAS COMUNES

### Error: "buildozer: command not found"
```bash
# Ejecuta primero:
./compilar_yascan.sh
# Opción 3: Instalar dependencias
```

### Error: "No space left on device"
```bash
# Necesitas más espacio. Limpia:
sudo apt-get clean
sudo apt-get autoremove
```

### APK muy grande (>50 MB)
```bash
# Normal. Incluye:
# - Python completo
# - Tor
# - Cryptography
# - OpenCV
# - Kivy
```

---

## 📚 DOCUMENTACIÓN COMPLETA

- **GUIA_COMPILAR_APK.md** - Guía paso a paso detallada
- **COMPATIBILIDAD_ANDROID.md** - Requisitos de celulares
- **README.md** - Manual de usuario de Yascan

---

## ✅ VERIFICAR COMPILACIÓN EXITOSA

```bash
# Debe existir:
ls -lh bin/yascan*.apk

# Debe mostrar algo como:
# yascan-1.0.0-armeabi-v7a-debug.apk  (30-50 MB)
```

---

## 🎉 ¡LISTO!

Ya tienes tu APK. Ahora:

1. Instálalo en tu celular
2. Instala Orbot desde Play Store
3. Abre Yascan
4. Crea tu identidad
5. ¡Empieza a chatear de forma segura!

---

**Tiempo total estimado:**
- Primera compilación: 1-2 horas
- Siguientes compilaciones: 5-10 minutos

**¿Dudas?** Ver GUIA_COMPILAR_APK.md (guía completa)
