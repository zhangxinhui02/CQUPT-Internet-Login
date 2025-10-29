#!/bin/sh
set -e

cd ..
INSTALL_PATH=$(pwd)

# 判断命令是否已安装
if command -v cqupt-internet >/dev/null 2>&1; then
    echo "Command 'cqupt-internet' has already been installed."
    exit
fi

# 准备Python虚拟环境
python3 -m venv .venv
.venv/bin/pip3 install -r requirements.txt

# 将命令模板复制到/usr/bin目录，并将命令中的路径占位符替换为实际安装路径
cp assets/cqupt-internet /usr/bin
sed -i "s|\${INSTALL_DIR}|${INSTALL_PATH}|g" /usr/bin/cqupt-internet
chmod +x /usr/bin/cqupt-internet

# 安装完毕
echo
echo "========================================"
echo "Install succeed."
echo "========================================"
echo
