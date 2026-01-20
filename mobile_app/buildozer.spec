[app]
# orientation
orientation = portrait

# (str) Title of your application
title = Life Logger

# (str) Package name
package.name = lifelogger

# (str) Package domain (needed for android/ios packaging)
package.domain = com.regularman

# (str) Source code where the main.py lives
# Если buildozer.spec лежит в корне, а код в mobile_app
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,json,db

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# ВАЖНО: certifi нужен для работы SSL/HTTPS в requests на Android
requirements = python3,kivy,requests,urllib3,certifi,idna,charset_normalizer,jnius,pyjnius,android

# (str) Custom source folders for requirements
# (list) Permissions
permissions = INTERNET
android.allow_cleartext = True

# Разрешаем Cleartext Traffic (HTTP) для работы с локальным IP
android.manifest.application_attributes = android:usesCleartextTraffic="true"

# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) use buildozer.spec's android.api to query the sdk path (default True)
# android.auto_setup = True

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# arm64-v8a — стандарт для большинства современных телефонов
android.archs = arm64-v8a

# (bool) adds support for multi-window mode
android.allow_multi_window = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1

# python
python = /home/medionchikl/shitanami_android_kivy/venv/bin/python