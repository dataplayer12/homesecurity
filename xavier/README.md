It is expected that your Jetson TX2 already has `numpy` and `opencv` installed.

We use darknet for object detection in Jetson Xavier.

The file `libdarknet.so` provided in this folder has been compiled for JetPack 4.2.1. If the file provided does not work and you would like to compile darknet yourself, please run the commands below:

```Shell
cd homesecurity/ #cd to project directory
sudo ./xavier/compile_darknet.sh
```