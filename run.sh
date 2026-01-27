#!/bin/bash
source .venv/bin/activate
export QT_IM_MODULE=fcitx
export GTK_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
# Ensure PySide6 can see its own plugins and any injected system plugins
python3 main.py
