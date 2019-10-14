from ctypes import *
import cv2
import numpy as np
import sys
import time
import logging
import datetime
import math
import random
import os
import darknet
import re
from streamutils import VideoStreamHandler
from xavier_config import threaded, WINDOW_NAME, BBOX_COLOR, configPath, weightPath, metaPath

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img,scale=(1.0,1.0)):
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))

        pt1 = (int(scale[0]*xmin), int(scale[1]*ymin))
        pt2 = (int(scale[0]*xmax), int(scale[1]*ymax))

        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)

    return img

def draw_help_and_fps(img, fps):
    """Draw help message and fps number at top-left corner of the image."""
    help_text = datetime.datetime.now().strftime("%A, %B %d %Y %X") #"'Esc' to Quit, 'H' for FPS & Help, 'F' for Fullscreen"
    font = cv2.FONT_HERSHEY_PLAIN
    line = cv2.LINE_AA

    fps_text = 'FPS: {:.1f}'.format(fps)
    cv2.putText(img, help_text, (11, 20), font, 1.0, (32, 32, 32), 4, line)
    cv2.putText(img, help_text, (10, 20), font, 1.0, (240, 240, 240), 1, line)
    cv2.putText(img, fps_text, (11, 50), font, 1.0, (32, 32, 32), 4, line)
    cv2.putText(img, fps_text, (10, 50), font, 1.0, (240, 240, 240), 1, line)
    return img

def open_display_window(width, height):
    """Open the cv2 window for displaying images with bounding boxeses."""
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, width, height)
    cv2.moveWindow(WINDOW_NAME, 0, 0)
    cv2.setWindowTitle(WINDOW_NAME, WINDOW_NAME)
    set_full_screen(True)

def set_full_screen(full_scrn):
    """Set display window to full screen or not."""
    prop = cv2.WINDOW_FULLSCREEN if full_scrn else cv2.WINDOW_NORMAL
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, prop)

def loop_and_detect(stream_handler, conf_th):
    """Loop, grab images from camera, and do object detection.

    # Arguments
      stream_handler: the stream handler object.
      conf_th: confidence/score threshold for object detection.
    """
    show_fps = True
    full_scrn = True
    fps = 0.0

    netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1

    metaMain = darknet.load_meta(metaPath.encode("ascii"))

    tic = time.time()
    img=stream_handler.read_streams()

    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                    darknet.network_height(netMain),3)
    
    scale=(float(img.shape[1])/darknet.network_width(netMain),\
        float(img.shape[0])/darknet.network_height(netMain))

    while True:
        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            # Check to see if the user has closed the display window.
            # If yes, terminate the while loop.
            break

        frame_read = stream_handler.read_streams()
        frame_rgb=frame_read[:,:,::-1]
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)
        
        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=conf_th)
        
        img = cvDrawBoxes(detections, frame_read, scale)
    
        if show_fps:
            img = draw_help_and_fps(img, fps)
        cv2.imshow(WINDOW_NAME, img)
        toc = time.time()
        curr_fps = 1.0 / (toc - tic)
        # calculate an exponentially decaying average of fps number
        fps = curr_fps if fps == 0.0 else (fps*0.9 + curr_fps*0.1)
        tic = toc

        key = cv2.waitKey(1)
        if key == ord('q') or key == ord('Q'):  # q key: quit program
            break
        elif key == ord('H') or key == ord('h'):  # Toggle help/fps
            show_fps = not show_fps
        elif key == ord('F') or key == ord('f'):  # Toggle fullscreen
            full_scrn = not full_scrn
            set_full_screen(full_scrn)


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Ask tensorflow logger not to propagate logs to parent (which causes
    # duplicated logging)
    logging.getLogger('tensorflow').propagate = False

    logger.info('opening camera device/file')

    url1='http://pi1.local:8000/stream.mjpg'
    url2='http://pi2.local:8000/stream.mjpg'
    url3='http://pi3.local:8000/stream.mjpg'
    url4='http://pi4.local:8000/stream.mjpg'
    
    stream_handler=VideoStreamHandler([url1,url2,url3,url4],threaded=threaded,resolution=(360,640))
    time.sleep(5)
    # grab image and do object detection (until stopped by user)
    logger.info('starting to loop and detect')
    open_display_window(1280, 720)
    loop_and_detect(stream_handler, 0.2)
    if threaded:
        stream_handler.close()
    logger.info('cleaning up')
    stream_handler.join_streams()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
