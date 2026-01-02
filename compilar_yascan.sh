#!/bin/bash

# ═══════════════════════════════════════════════════════════════
#  YASCAN - Script de Compilación Automatizada
#  Versión: 1.0.0
#  Descripción: Compila Yascan a APK para Android
# ═══════════════════════════════════════════════════════════════

set -e  # Detener en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════"
echo "   YASCAN - Compilador Automatizado de APK"
echo "   Versión 1.0.0"
echo "═══════════════════════════════════════════════════════"
echo -e "${NC}"

# Función de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ] || [ ! -f "buildozer.spec" ]; then
    log_error "Error: No se encontró main.py o buildozer.spec"
    log_error "Por favor ejecuta este script desde la carpeta del proyecto Yascan"
    exit 1
fi

log_success "Directorio del proyecto verificado"

# Verificar sistema operativo
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    log_warning "Este script está optimizado para Linux"
    log_warning "Si estás en Windows, usa WSL2"
    read -p "¿Continuar de todas formas? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Menú de opciones
echo ""
log_info "Selecciona el tipo de compilación:"
echo ""
echo "  1) Debug APK (para pruebas - más rápido)"
echo "  2) Release APK (para distribución - requiere firma)"
echo "  3) Instalar dependencias del sistema"
echo "  4) Limpiar cache de buildozer"
echo "  5) Compilar e instalar en dispositivo conectado"
echo "  6) Ver logs del dispositivo Android"
echo ""
read -p "Opción [1-6]: " option

