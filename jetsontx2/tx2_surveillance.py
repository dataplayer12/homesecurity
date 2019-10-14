import cv2
import numpy as np

import sys
import time
import logging
import datetime

import numpy as np
import cv2
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt

from utils.od_utils import read_label_map, load_trt_pb, detect
from utils.visualization import BBoxVisualization
from streamutils import VideoStreamHandler
from tx2_config import threaded, MODEL, LABELMAP, WINDOW_NAME, BBOX_COLOR

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


def show_bounding_boxes(img, box, conf, cls, cls_dict):
    """Draw detected bounding boxes on the original image."""
    font = cv2.FONT_HERSHEY_DUPLEX
    for bb, cf, cl in zip(box, conf, cls):
        cl = int(cl)
        y_min, x_min, y_max, x_max = bb[0], bb[1], bb[2], bb[3]
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), BBOX_COLOR, 2)
        txt_loc = (max(x_min, 5), max(y_min-3, 20))
        cls_name = cls_dict.get(cl, 'CLASS{}'.format(cl))
        txt = '{} {:.2f}'.format(cls_name, cf)
        cv2.putText(img, txt, txt_loc, font, 0.8, BBOX_COLOR, 1)
    return img

def loop_and_detect(stream_handler, tf_sess, conf_th, vis, od_type):
    """Loop, grab images from camera, and do object detection.

    # Arguments
      stream_handler: the stream handler object.
      tf_sess: TensorFlow/TensorRT session to run SSD object detection.
      conf_th: confidence/score threshold for object detection.
      vis: for visualization.
    """
    show_fps = True
    full_scrn = True
    fps = 0.0
    tic = time.time()
    while True:
        if cv2.getWindowProperty(WINDOW_NAME, 0) < 0:
            # Check to see if the user has closed the display window.
            # If yes, terminate the while loop.
            break

        img = stream_handler.read_streams()
        box, conf, cls = detect(img, tf_sess, conf_th, od_type=od_type)
        cls-=1
        img = vis.draw_bboxes(img, box, conf, cls)
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

    # build the class (index/name) dictionary from labelmap file
    logger.info('reading label map')
    cls_dict = read_label_map(LABELMAP)

    pb_path = './human_detection/{}_trt.pb'.format(MODEL)
    log_path = './jetsontx2/logs/{}_trt'.format(MODEL)

    logger.info('opening camera device/file')

    url1='http://pi1.local:8000/stream.mjpg'
    url2='http://pi2.local:8000/stream.mjpg'
    url3='http://pi3.local:8000/stream.mjpg'
    url4='http://pi4.local:8000/stream.mjpg'
    
    stream_handler=VideoStreamHandler([url1,url2,url3,url4],threaded=threaded,resolution=(360,640))

    logger.info('loading TRT graph from pb: %s' % pb_path)
    trt_graph = load_trt_pb(pb_path)

    logger.info('starting up TensorFlow session')
    tf_config = tf.ConfigProto()
    tf_config.gpu_options.allow_growth = True
    tf_sess = tf.Session(config=tf_config, graph=trt_graph)

    logger.info('warming up the TRT graph with a dummy image')
    od_type = 'ssd'
    dummy_img = np.zeros((720, 1280, 3), dtype=np.uint8)
    _, _, _ = detect(dummy_img, tf_sess, conf_th=.3, od_type=od_type)

    # grab image and do object detection (until stopped by user)
    logger.info('starting to loop and detect')
    vis = BBoxVisualization(cls_dict)
    open_display_window(1280, 720)
    loop_and_detect(stream_handler, tf_sess, 0.2, vis, od_type=od_type)
    if threaded:
        stream_handler.close()
    logger.info('cleaning up')
    tf_sess.close()
    stream_handler.join_streams()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
