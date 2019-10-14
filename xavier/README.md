It is expected that your Jetson TX2 already has `numpy` and `opencv` installed.

We use darknet for object detection in Jetson Xavier.

The file `libdarknet.so` provided in this folder has been compiled for JetPack 4.2.1. If the file provided does not work and you would like to compile darknet yourself, please follow the instructions [here](https://pysource.com/2019/08/29/yolo-v3-install-and-run-yolo-on-nvidia-jetson-nano-with-gpu/). Although these instructions are for Jetson Nano, they will work for Jetson Xavier as well. In step 4, in addition to setting `GPU`, `CUDNN`, `OPENCV` to `1`, please set `LIBSO` and `OPENMP` to `1` as well.

```Shell
sudo apt-get update
cd ~
git clone http://www.github.com/dataplayer12/darknet.git
cd darknet
make
```
After you run `make`, there will be a file called `libdarknet.so`. Please copy that file to `homesecurity/human_detection/xavier/` and replace the current version of `libdarknet.so`.
