#!/bin/sh
set -e

INTERVAL=${1:-"60"}  # 登录检查周期（秒），默认为60

cd ..
cp assets/cqupt-internet-autologin.service /etc/systemd/system
sed -i "s|\${INTERVAL}|${INTERVAL}|g" /etc/systemd/system/cqupt-internet-autologin.service
systemctl daemon-reload
systemctl enable --now cqupt-internet-autologin.service
echo
echo "========================================"
echo "Install succeed. Service 'cqupt-internet-autologin.service' was enabled and running now."
echo "You can use 'systemctl start/stop cqupt-internet-autologin' to manage the service."
echo "========================================"
echo
