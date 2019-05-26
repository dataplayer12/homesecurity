from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2, time, os
#import send_email
import queue
import numpy as np
import sys
sys.path.append(os.getcwd()+'/common/')
from config import * #h264_folder, mp4_folder, motion_threshold,log_dir,log_file,countfile
from file_manager import FileManagerThread, FileCleanerThread, counter

file_q = queue.Queue()

os.environ['TZ']= location
time.tzset()

print(('Time: {}. Starting...'.format(time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime()))))
print('Finished importing modules')
print(('Sleeping for {} seconds'.format(initial_sleep)))
time.sleep(initial_sleep)

camera=PiCamera()
camera.resolution=(320,240)
camera.vflip=True

time_since_last_sent=200 #in minutes
time_last_sent=time.time()
file_counter=counter(countfile)

video_num=file_counter.count

fct=FileCleanerThread()
fct.start()

fmt= FileManagerThread(h264_q=file_q)
fmt.start()

def record_for(rec_time):
    video_num=file_counter.get_current_count()
    this_file='video{}.h264'.format(video_num)
    if this_file in os.listdir(h264_folder):
        os.remove(h264_folder+this_file)
    #remove this file, if it already exists

    camera.start_recording(h264_folder+this_file)
    print('Video recording started')
    camera.wait_recording(rec_time)
    camera.stop_recording()
    file_counter.update_count()
    file_q.put(this_file)
    #handle_file(filename)

if __name__ == '__main__':
    start=time.time()
    not_beginning=False
    count=0
    fgbg=cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=8, detectShadows=False)
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
    while True:
        rawCapture=PiRGBArray(camera)
        camera.capture(rawCapture,format="bgr",use_video_port=True)
        frame=rawCapture.array
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
