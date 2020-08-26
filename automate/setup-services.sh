USER=$SUDO_USER
SERVICES_DIR=/etc/systemd/system/

# vibe-check-cluster
cat >$SERVICES_DIR/vibe-check-cluster.service <<EOL
[Unit]
Description=Vibe Check Cluster
After=mongodb.service

[Service]
WorkingDirectory=/home/$USER/Documents/vibe-check/database
ExecStart=/home/$USER/Documents/vibe-check/database/run.sh
User=$USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# vibe-check-app
cat >$SERVICES_DIR/vibe-check-app.service <<EOL
[Unit]
Description=Vibe Check App
After=mongodb.service

[Service]
WorkingDirectory=/home/$USER/Documents/vibe-check/app
ExecStart=/home/$USER/Documents/vibe-check/app/run.sh
User=$USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

# vibe-check-face
cat >$SERVICES_DIR/vibe-check-face.service <<EOL
[Unit]
Description=Vibe Check Face
After=mongodb.service

[Service]
WorkingDirectory=/home/$USER/Documents/vibe-check/face
ExecStart=/home/$USER/Documents/vibe-check/face/run.sh
User=$USER
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload

systemctl enable vibe-check-cluster
systemctl start vibe-check-cluster

systemctl enable vibe-check-app
systemctl start vibe-check-app

systemctl enable vibe-check-face
systemctl start vibe-check-face