case $option in
    1)
        log_info "Compilando APK en modo DEBUG..."
        echo ""
        
        # Verificar buildozer
        if ! command -v buildozer &> /dev/null; then
            log_error "Buildozer no está instalado"
            log_info "Ejecuta la opción 3 primero para instalar dependencias"
            exit 1
        fi
        
        # Compilar
        log_info "Iniciando compilación (puede tomar 30-60 minutos la primera vez)..."
        buildozer android debug
        
        if [ $? -eq 0 ]; then
            echo ""
            log_success "¡APK compilado exitosamente!"
            echo ""
            log_info "Ubicación del APK:"
            APK_PATH=$(find bin/ -name "*.apk" -type f | head -n 1)
            echo -e "  ${GREEN}$APK_PATH${NC}"
            
            # Información del APK
            APK_SIZE=$(du -h "$APK_PATH" | cut -f1)
            echo ""
            log_info "Tamaño: $APK_SIZE"
            
            # Renombrar para simplificar
            if [[ $APK_PATH == *"debug"* ]]; then
                NEW_NAME="bin/yascan-debug.apk"
                cp "$APK_PATH" "$NEW_NAME"
                log_success "APK copiado a: $NEW_NAME"
            fi
            
            echo ""
            log_info "Próximos pasos:"
            echo "  1. Conecta tu celular por USB"
            echo "  2. Habilita 'Depuración USB' en Opciones de Desarrollador"
            echo "  3. Ejecuta: adb install $NEW_NAME"
            echo "  O bien, copia el APK a tu celular y ábrelo"
        else
            log_error "Error en la compilación"
            exit 1
        fi
        ;;
        
    2)
        log_info "Compilando APK en modo RELEASE..."
        echo ""
        
        # Verificar buildozer
        if ! command -v buildozer &> /dev/null; then
            log_error "Buildozer no está instalado"
            exit 1
        fi
        
        # Compilar release
        log_info "Iniciando compilación release..."
        buildozer android release
        
        if [ $? -eq 0 ]; then
            echo ""
            log_success "APK release compilado"
            
            # Buscar APK unsigned
            APK_UNSIGNED=$(find bin/ -name "*unsigned.apk" -type f | head -n 1)
            
            if [ -z "$APK_UNSIGNED" ]; then
                log_error "No se encontró APK sin firmar"
                exit 1
            fi
            
            log_info "APK sin firmar: $APK_UNSIGNED"
            
            # Verificar si existe keystore
            KEYSTORE="$HOME/.android/yascan.keystore"
            
            if [ ! -f "$KEYSTORE" ]; then
                log_warning "No se encontró keystore"
                log_info "Creando nuevo keystore..."
                
                mkdir -p "$HOME/.android"
                
                keytool -genkey -v \
                    -keystore "$KEYSTORE" \
                    -alias yascan \
                    -keyalg RSA \
                    -keysize 2048 \
                    -validity 10000
                
                log_success "Keystore creado en: $KEYSTORE"
                log_warning "IMPORTANTE: Guarda una copia de este archivo!"
            fi
            
            # Firmar APK
            log_info "Firmando APK..."
            
            jarsigner -verbose \
                -sigalg SHA256withRSA \
                -digestalg SHA-256 \
                -keystore "$KEYSTORE" \
                "$APK_UNSIGNED" \
                yascan
            
            if [ $? -eq 0 ]; then
                log_success "APK firmado exitosamente"
                
                # Alinear APK
                log_info "Alineando APK..."
                
                ZIPALIGN=$(find ~/.buildozer/android/platform/android-sdk/build-tools/ -name "zipalign" | head -n 1)
                
                if [ -n "$ZIPALIGN" ]; then
                    APK_SIGNED="bin/yascan-release-signed.apk"
                    
                    "$ZIPALIGN" -v 4 "$APK_UNSIGNED" "$APK_SIGNED"
                    
                    log_success "APK final: $APK_SIGNED"
                    
                    APK_SIZE=$(du -h "$APK_SIGNED" | cut -f1)
                    log_info "Tamaño: $APK_SIZE"
                    
                    echo ""
                    log_success "¡APK listo para distribución!"
                    echo ""
                    log_info "Próximos pasos:"
                    echo "  1. Sube $APK_SIGNED a Google Drive, Dropbox, etc."
                    echo "  2. Comparte el link de descarga con usuarios"
                    echo "  3. Los usuarios deben habilitar 'Orígenes desconocidos'"
                else
                    log_warning "zipalign no encontrado, pero APK está firmado"
                fi
            else
                log_error "Error firmando APK"
                exit 1
            fi
        else
            log_error "Error en la compilación"
            exit 1
        fi
        ;;
        
    3)
        log_info "Instalando dependencias del sistema..."
        echo ""
        
        # Verificar sudo
        if ! command -v sudo &> /dev/null; then
            log_error "sudo no disponible"
            exit 1
        fi
        
        log_info "Actualizando repositorios..."
        sudo apt-get update
        
        log_info "Instalando herramientas básicas..."
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-venv \
            git \
            zip \
            unzip \
            openjdk-11-jdk \
            wget \
            curl
        
        log_info "Instalando dependencias de compilación..."
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
            gstreamer1.0-plugins-good \
            autoconf \
            automake \
            libtool \
            pkg-config \
            libffi-dev \
            libssl-dev
        
        log_info "Instalando buildozer y Cython..."
        pip3 install --upgrade pip
        pip3 install --upgrade buildozer
        pip3 install --upgrade Cython==0.29.33
        
        log_success "Dependencias instaladas"
        
        # Verificar instalación
        echo ""
        log_info "Verificando instalación..."
        
        if command -v buildozer &> /dev/null; then
            BUILDOZER_VERSION=$(buildozer --version 2>&1 | head -n 1)
            log_success "Buildozer: $BUILDOZER_VERSION"
        else
            log_error "Buildozer no se instaló correctamente"
        fi
        
        if command -v python3 &> /dev/null; then
            PYTHON_VERSION=$(python3 --version)
            log_success "Python: $PYTHON_VERSION"
        fi
        
        echo ""
        log_success "¡Todo listo! Ahora puedes compilar con la opción 1 o 2"
        ;;
        
    4)
        log_info "Limpiando cache de buildozer..."
        
        if [ -d ".buildozer" ]; then
            log_warning "Esto eliminará .buildozer/ (~2-3 GB)"
            read -p "¿Continuar? (s/n) " -n 1 -r
            echo
            
            if [[ $REPLY =~ ^[Ss]$ ]]; then
                rm -rf .buildozer/
                log_success "Cache eliminado"
                log_info "La próxima compilación descargará todo de nuevo"
            else
                log_info "Cancelado"
            fi
        else
            log_warning "No hay cache para limpiar"
        fi
        ;;
        
    5)
        log_info "Compilando e instalando en dispositivo..."
        echo ""
        
        # Verificar adb
        if ! command -v adb &> /dev/null; then
            log_error "adb no está instalado"
            log_info "Instala Android Platform Tools"
            exit 1
        fi
        
        # Verificar dispositivo conectado
        DEVICES=$(adb devices | grep -v "List" | grep "device" | wc -l)
        
        if [ $DEVICES -eq 0 ]; then
            log_error "No hay dispositivos Android conectados"
            log_info "Conecta tu celular por USB y habilita Depuración USB"
            exit 1
        fi
        
        log_success "Dispositivo conectado"
        
        # Compilar e instalar
        buildozer android debug deploy run
        
        if [ $? -eq 0 ]; then
            log_success "App instalada y ejecutada en el dispositivo"
        else
            log_error "Error en instalación"
        fi
        ;;
        
    6)
        log_info "Mostrando logs del dispositivo..."
        echo ""
        
        if ! command -v adb &> /dev/null; then
            log_error "adb no está instalado"
            exit 1
        fi
        
        log_info "Filtrando logs de Yascan..."
        log_info "Presiona Ctrl+C para salir"
        echo ""
        
        adb logcat | grep -i yascan
        ;;
        
    *)
        log_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
log_info "Script finalizado"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
