FROM python:3.12-slim-bookworm

# Install system dependencies required for QtWebEngine
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libnss3 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libasound2 \
    libfontconfig1 \
    libxrandr2 \
    libpango-1.0-0 \
    libcairo2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-cursor0 \
    libxkbfile1 \
    libxshmfence1 \
    libegl1 \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 일반 사용자로 Chromium 샌드박스를 유지한다. / Keep Chromium sandboxed as a normal user.
RUN useradd --create-home --uid 1000 primity
COPY --chown=primity:primity main.py LICENSE NOTICE ./
COPY --chown=primity:primity src ./src
COPY --chown=primity:primity assets ./assets

# Set environment variable for containerized Qt apps
ENV QT_DEBUG_PLUGINS=0
ENV QT_QPA_PLATFORM=xcb

USER primity
CMD ["python", "main.py"]

