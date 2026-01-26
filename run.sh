#!/bin/bash
source .venv/bin/activate
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx
python3 main.py
