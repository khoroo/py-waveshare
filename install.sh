#!/bin/bash

POETRY_DIR=$PWD

# install bcm2835 drivers
cd /tmp
wget "http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz"
tar "zxvf bcm2835-1.60.tar.gz"
cd bcm2835-1.60/
sudo ./configure
sudo make
sudo make check
sudo make install

# install wiringpi
sudo apt-get install wiringpi
wget https://project-downloads.drogon.net/wiringpi-latest.deb
sudo dpkg -i wiringpi-latest.deb
gpio -v

cd $POETRY_DIR
poetry install
