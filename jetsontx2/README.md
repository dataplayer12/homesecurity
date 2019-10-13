It is expected that your Jetson TX2 already has `numpy` and `opencv` installed.
Install the official tensorflow release for Jetson TX2 by following the instructions from [here](https://devtalk.nvidia.com/default/topic/1038957/jetson-tx2/tensorflow-for-jetson-tx2-/).


When running inference on TX2 for the first time, You will have to compile the MobileNet SSD model for your version of tensorflow and JetPack. To do so, launch the `compile_ssd_mobilenet.py` script from project directory.

```Shell
cd homesecurity/ #cd to project directory
python3 jetsontx2/compile_ssd_mobilenet.py
```
