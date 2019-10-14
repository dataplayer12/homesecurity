threaded=True

configPath = "./human_detection/xavier/yolov3-tiny.cfg"
weightPath = "./human_detection/xavier/yolov3-tiny.weights"
metaPath = "./human_detection/xavier/coco.data"

WINDOW_NAME = 'Home security Monitor'

BBOX_COLOR = (255, 255, 0)  # green

qsize=100 #queue size for frame buffer for each camera
#larger size will result in longer lag but fewer 'Cannot read frame..' messages
