'''od_utils.py

Object detection utility functions.
'''


import time

import numpy as np
import cv2
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt


MEASURE_MODEL_TIME = False
avg_time = 0.0


def read_label_map(path_to_labels):
    """Read from the label map file and return a class dictionary which
    maps class id (int) to the corresponding display name (string).

    Reference:
    https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb
    """
    from object_detection.utils import label_map_util

    category_index = label_map_util.create_category_index_from_labelmap(
        path_to_labels)
    cls_dict = {int(x['id']): x['name'] for x in category_index.values()}
    num_classes = max(c for c in cls_dict.keys()) + 1
    # add missing classes as, say,'CLS12' if any
    return {i: cls_dict.get(i, 'CLS{}'.format(i)) for i in range(num_classes)}


def build_trt_pb(model_name, pb_path, download_dir='data'):
    """Build TRT model from the original TF model, and save the graph
    into a pb file for faster access in the future.

    The code was mostly taken from the following example by NVIDIA.
    https://github.com/NVIDIA-Jetson/tf_trt_models/blob/master/examples/detection/detection.ipynb
    """
    from tf_trt_models.detection import download_detection_model
    from tf_trt_models.detection import build_detection_graph
    from utils.egohands_models import get_egohands_model

    if 'coco' in model_name:
        config_path, checkpoint_path = \
            download_detection_model(model_name, download_dir)
    else:
        config_path, checkpoint_path = \
            get_egohands_model(model_name)
    frozen_graph_def, input_names, output_names = build_detection_graph(
        config=config_path,
        checkpoint=checkpoint_path
    )
    trt_graph_def = trt.create_inference_graph(
        input_graph_def=frozen_graph_def,
        outputs=output_names,
        max_batch_size=1,
        max_workspace_size_bytes=1 << 26,
        precision_mode='FP16',
        minimum_segment_size=50
    )
    with open(pb_path, 'wb') as pf:
        pf.write(trt_graph_def.SerializeToString())


def load_trt_pb(pb_path):
    """Load the TRT graph from the pre-build pb file."""
    trt_graph_def = tf.GraphDef()
    with tf.gfile.GFile(pb_path, 'rb') as pf:
        trt_graph_def.ParseFromString(pf.read())
    # force CPU device placement for NMS ops
    for node in trt_graph_def.node:
        if 'rfcn_' in pb_path and 'SecondStage' in node.name:
            node.device = '/device:GPU:0'
        if 'faster_rcnn_' in pb_path and 'SecondStage' in node.name:
            node.device = '/device:GPU:0'
        if 'NonMaxSuppression' in node.name:
            node.device = '/device:CPU:0'
    with tf.Graph().as_default() as trt_graph:
        tf.import_graph_def(trt_graph_def, name='')
    return trt_graph


def write_graph_tensorboard(sess, log_path):
    """Write graph summary to log_path, so TensorBoard could display it."""
    writer = tf.summary.FileWriter(log_path)
    writer.add_graph(sess.graph)
    writer.flush()
    writer.close()


def _preprocess(src, shape=None, to_rgb=True):
    """Preprocess input image for the TF-TRT object detection model."""
    img = src.astype(np.uint8)
    if shape:
        img = cv2.resize(img, shape)
    if to_rgb:
        # BGR to RGB
        img = img[..., ::-1]
    return img


def _postprocess(img, boxes, scores, classes, conf_th):
    """Postprocess ouput of the TF-TRT object detector."""
    h, w, _ = img.shape
    out_box = boxes[0] * np.array([h, w, h, w])
    out_box = out_box.astype(np.int32)
    out_conf = scores[0]
    out_cls = classes[0].astype(np.int32)

    # only return bboxes with confidence score above threshold
    mask = np.where(out_conf >= conf_th)
    return (out_box[mask], out_conf[mask], out_cls[mask])


def detect(origimg, tf_sess, conf_th, od_type='ssd'):
    """Do object detection over 1 image."""
    global avg_time

    tf_input = tf_sess.graph.get_tensor_by_name('image_tensor:0')
    tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
    tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
    tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
    #tf_num = tf_sess.graph.get_tensor_by_name('num_detections:0')

    if od_type == 'faster_rcnn':
        img = _preprocess(origimg, (1024, 576))
    elif od_type == 'ssd':
        img = _preprocess(origimg, (300, 300))
    else:
        raise ValueError('bad object detector type: $s' % od_type)

    if MEASURE_MODEL_TIME:
        tic = time.time()

    boxes_out, scores_out, classes_out = tf_sess.run(
        [tf_boxes, tf_scores, tf_classes],
        feed_dict={tf_input: img[None, ...]})

    if MEASURE_MODEL_TIME:
        td = (time.time() - tic) * 1000  # in ms
        avg_time = avg_time * 0.9 + td * 0.1
        print('tf_sess.run() took {:.1f} ms on average'.format(avg_time))

    box, conf, cls = _postprocess(
        origimg, boxes_out, scores_out, classes_out, conf_th)

    return (box, conf, cls)
