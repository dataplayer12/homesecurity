import cv2, time, os
#import send_email
import queue
import numpy as np

import sys
sys.path.append(os.getcwd()+'/common/')
sys.path.append(os.getcwd()+'/human_detection/')

from config import * #h264_folder, mp4_folder, motion_threshold,log_dir,log_file,countfile
from file_managernano import FileManagerThread, FileCleanerThread, counter

file_q = queue.Queue()

os.environ['TZ']= location
time.tzset()

print(('Time: {}. Starting...'.format(time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()))))
print('Finished importing modules')
print(('Sleeping for {} seconds'.format(initial_sleep)))
time.sleep(initial_sleep)

def gstreamer_pipeline (capture_width=320, capture_height=240, display_width=320, display_height=240, framerate=60, flip_method=0) :   
    return ('nvarguscamerasrc ! ' 
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))

time_since_last_sent=200 #in minutes
time_last_sent=time.time()
file_counter=counter(countfile)

video_num=file_counter.count
if usbcam: #defined in config.py
	camera=cv2.VideoCapture(0)
else:
	camera=cv2.VideoCapture(gstreamer_pipeline(flip_method=0),cv2.CAP_GSTREAMER)

fct=FileCleanerThread()
fct.start()

fmt= FileManagerThread(h264_q=file_q)
fmt.start()

def record_for(rec_time):
    video_num=file_counter.get_current_count()
    this_file='video{}.mp4'.format(video_num)
    if this_file in os.listdir(h264_folder):
        os.remove(h264_folder+this_file)
    #remove this file, if it already exists
    fps=24.0
    size=(320,240)
    writer=cv2.VideoWriter(h264_folder+this_file,cv2.VideoWriter_fourcc(*'MP4V'),fps,size)
    print('Video recording started')
    starttime=time.time()
    while (time.time()-starttime)<rec_time:
        ret,frame=camera.read()
        writer.write(frame)
    writer.release()
    file_counter.update_count()
    file_q.put(this_file)
    #handle_file(filename)

if __name__ == '__main__':
    start=time.time()
    not_beginning=False
    count=0
    fgbg=cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=8, detectShadows=False)
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    time.sleep(1)
    while True:
        ret,frame=camera.read()
        #cv2.imwrite('capture.jpg',image)
        fgmask=fgbg.apply(frame,learningRate=0.1)
        fgmask=cv2.erode(fgmask,kernel,iterations=1)
        motion_magnitude=np.mean(fgmask)
        #print(motion_magnitude)
        count+=1
        time_since_last_sent=(time.time()-time_last_sent)/60

        if count%50==0:
            not_beginning=True
            print(('frame rate={}'.format(count/(time.time()-start))))

        if not_beginning and motion_magnitude>=motion_threshold:
            print('Motion detected!!')
            record_for(20)
            not_beginning=False
            count=0
            fgbg=cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=8, detectShadows=False)
            start=time.time()
        elif count>1000000:
            print('count is 1 million. Setting count to zero')
            count=0

        # if time.localtime().tm_min<2 and time_since_last_sent>58:
