#!/bin/sh
set -e

# 登录检查周期（秒）
INTERVAL=${1:-"60"}

cd ..
cp assets/cqupt-internet-autologin.service /etc/systemd/system
sed -i "s|\${INTERVAL}|${INTERVAL}|g" /etc/systemd/system/cqupt-internet-autologin.service
systemctl daemon-reload
systemctl enable --now cqupt-internet-autologin.service
echo "Install succeed. Service 'cqupt-internet-autologin.service' was enabled and running now."
