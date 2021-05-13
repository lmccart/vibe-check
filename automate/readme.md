# Automation

## Load multiple windows in kiosk mode

First build multibrowse: `bash build-multibrowse.sh` If you have a problem building multibrowse, make sure to restart the shell so `pip` is available.

Then run `bash open-chrome.sh`.

Make a shell script executable:

```
gsettings set org.gnome.nautilus.preferences executable-text-activation 'launch'
```

## Create services for background tasks

Run `sudo bash setup-services.sh` to setup the `vibe-check-cluster`, `vibe-check-app`, `vibe-check-face` services.

To check the status, run `journalctl -feu vibe-check-cluster`.

To restart after making changes to code, run `sudo systemctl restart vibe-check-cluster`.

## Take screenshots

Install `sudo apt install scrot` then `bash screenshot.sh` and look in `screenshots/` for `0-thumb.jpg` and `1-thumb.jpg`.