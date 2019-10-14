threaded=True

DATA_DIR = './human_detection/' #for storing all files related to object detection model

MODEL = 'ssd_mobilenet_v1_coco' #model name

LABELMAP = DATA_DIR+'labels.txt' #this file should be a .txt

CONFIG_FILE = DATA_DIR+MODEL + '.config'   #config file for detection model

CHECKPOINT_FILE = DATA_DIR+'ssd_mobilenet_v1_coco_2017_11_17/model.ckpt' #checkpoint of trained model

SERIAL_FILE=DATA_DIR+'{}_trt.pb'.format(MODEL)

WINDOW_NAME = 'Home security Monitor'

BBOX_COLOR = (0, 255, 0)  # green

qsize=300 #queue size for frame buffer for each camera
#larger size will result in longer lag but fewer 'Cannot read frame..' messages
