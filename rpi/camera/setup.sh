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