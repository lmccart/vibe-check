# Raspberry Pi setup

## SD card setup

1. Download [RaspiOS Lite](https://downloads.raspberrypi.org/raspios_lite_armhf_latest) from [this page](https://www.raspberrypi.org/downloads/raspberry-pi-os/).
2. Use [Balena Etcher](balena.io/etcher/) to burn the SD card
3. After burning, remove and re-insert the SD card
4. Run `touch /Volumes/boot/ssh` to enable ssh by default.
5. Edit `/Volumes/boot/config.txt` to set `start_x=0`, `gpu_mem=300` and add `dtparam=i2c_vc=on`.
6. Run `touch /Volumes/boot/wpa_supplicant.conf` to create the wifi settings configuration and paste the configuration below.
7. Eject the SD card and put it in the pi.
8. Boot the pi.

Open the wifi settings and paste:

```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="vibe-check"
    psk="duchenne"
}
```

## Setting up the first Pi

First update the firmware:

```
ssh pi@<ip address>
sudo apt update
sudo apt full-upgrade -y
sudo reboot now
```

Then install the dependencies:

```
ssh pi@<ip address>
sudo apt install -y wiringpi i2c-tools libopencv-dev
sudo apt install -y python-opencv python-pip llvm iperf3
pip install llvmlite==0.31.0 numba==0.47.0 numpy requests v4l2
sudo apt autoremove -y
sudo apt clean
sudo chmod u+s /sbin/shutdown
```

And enable the camera and I2C with `sudo raspi-config`:

1. Select "5 Interfacing Options"
2. Select "P1 Camera"
3. Select "Yes"
4. Select "5 Interfacing Options"
5. Select "P5 I2C"
6. Select "Yes"
7. Right arrow key twice to select <Back>, enter
8. Right arrow key twice to select <Finish>, enter

## Setting up remaining Pis

Make an image of the first pi using Disk Utility. Select "compressed" image type. Then use Etcher to create remaining cards.

Load each card into a pi and find the IP address. Then run `./cameras set-hostname <ip> <number>` for example `./cameras set-hostname 192.168.0.195 11`. Finally push the code to the pi with `./cameras update <number>` for example `./cameras update 11`.

Some final scripts are needed to regulate the network connection, run `./cameras exec "sudo bash camera/fix-wlan.sh"`.