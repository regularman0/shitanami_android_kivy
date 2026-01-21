[app]
# (str) Title of your application
title = Life Logger

# (str) Package name
package.name = lifelogger

# (str) Package domain (needed for android/ios packaging)
package.domain = com.regularman

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,json,db

# (str) Application versioning (method 1)
version = 1.0.1

# (list) Application requirements
# ВАЖНО: certifi нужен для работы SSL/HTTPS в requests на Android
requirements = python3,kivy,requests,urllib3,certifi,idna,charset_normalizer,jnius,pyjnius,android

# (list) Permissions
# ACCESS_NETWORK_STATE иногда нужен для проверки подключения
permissions = INTERNET,ACCESS_NETWORK_STATE

# (str) Custom source folders for requirements
# (list) Source paths to include (let empty to include all the files)

# --- НАСТРОЙКИ СЕТИ ---
# Разрешаем HTTP (Cleartext) для локальных IP.
# Удалил несуществующую опцию 'android.allow_cleartext', она могла ломать парсер.
android.manifest.application_attributes = android:usesCleartextTraffic="true"

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) adds support for multi-window mode
android.allow_multi_window = True

# (str) Orientation
orientation = portrait

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1