#!/bin/bash
source .venv/bin/activate
export QT_IM_MODULE=fcitx
export GTK_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
export QT4_IM_MODULE=fcitx
export CLUTTER_IM_MODULE=fcitx
export QT_QPA_PLATFORM=xcb
python3 main.py
