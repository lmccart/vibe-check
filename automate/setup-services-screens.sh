USER=$SUDO_USER
SERVICES_DIR=/etc/systemd/system/

# vibe-check-screens
cat >$SERVICES_DIR/vibe-check-screens.service <<EOL
[Unit]
Description=Vibe Check Screens
After=mongodb.service

[Service]
WorkingDirectory=/home/$USER/Documents/vibe-check/automate
ExecStart=/home/$USER/Documents/vibe-check/automate/connect_screen.py
User=$USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload

systemctl enable vibe-check-screens
systemctl start vibe-check-screens