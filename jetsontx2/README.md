It is expected that your Jetson TX2 already has `numpy` and `opencv` installed.
Install the official tensorflow release for Jetson TX2 by following the instructions from [here](https://devtalk.nvidia.com/default/topic/1038957/jetson-tx2/tensorflow-for-jetson-tx2-/).


When running inference on TX2 for the first time, You will have to compile the MobileNet SSD model for your version of tensorflow and JetPack. To do so, launch the `compile_ssd_mobilenet.py` script from project directory.

```Shell
cd homesecurity/ #cd to project directory
python3 jetsontx2/compile_ssd_mobilenet.py
```
## Note on network latency:

In this application, the performance of the jetson is limited by the bandwidth of your local network (not to be confused with neural network ;) ). The 4 IP cameras as well as the jetson may all be on Wi-Fi, and all the activity can be challenging for a router to keep up with. Moreover, since the raspberry pi zeros support only 802.11 b/g/n standards (2.4 GHz band), their latency is higher than 5 GHz bands supported by default antenna on the jetson's carrier board.

If you see many "Cannot read camera at.." messages, you have two options:

- If you have opened a camera stream on a browser, please close it as streaming to the browser doubles the work the pi has to do.
- Try increasing `qsize` in `jetsontx2/jetson_config.py`. This will reduce the frequency of these messages, but will result in higher lag between the screen and camera. If the lag becomes too much, reduce qsize and try next option.
- Try setting `threaded = False` in the same file. This will get rid of the benefits of multi-threading and read all cameras in series from the same thread. It will reduce your fps by ~2, but will get rid of ugly error screens.
- Try connecting the jetson to the network via ethernet and if possible the pi zeros as well. If you must keep the jetson on Wi-Fi, please use a router that supports 5 GHz band (802.11 ac in marketing speak).
