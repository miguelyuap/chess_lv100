[app]

# (str) Title of your application
title = Chess Lv.100

# (str) Package name
package.name = chesslv100

# (str) Package domain (needed for android/ios packaging)
package.domain = org.antigravity

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,ttf,txt,spec

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
requirements = python3,pygame-ce,python-chess

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (list) Architectures to build for (arm64-v8a es suficiente para dispositivos modernos)
android.archs = arm64-v8a

# (bool) If true, then skip try to update the android sdk information
android.skip_update = False

# (bool) If true, then accept all the sdk licenses automatically
android.accept_sdk_licenses = True


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = error, 1 = warning)
warn_on_root = 1