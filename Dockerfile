FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99
ENV WINEPREFIX=/root/.wine
ENV WINEDEBUG=-all

# Install wine, winetricks, cabextract, xvfb, unzip, curl, wget
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wine \
        winetricks \
        cabextract \
        xvfb \
        unzip \
        curl \
        wget \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Download MT5 Terminal Installer
RUN mkdir -p /opt/mt5 && \
    wget -q https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe -O /opt/mt5/mt5setup.exe || true


WORKDIR /app

COPY . .

RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
