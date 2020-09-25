# Vibe Check (2020)
### Lauren McCarthy and Kyle McDonald

As tracking and surveillance solutions are proposed to guide us through the current crisis, we enact another control system through the passive observation of our neighbors. Are they a threat, or essential to retaining our feeling of humanness? We notice our heightened sense of interdependence. Vibe Check appropriates common surveillance tools including face recognition and expression analysis to catalog the emotional effect exhibition visitors have on one another. Some are identified as evoking expressions of happiness, disgust, sadness, surprise, or boredom. Upon entering the exhibition, visitors are playfully alerted to who these people are, and as they leave, they may find they’ve earned this distinction themselves.

Commissioned by HeK and MU for the context of the exhibition [Real Feelings](https://www.hek.ch/en/program/events-en/event/opening-real-feelings.html).

## Setup

As a very first step, install [Anaconda](https://www.anaconda.com/). Then follow the `readme.md` in each folder:

1. `database/`
2. `app/`
3. `face/`
4. `automate/`

### Additional configuration

Disable all desktop notifications:

```
gsettings set org.gnome.desktop.notifications show-banners false
```

## Status check

* CPU should be busy: run `htop` and look for CPU activity.
* GPUs should be busy: run `nvidia-smi`
* Services should be running: `cd automate && ./status`
* Logs should be updating `journalctl -feu vibe-check-face`
* Cameras should be sending data (active) `cd rpi && ./cameras status`

## Start-up and shut-down

Install XBindKeys:

```
sudo apt-get install xbindkeys xbindkeys-config
xbindkeys --defaults > /home/hek/.xbindkeysrc
xbindkeys-config
```

Add an action for `control+shift + q` pointing to:

```
bash /home/hek/Documents/vibe-check/automate/killall-chrome.sh
```

And for `control+shift + q` pointing to:

```
bash /home/hek/Documents/vibe-check/automate/open-chrome.sh
```