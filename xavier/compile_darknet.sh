#1/bin/bash

sudo apt-get update
git clone http://www.github.com/dataplayer12/darknet.git
cd ./darknet
make
mv libdarknet.so ../human_detection/xavier/
cd ../
sudo rm -rf darknet
echo "Darknet library has been compiled and saved"