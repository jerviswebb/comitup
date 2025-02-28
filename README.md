# Daifuku Comitup Fork

See original [here.](http://github.com/davesteele/comitup)

## Changes

- Added zerotier ID and device ID to the view when setting up WiFi

## Building a deb Package

**_IMPORTANT: THIS MUST BE DONE ON A RASPBERRY PI! THE DEPENDENCIES ARE ARM-SPECIFIC!_**

### Debian 11 (bullseye) (OLD RPi OS)

```bash
git clone https://github.com/jerviswebb/comitup.git
tar czvf comitup_1.39.orig.tar.gz comitup
cd comitup
echo -e "deb http://deb.debian.org/debian/ stable main\ndeb-src http://deb.debian.org/debian/ stable main" | sudo tee -a /etc/apt/sources.list
sudo apt-get update
sudo apt-get install debhelper pybuild-plugin-pyproject dh-python python3-setuptools python3-pytest python3-pytest-runner python3-mock python3-cachetools pandoc python3-flask
dpkg-buildpackage -us -uc # build the package without signing it
cd ..
ls  # you'll now see a .deb file in the directory!
```

### Debian 12 (bookworm) (RPi OS)

```bash
git clone https://github.com/jerviswebb/comitup.git
tar czvf comitup_1.43.orig.tar.gz comitup
cd comitup
echo -e "deb http://davesteele.github.io/comitup/repo comitup main" | sudo tee -a /etc/apt/sources.list
wget https://davesteele.github.io/key-366150CE.pub.txt
sudo apt-key add key-366150CE.pub.txt
sudo apt-get update #ignore warning about version id change from 12.8 -> 12.9
sudo apt-get insatll debhelper pybuild-plugin-pyproject dh-python python3-setuptools python3-pytest python3-pytest-runner python3-mock python3-cachetools pandoc python3-flask python3-networkmanager python3-gi python3-dbus python3-cairo iptables libcairo2
dpkg-buildpackage -us -uc # builds without signing
cd ..
ls # you'll see a .deb file in the directory!
```

## Installing the deb Package

### Debian 11 (bullseye) (OLD RPi OS)

```bash
sudo dpkg -i comitup_1.39-1_all.deb
sudo apt-get install -f # to install missing dependencies reported by dpkg
sudo systemctl enable NetworkManager.service
sudo sed -i '$ s/^/#/' /etc/network/interfaces # comment out the import line in /etc/network/interfaces to allow NetworkManager to manage the interfaces
sudo systemctl mask systemd.resolved
sudo rm -rf /etc/wpa_supplicant/wpa_supplicant.conf # remove the default wpa_supplicant configuration so that NetworkManager can manage the WiFi
sudo reboot now # reboot the system to apply the changes
```

### Debian 12 (bookworm) (RPi OS)

```bash
sudo dpkg -i comitup_1.43-1_all.deb
sudo apt-get install -f # to install missing dependencies reported by dpkg
sudo systemctl enable NetworkManager.service
sudo systemctl mask systemd.resolved
sudo reboot now # reboot the system to apply the changes
```
