#!/bin/bash


device="jetsontx2" #'raspi3','jetsonano','streampi','jetsontx2'

if [ "$device" == "streampi" ]; then
	cd common/
	python3 stream_video.py
elif [ "$device" == "raspi3" ]; then
	cd raspi3/
	python3 securitycam.py
elif [ "$device" == "jetsonano" ]; then
	cd jetsonano/
	python3 securitycamnano.py
elif [ "$device" == "jetsontx2" ]; then
	cd jetsontx2/
	python3 stream_surveillance.py
fi
