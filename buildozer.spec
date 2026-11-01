[app]
title = Utaun Android
package.name = utaunandroid
package.domain = org.utaun
source.dir = .
source.include_exts = py,kv,ini,txt,wav,png,jpg
version = 0.1.0
requirements = python3,kivy,numpy
orientation = portrait
fullscreen = 0
android.api = 28
android.minapi = 23
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
