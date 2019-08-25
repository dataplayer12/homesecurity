#!/bin/bash

device="jetsonano" #'raspi3','jetsonano','streampi','jetsontx2'

if [ "$device" == "streampi" ]; then
	cd common/
	python3 stream_video.py
elif [ "$device" == "raspi3" ]; then
	#cd raspi3/
	#logname="logs/camlog$(ls -l logs|wc -l).txt"
	#touch $logname
	#echo $logname
	nohup python3 -u raspi3/securitycam.py &> logs/camlog$(ls -l ./logs|wc -l).txt &
	#nohup python3 securitycam.py &
elif [ "$device" == "jetsonano" ]; then
	#cd jetsonano/
	python3 jetsonano/securitycamnano.py
elif [ "$device" == "jetsontx2" ]; then
	cd jetsontx2/
	python3 stream_surveillance.py
fi
