FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

ARG TYPST_VERSION=0.14.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    wget \
    xz-utils \
    libreoffice \
    pandoc \
    ffmpeg \
    imagemagick \
    ghostscript \
    qpdf \
    gdal-bin \
    calibre \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-core \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/typst.tar.xz \
    "https://github.com/typst/typst/releases/download/v${TYPST_VERSION}/typst-x86_64-unknown-linux-musl.tar.xz" \
    && mkdir -p /tmp/typst \
    && tar -xf /tmp/typst.tar.xz -C /tmp/typst --strip-components=1 \
    && mv /tmp/typst/typst /usr/local/bin/typst \
    && chmod +x /usr/local/bin/typst \
    && rm -rf /tmp/typst /tmp/typst.tar.xz

WORKDIR /app

COPY pyproject.toml .
COPY uconvert ./uconvert

RUN pip install --no-cache-dir -e .

WORKDIR /data

ENTRYPOINT ["uconvert"]