[app]
title = DataMonitor
package.name = datamonitor
package.domain = org.wito50
source.dir = .
source.include_exts = py,txt,db
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# Archivos que se copiarán al APK
presplash.filename = 
icon.filename = 

# Modo consola
log_level = 2
console = 1

# Archivos adicionales
include_patterns = *.txt, *.db

[buildozer]
log_level = 2
warn_on_root = 1

# Configuración de Android
android.sdk = 31
android.ndk = 23.1.7779620
android.api = 31
android.minapi = 21
android.build_tools_version = 33.0.2
android.archs = arm64-v8a,armeabi-v7a
package.class = MainApp
