# setup networking

# cat >/etc/wpa_supplicant/wpa_supplicant.conf <<EOL
# country=US
# ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
# update_config=1

# network={
#     ssid="vibe-check"
#     psk="duchenne"
# }
# EOL

# setup wpa to scan every 2 minutes
# https://www.raspberrypi.org/forums/viewtopic.php?p=1432916#p1432916

# cat >/usr/local/bin/wpaping <<EOL
# #!/bin/bash
# while : ;
# do
#     iwconfig wlan0 power off # disable power management
#     wpa_cli -i wlan0 scan
#     sleep 120
# done
# EOL

# chmod +x /usr/local/bin/wpaping

# cat >/lib/systemd/system/wpaping.service <<EOL
# [Unit]
# Description=WPA Supplicant pinger
# Requires=network-online.target

# [Service]
# ExecStart=/usr/local/bin/wpaping
# User=root
# StandardInput=null
# StandardOutput=null
# StandardError=null
# Restart=on-failure

# [Install]
# WantedBy=multi-user.target
# EOL

# systemctl daemon-reload

# systemctl enable wpaping.service
# systemctl start wpaping.service

cat >/lib/systemd/system/vibecheck.service <<EOL
[Unit]
Description=Vibe Check Camera
Requires=network-online.target

[Service]
WorkingDirectory=/home/pi/camera
ExecStart=/home/pi/camera/stream.py
User=pi
StandardInput=null
StandardOutput=append:/var/log/vibecheck.log
StandardError=append:/var/log/vibecheck.err.log
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload

systemctl enable vibecheck.service
systemctl start vibecheck.service