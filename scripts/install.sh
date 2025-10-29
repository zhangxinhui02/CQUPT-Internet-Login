#!/bin/sh
set -e

cd ..
INSTALL_PATH=$(pwd)
python3 -m venv .venv
.venv/bin/pip3 install -r requirements.txt
cp assets/cqupt-internet /usr/bin
sed -i "s|\${INSTALL_DIR}|${INSTALL_PATH}|g" /usr/bin/cqupt-internet
chmod +x /usr/bin/cqupt-internet
echo
echo "========================================"
echo "Install succeed."
echo "========================================"
echo
