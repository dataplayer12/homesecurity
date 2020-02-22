Raspberry pi 3/4 requires `picamera`, `numpy` and `opencv`:
```Shell
sudo apt-get update
sudo apt-get install python-picamera python3-picamera
sudo apt-get install python3-pip
sudo pip3 install "picamera[array]"
sudo apt-get install python3-opencv
sudo apt install -y gpac
pip3 install tensorflow
```
For best results, compile opencv natively on the Pi with ARM optimizations. You can use the script `install_optimized_opencv.sh` for this:

```Shell
cd raspi3/
sudo chmod +x install_optimized_opencv.sh
sudo ./install_optimized_opencv.sh #this script will take a long time to execute.
```

Credit:
These instructions are courtesy of an excellent blog post from [pyimagesearch](https://www.pyimagesearch.com/2017/10/09/optimizing-opencv-on-the-raspberry-pi/) teaching how to compile opencv for best performance on raspberry pi.
