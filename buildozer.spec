[app]

(str) Title of your application
title = Monitor de Datos Moviles

(str) Package name
package.name = datamonitor

(str) Package domain (needed for android/ios packaging)
package.domain = com.datamonitor

(str) Source code where the main.py is located
source.dir = .

(list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

(str) Application versioning (method 1)
version = 1.0

(list) Application requirements
comma separated e.g. requirements = sqlite3,kivy
Especificar la versión de Kivy es buena práctica
requirements = python3,kivy==2.3.0,sqlite3

(str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

(str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

(str) Supported orientation (landscape, portrait or all)
orientation = portrait

(bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

(int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

[android]

(list) Permissions
android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_PHONE_STATE,WRITE_EXTERNAL_STORAGE,ACCESS_FINE_LOCATION

(str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

(str) Android app theme, default is ok for Kivy-based app
android.theme = @android:style/Theme.NoTitleBar

(str) Android API to use
Se recomienda usar una API más reciente y estable como la 33
android.api = 33

(str) Android SDK version to use - Esta línea es redundante con android.api
android.sdk = 30 # Eliminada o comentada
(str) Android NDK version to use
La versión 25b es estable y recomendada
android.ndk = 25b

(bool) If True, then skip trying to update the Android sdk
android.skip_update = False

(bool) If True, then automatically accept SDK license
Aunque esta opción existe, la aceptación manual en el .yml es más fiable en CI.
android.accept_sdk_license = True

(str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

(bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

(str) Android Build Tools version to use
Mantener la versión 33.0.0 es crucial para evitar problemas de licencia con la 36.0.0
android.build_tools_version = 33.0.0

[python]

(str) Python version to use
version = 3.9

(list) Python packages to install
python.packages =
