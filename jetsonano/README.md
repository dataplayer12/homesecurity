- Jetson Nano requires `opencv` and `tensorflow`. The default image for Jetson Nano comes with opencv compiled with CUDA.
Tensorflow for Jetson Nano can be installed by following the official instructions from [NVIDIA](https://devtalk.nvidia.com/default/topic/1048776/jetson-nano/official-tensorflow-for-jetson-nano-/)

- When running inference on TX2 for the first time, You will have to compile the MobileNet SSD model for your version of tensorflow and JetPack. To do so, launch the compile_ssd_mobilenet.py script from project directory.
```
cd homesecurity/ #cd to project directory
python3 jetsontx2/compile_ssd_mobilenet.py
```
- Once the script has run successfully and the model has been exported, you can launch the project using the launch.sh bash script.
```
bash launch.sh
```
