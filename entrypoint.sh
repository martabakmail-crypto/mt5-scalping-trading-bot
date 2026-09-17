#!/bin/bash
set -e

rm -f /tmp/.X99-lock /tmp/.X11-unix/X99

echo "Starting virtual display Xvfb on :99..."
Xvfb :99 -screen 0 1024x768x16 &
sleep 2

WINE_BIN=$(which wine || echo "wine")

if [ ! -f "/root/.wine/drive_c/windows/system32/ucrtbase.dll" ]; then
    echo "Installing Microsoft VC++ Runtime (vcrun2015) via Winetricks..."
    winetricks -q vcrun2015 || true
    sleep 3
fi

if [ ! -f "/root/.wine/drive_c/Python311/python.exe" ]; then
    echo "Initializing Wine prefix..."
    wineboot --init || true
    sleep 3

    echo "Extracting Portable Windows Python 3.11 inside Wine..."
    mkdir -p /root/.wine/drive_c/Python311
    wget -q https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip -O /tmp/python-embed.zip
    unzip -o /tmp/python-embed.zip -d /root/.wine/drive_c/Python311
    rm -f /tmp/python-embed.zip

    # Enable site-packages in embedded python
    sed -i 's/#import site/import site/' /root/.wine/drive_c/Python311/python311._pth || true

    echo "Installing pip inside Embedded Windows Python..."
    wget -q https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py
    $WINE_BIN "C:\\Python311\\python.exe" /tmp/get-pip.py || true
    rm -f /tmp/get-pip.py

    echo "Installing MetaTrader 5 Terminal client..."
    if [ -f "/opt/mt5/mt5setup.exe" ]; then
        $WINE_BIN /opt/mt5/mt5setup.exe /auto || true
    fi
fi


echo "Installing/Ensuring compatible Python dependencies..."
$WINE_BIN "C:\\Python311\\python.exe" -m pip install --no-cache-dir -r /app/requirements.txt || true

echo "Starting MT5 Scalping Trading Bot Engine..."
exec $WINE_BIN cmd /c "set PYTHONPATH=Z:\app&& C:\Python311\python.exe Z:\app\main.py"

