[app]
title = DataMonitor
package.name = datamonitor
package.domain = org.wito
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[app.android]
android.api = 31
android.minapi = 21
android.sdk = 20
android.ndk = 25b
android.ndk_path = 
android.sdk_path = 
android.p4a_dir = 
android.bootstrap = sdl2
android.build_tools_version = 31.0.0
