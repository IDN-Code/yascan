[app]

# Nombre de la aplicación
title = Yascan

# Nombre del paquete
package.name = yascan

# Dominio del paquete (usado para crear package.domain.name)
package.domain = com.yascan

# Directorio fuente de la aplicación
source.dir = .

# Extensiones de archivos a incluir
source.include_exts = py,png,jpg,kv,atlas,json

# (lista) Archivos o directorios a excluir
# source.exclude_exts = spec

# (lista) Patrones de directorios a excluir
# source.exclude_dirs = tests, bin

# (lista) Patrones de archivos a excluir
# source.exclude_patterns = license,images/*/*.jpg

# (str) Versión de la aplicación
version = 1.0.0

# (lista) Requerimientos de la aplicación
# formato: nombre_modulo o nombre_modulo==version
requirements = python3,kivy,pysocks,pyaes,ecdsa,requests,pillow

# (str) Orientación de la pantalla (portrait, landscape, sensor)
orientation = portrait

# (bool) Indicar si la aplicación debe ser en pantalla completa
fullscreen = 0

# (int) Target Android API (debe ser al menos 31 para nuevas apps en Play Store)
android.api = 33

# (int) Mínima API que soportará la app
android.minapi = 21

# (int) Android SDK version a usar
android.sdk = 33

# (str) Android NDK version a usar
android.ndk = 25b

# (bool) Usar --private data storage
android.private_storage = True

# (lista) Permisos de Android
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# (lista) Features de Android
android.features = android.hardware.camera,android.hardware.camera.autofocus

# (str) Soporte para Android arch
android.archs = arm64-v8a

# (bool) Habilitar AndroidX
android.enable_androidx = True

# (str) Presplash background color
android.presplash_color = #000000

# (str) Icono de la aplicación
# icon.filename = %(source.dir)s/data/icon.png

# (str) Presplash de la aplicación
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Archivo de inicio de la aplicación
android.entrypoint = org.kivy.android.PythonActivity

# (str) Java runtime
# android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (lista) AAR archives a añadir
# android.add_aars = your_lib.aar

# (str) Gradle dependencies
android.gradle_dependencies = 

# (bool) Habilitar backup automático en Android >= 6.0
android.allow_backup = True

# (str) Nombre del servicio Python
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# (str) Bootstrap python-for-android a usar
# p4a.bootstrap = sdl2

# (lista) Módulos p4a recipe
# p4a.local_recipes = 

# (str) Directorio de source.include_patterns
# p4a.source_dir = 

# (str) URL del hook
# p4a.hook = 

# (str) Bootstrap a usar para pure Python apps
# p4a.port = 

# (lista) Extensiones Python compiladas en APK
# android.add_compile_options = 

# (bool) Copiar biblioteca en lib/
# android.copy_libs = 1

# (str) Nombre de archivo APK resultante
# android.release_artifact = aab

# (str) Modo de release APK (release o debug)
# android.release = debug

# (str) Keystore para firmar APK en modo release
# android.keystore = ~/.android/debug.keystore
# android.keystore_alias = androiddebugkey
# android.keystore_password = android
# android.key_password = android


[buildozer]

# (int) Nivel de log (0 = error, 1 = info, 2 = debug)
log_level = 2

# (int) Mostrar warnings como errores
warn_on_root = 1

# (str) Directorio de build
# build_dir = ./.buildozer

# (str) Directorio de especificación
# bin_dir = ./bin
