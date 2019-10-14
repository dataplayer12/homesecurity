#!/bin/bash

BASEDIR=$(pwd)

DEVICE="jetsontx2"
#OPTIONS: 'raspi3','jetsonano','streampi','jetsontx2', 'xavier'
#In principle, the device streampi can be anything,
#but, a pi zero is most commonly used.

function setupdirs {

if [ ! -d "$BASEDIR/h264_videos/" ]
then
    mkdir h264_videos
    echo 'Setting up h264 directory'
fi

if [ ! -d "$BASEDIR/mp4_videos/" ]
then
    mkdir mp4_videos
    echo 'Setting up MP4 directory'
fi
}

if [ "$DEVICE" == "streampi" ]; then
	cd common/
	python3 stream_video.py

elif [ "$DEVICE" == "raspi3" ]; then
	setupdirs;
	nohup python3 -u raspi3/securitycam.py &> logs/camlog$(ls -l ./logs|wc -l).txt &

elif [ "$DEVICE" == "jetsonano" ]; then
	setupdirs;
	python3 jetsonano/securitycamnano.py

elif [ "$DEVICE" == "jetsontx2" ]; then
	python3 jetsontx2/tx2_surveillance.py

elif [ "$DEVICE" == "xavier" ]; then
	python3 xavier/xavier_surveillance.py

fi
