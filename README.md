# Daifuku Comitup Fork

See original [here.](http://github.com/davesteele/comitup)

## Changes

- Added zerotier ID and device ID to the view when setting up WiFi

## Building a deb Package

```bash
git clone https://github.com/jerviswebb/comitup.git
tar czvf comitup_1.39.orig.tar.gz comitup
cd comitup
sudo apt-get install debhelper pybuild-plugin-pyproject dh-python python3-setuptools python3-pytest python3-pytest-runner python3-mock python3-cachetools pandoc python3-flask
dpkg-buildpackage -us -uc
cd ..
ls  # you'll now see a .deb file in the directory!
```

## Installing the deb Package

```bash
sudo dpkg -i comitup_1.39-1_all.deb
```
