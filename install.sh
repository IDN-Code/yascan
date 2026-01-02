#!/bin/bash

echo "================================================"
echo "  DeepChat Secure - Instalación Rápida"
echo "================================================"
echo ""

# Verificar Python
echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "Instala Python 3.10+ y vuelve a ejecutar este script"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"
echo ""

# Verificar Tor
echo "[2/6] Verificando Tor..."
if ! command -v tor &> /dev/null; then
    echo "⚠️  Tor no está instalado. Instalando..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y tor
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install tor
    else
        echo "❌ Sistema operativo no soportado para instalación automática de Tor"
        echo "Por favor instala Tor manualmente: https://www.torproject.org/download/"
        exit 1
    fi
fi

TOR_VERSION=$(tor --version | head -n1)
echo "✅ $TOR_VERSION"
echo ""

# Crear entorno virtual
echo "[3/6] Creando entorno virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi
echo ""

# Activar entorno virtual
echo "[4/6] Activando entorno virtual..."
source venv/bin/activate
echo "✅ Entorno virtual activado"
echo ""

# Instalar dependencias
echo "[5/6] Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas correctamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi
echo ""

# Verificar OpenCV
echo "[6/6] Verificando instalación de OpenCV..."
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ OpenCV instalado correctamente"
else
    echo "⚠️  Instalando dependencias de OpenCV..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install -y \
            libopencv-dev \
            python3-opencv \
            libgl1-mesa-glx \
            libglib2.0-0
    fi
    
    pip install opencv-python-headless
fi
echo ""

# Crear directorio de datos
echo "Creando directorio de datos..."
mkdir -p ~/.deepchat
echo "✅ Directorio ~/.deepchat creado"
echo ""

# Iniciar Tor (opcional)
echo "¿Deseas iniciar Tor ahora? (s/n)"
read -r response
if [[ "$response" =~ ^([sS][iI]|[sS])$ ]]; then
    echo "Iniciando Tor..."
    sudo systemctl start tor
    sudo systemctl enable tor
    
    sleep 3
    
    if systemctl is-active --quiet tor; then
        echo "✅ Tor iniciado correctamente"
    else
        echo "⚠️  Error iniciando Tor. Intenta manualmente: sudo systemctl start tor"
    fi
fi
echo ""

echo "================================================"
echo "  ✅ Instalación Completada!"
echo "================================================"
echo ""
echo "Para ejecutar la aplicación:"
echo ""
echo "  1. Activar entorno virtual:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Ejecutar aplicación:"
echo "     python main.py"
echo ""
echo "Para compilar para Android:"
echo ""
echo "  1. Instalar buildozer:"
echo "     pip install buildozer"
echo ""
echo "  2. Compilar APK:"
echo "     buildozer android debug"
echo ""
echo "  3. Instalar en dispositivo:"
echo "     buildozer android deploy run"
echo ""
echo "================================================"
echo "  Documentación: README.md"
echo "  Soporte: https://github.com/tu-usuario/deepchat-secure"
echo "================================================"
