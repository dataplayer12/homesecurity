# Code adapted from Tensorflow Object Detection Framework
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
# Tensorflow Object Detection Detector

import numpy as np
import tensorflow as tf
import cv2
import time

class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def processFrame(self, image):
        # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
        #start_time = time.time()
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: image_np_expanded})
        #end_time = time.time()

        #print("Elapsed Time:", end_time-start_time)

        im_height, im_width,_ = image.shape
        boxes_list = [None for i in range(boxes.shape[1])]
        for i in range(boxes.shape[1]):
            boxes_list[i] = (int(boxes[0,i,0] * im_height),
                        int(boxes[0,i,1]*im_width),
                        int(boxes[0,i,2] * im_height),
                        int(boxes[0,i,3]*im_width))

        return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()

model_path = 'ssd_mobilenet_v1_coco_2017_11_17/frozen_inference_graph.pb'
odapi = DetectorAPI(path_to_ckpt=model_path)
threshold = 0.5

def determine_if_person_in(fname,threshold=0.5,is_nano=False):
    print('Analyzing file {} to find human in video'.format(fname))
    jpeg_name=fname[:fname.rfind('.')+1]+'jpg'
    if not is_nano:
        return True,'There may be someone in the room'
        
    video=cv2.VideoCapture(fname)
    n_frames=video.get(cv2.CAP_PROP_FRAME_COUNT)
    max_budget=int(8*n_frames/100) if is_nano else int(4*n_frames/100)
    #print('max budget: {}'.format(max_budget))
    random_frames=np.random.permutation(int(n_frames))
    chosen_frames=random_frames[:max_budget]
    #print('random frames are: {}'.format(random_frames))
    #print('Chosen frames are: {}'.format(chosen_frames))

    for cf in chosen_frames:
        video.set(cv2.CAP_PROP_POS_FRAMES,cf)
        ret,frame=video.read()
        if not ret:
            video.release()
            #print('Could not read frame. Returning')
            message='Could not check the video. '
            print(message)
            return True, message
        else:
            boxes, scores, classes, num= odapi.processFrame(frame)

            good_indices=np.where(np.array(scores)>threshold)
            #print('Good classes: {}'.format(np.array(classes)[good_indices]))
            result=(1 in np.array(classes)[good_indices])
            if result:
                video.release()
                #print('Person found in frame {}. Returning'.format(cf))
                for i in range(len(boxes)):
                    if classes[i] == 1 and scores[i] > threshold:
                        box=boxes[i]
                        cv2.rectangle(frame,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)
                cv2.imwrite(jpeg_name,frame)
                message='There is someone in the room. '
                print(message)
                return True,message #if person is found in any frame, the function returns True
    message='Person not found in video. '
    print(message)
    return False,message


if __name__ == "__main__":
    cap = cv2.VideoCapture('video297.mp4')
    count=0
    while True:
        r, img = cap.read()
        #img = cv2.resize(img, (1280, 720))
        count+=r        
        boxes, scores, classes, num = odapi.processFrame(img)

        # Visualization of the results of a detection.

        for i in range(len(boxes)):
            # Class 1 represents human
            if classes[i] == 1 and scores[i] > threshold:
                box = boxes[i]
                cv2.rectangle(img,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)

        cv2.imshow("preview", img)
        #if count%50==0:
        #    cv2.imwrite('result{}.jpg'.format(count),img)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break