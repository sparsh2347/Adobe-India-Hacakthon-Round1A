FROM mirror.gcr.io/library/python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7 \
    libtiff-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    ghostscript \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    git \
    curl \
    gfortran \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_RETRIES=10 \
    PIP_NO_CACHE_DIR=1 \
    PIP_INDEX_URL=https://pypi.org/simple

COPY . .

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --retries 10 --timeout 100 --default-timeout=100 -r requirements.txt

CMD ["python", "round1a_main.py", "input", "output"]
