# Setup MongoDB

## Install MongoDB

```
sudo apt update
sudo apt install -y mongodb
sudo systemctl status mongodb # show status
```

## Import Placeholder Data

```
cd vibe-check/database
mongorestore -d vibecheck vibecheck
```

In the future the `-d` flag may become `--nsInclude` (need to check on this).
