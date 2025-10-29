#!/bin/sh
set -e

INTERVAL=${1:-"60"}  # 登录检查周期（秒），默认为60

# 判断cqupt-internet命令是否已安装
if command -v cqupt-internet >/dev/null 2>&1; then
    echo "Command 'cqupt-internet' check OK."
else
    echo "Command 'cqupt-internet' required. Install the command first."
    exit 1
fi

# 将服务文件模板复制到/etc/systemd/system目录，并将服务文件中的周期占位符替换实际周期
cd ..
cp assets/cqupt-internet-autologin.service /etc/systemd/system
sed -i "s|\${INTERVAL}|${INTERVAL}|g" /etc/systemd/system/cqupt-internet-autologin.service

# 启用服务
systemctl daemon-reload
systemctl enable --now cqupt-internet-autologin.service

# 安装完毕
echo
echo "========================================"
echo "Install succeed. Service 'cqupt-internet-autologin.service' was enabled and running now."
echo "You can use 'systemctl start/stop cqupt-internet-autologin' to manage the service."
echo "========================================"
echo
