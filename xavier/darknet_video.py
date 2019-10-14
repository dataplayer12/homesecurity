from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
import darknet
import re

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img,scale=(1.0,1.0),fps=0.0):
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

        cv2.putText(img, 'Network FPS: {:.2f}'.format(fps), (11, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, [255, 255, 255], 4)

    return img


netMain = None
metaMain = None
altNames = None


def YOLO():

    global metaMain, netMain, altNames
    configPath = "./cfg/yolov3-tiny.cfg"
    weightPath = "./yolov3-tiny.weights"
    metaPath = "./cfg/coco.data"
    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")
    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")
    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")
    if netMain is None:
        netMain = darknet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    if metaMain is None:
        metaMain = darknet.load_meta(metaPath.encode("ascii"))
    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass
    #cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture("nyc.mp4")
    nframes=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    count=0
    cap.set(3, 1280)
    cap.set(4, 720)
    fps=cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(
        "nycoutput.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps,
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    print("Starting the YOLO loop...")

    # Create an image we reuse for each detect
    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                    darknet.network_height(netMain),3)

    ret, frame_read = cap.read()
    count+=ret
    scale=(float(cap.get(cv2.CAP_PROP_FRAME_WIDTH))/darknet.network_width(netMain),\
        float(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))/darknet.network_height(netMain))
    netfps=0.0
    while ret:
        count+=1
        frame_rgb = frame_read[:,:,::-1]
        frame_resized = cv2.resize(frame_rgb,
                                   (darknet.network_width(netMain),
                                    darknet.network_height(netMain)),
                                   interpolation=cv2.INTER_LINEAR)

        
        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
        prev_time = time.time()
        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
        netfps=0.9*netfps+0.1/(time.time()-prev_time)
        image = cvDrawBoxes(detections, frame_read, scale,fps=netfps)
        #image = image[:,:,::-1]

        out.write(image)
        #cv2.imshow('Demo', image)
        #cv2.waitKey(3)
        if (count%1000==0):
            print("Progress={:.2f}\%".format(count*100/nframes))
        ret, frame_read = cap.read()

    cap.release()
    out.release()

if __name__ == "__main__":
    start=time.time()
    YOLO()
    finish=time.time()
    print('Total time taken to process video= {:.2f}'.format(finish-start))
