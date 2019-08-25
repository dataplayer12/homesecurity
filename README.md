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

## Architectures
### Raspberry Pi 3
![Architecture 1](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch1.png)
----
### Jetson Nano
![Architecture 2](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch2.png)
----
### Raspberry Pi Zero W + Jetson TX2
![Architecture 3](https://github.com/dataplayer12/homesecurity/blob/master/docs/arch3.png)

## Development

This software was written for monitoring the security of my home with a raspberry pi. The section related to raspberry pi 3 has been in use at my home for about two years and there are failsafes built in to prevent issues such as loss of network connection and memory overflow. Since my requirements are well-served with the current version, more features will be added only if requests are made by raising issues. 
**Pull requests which add useful features or failsafes are more than welcome!**
