#!/bin/bash
source .venv/bin/activate
export QT_IM_MODULE=fcitx
export GTK_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
export QT_QPA_PLATFORM=xcb
# Ensure PySide6 can see its own plugins and any injected system plugins
export QT_PLUGIN_PATH=$(pwd)/.venv/lib/python3.12/site-packages/PySide6/Qt/plugins
python3 main.py
