# Introduction

Software for security monitoring with single or multiple cameras with:
- Raspberry pi zero
- Raspberry pi 3B/4B
- Jetson Nano
- Jetson TX2
- Jetson AGX Xavier

## Functions
- Raspberry pi 3: The camera performs motion detection and records a video. The video is sent in an email.
- Jetson Nano: After recording video, an object detection model checks if a person is presentin the video. If yes, the video and a screenshot are sent by email.
- Jetson TX2 + Pi Zeros: A set of 4 raspi zeros stream video over Wi-Fi to a Jetson TX2, which combines inputs from all sources, performs object detection and displays the results on a monitor.
- Jetson Xavier + Pi Zeros: Same as that of TX2

## Configurations
### Raspberry Pi 3
![Architecture 1](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch1.png)
----
### Jetson Nano
![Architecture 2](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch2.png)
----
### Raspberry Pi Zero W + Jetson TX2
![Architecture 3](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch3.png)
----
### Raspberry Pi Zero W + Jetson Xavier
![Architecture 4](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch4.png)

## Setup
Clone the repo and choose the device by modifying the `DEVICE` variable in the `launch.sh` script.
```Shell
git clone http://www.github.com/dataplayer12/homesecurity.git
cd ./homesecurity
nano launch.sh #Edit the DEVICE variable to be one of the four options described in the comments
bash launch.sh
```
You may have to install some dependecies in order for the script to work. Instructions for dependencies for each device are in their respective directories:

- [Raspberry Pi Zero](https://github.com/dataplayer12/homesecurity/tree/master/common)
- [Raspberry Pi 3/4](https://github.com/dataplayer12/homesecurity/tree/master/raspi3)
- [Jetson Nano](https://github.com/dataplayer12/homesecurity/tree/master/jetsonano)
- [Jetson TX2](https://github.com/dataplayer12/homesecurity/tree/master/jetsontx2)
- [Jetson Xavier](https://github.com/dataplayer12/homesecurity/tree/master/xavier)

If you are using a raspberry pi 3/4 or Jetson Nano, you will have to provide email addresses for receiving videos when some activity is observed by the camera. This is done by writing these details to a `confidential.txt` text file.
```Shell
cd homesecurity #be in the base directory of the project
nano confidential.txt #open text file
```
The contents of `confidential.txt` are as follows:

```Text
{"recepients": ["email1", "email2"], "myemail": "senderemail", "mypass": "senderpassword"}
```

You will have to configure the `senderemail` to allow login from your pi. For Gmail, you can do this by enabling two-factor authentication and setting an app-specific password for your gmail account or by downgrading your security settings to allow less secure devices like the pi to access your Google account. No special settings are required on the receiver's email address. The `confidential.txt` file will never be tracked or uploaded to your GitHub repo if you are forking the project and developing it further. Please raise an issue if you have any specific questions.

## Note on network latency on TX2 and Xavier:

In this application, the performance of the jetson is limited by the bandwidth of your local network (not to be confused with neural network ;) ). The 4 IP cameras as well as the jetson may all be on Wi-Fi, and all the activity can be challenging for a router to keep up with. Moreover, since the raspberry pi zeros support only 802.11 b/g/n standards (2.4 GHz band), their latency is higher than 5 GHz bands supported by default antenna on the jetson's carrier board.

If you see many "Cannot read camera at.." messages, you have a few options:

- If you have opened a camera stream on a browser, please close it as streaming to the browser doubles the work the pi has to do.
- Try increasing `qsize` in `jetsontx2/tx2_config.py` or `xavier/xavier_config.py`. This will reduce the frequency of these messages, but will result in higher lag between the screen and camera. If the lag becomes too much, reduce qsize and try next option.
- Try setting `threaded = False` in the same file. This will get rid of the benefits of multi-threading and read all cameras in series from the same thread. It will reduce the display fps by ~2 on TX2, but will get rid of ugly error screens.
- Try connecting the jetson to the network via ethernet and if possible the pi zeros as well. If you must keep the jetson on Wi-Fi, please use a router that supports 5 GHz band (802.11 ac in marketing speak).


## Development

This software was written for monitoring the security of my home with a raspberry pi. The section related to raspberry pi 3 has been in use at my home for about two years and there are failsafes built in to prevent issues such as loss of network connection and memory overflow. Since my requirements are well-served with the current version, more features will be added only if requests are made by raising issues. 
**Pull requests which add useful features or failsafes are more than welcome!**
