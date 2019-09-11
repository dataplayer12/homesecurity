# Introduction

Software for security monitoring with single or multiple cameras with:
- Raspberry pi zero
- Raspberry pi 3B/4B
- Jetson Nano
- Jetson TX2

## Functions
- Raspberry pi 3: The camera performs motion detection and records a video. The video is sent in an email.
- Jetson Nano: After recording video, an object detection model checks if a person is presentin the video. If yes, the video and a screenshot are sent by email.
- Jetson TX2 + Pi Zeros: A set of 4 raspi zeros stream video over Wi-Fi to a Jetson TX2, which combines inputs from all sources, performs object detection and displays the results on a monitor.

## Configurations
### Raspberry Pi 3
![Architecture 1](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch1.png)
----
### Jetson Nano
![Architecture 2](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch2.png)
----
### Raspberry Pi Zero W + Jetson TX2
![Architecture 3](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch3.png)

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

If you are using a raspberry pi 3/4 or Jetson Nano, you will have to provide email addresses for receiving videos when some activity is observed by the camera. This is done by writing these details to a `confidential.txt` text file.
```Shell
cd homesecurity #be in the base directory of the project
nano confidential.txt #open text file
```
The contents of `confidential.txt` are as follows:

```Text
{"recepients": ["email1", "email2"], "myemail": "senderemail", "mypass": "senderpassword"}
```

You will have to configure the `senderemail` to allow login from your pi. For Gmail, you can do this by enabling two-factor authentication and setting an app-specific password for your gmail account or by downgrading your security settings to allow less secure devices like the pi to access your Google account. No special settings are required on the receiver's email address. Please raise an issue if you have any specific questions.

## Development

This software was written for monitoring the security of my home with a raspberry pi. The section related to raspberry pi 3 has been in use at my home for about two years and there are failsafes built in to prevent issues such as loss of network connection and memory overflow. Since my requirements are well-served with the current version, more features will be added only if requests are made by raising issues. 
**Pull requests which add useful features or failsafes are more than welcome!**
