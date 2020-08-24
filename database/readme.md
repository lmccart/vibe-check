# Setup MongoDB

## Install MongoDB

```
sudo apt update
sudo apt install -y mongodb
sudo systemctl status mongodb # show status
```

## Import Placeholder Data

```
mongorestore -d vibecheck vibecheck
```