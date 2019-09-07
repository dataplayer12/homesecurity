"""test_visualization.py
"""


import numpy as np
import cv2
from visualization import BBoxVisualization


def main():
    """main
    """
    cls_dict = {0: 'cat', 1: 'dog', 2: 'person'}
    num_classes = 3
    boxes = np.array(
        [[100, 100, 300, 200],
         [100, 400, 300, 500],
         [200, 250, 400, 300]],
        dtype=np.int32
    )
    confs = np.array([0.5, 0.7, 0.9], dtype=np.float32)
    clss = np.array([0, 1, 2], dtype=np.int32)

    img = cv2.imread('../examples/detection/data/huskies.jpg')
    assert img is not None
    vis = BBoxVisualization(cls_dict, num_classes)
    img = vis.draw_bboxes(img, boxes, confs, clss)
    cv2.imshow('Test BBoxVisualization', img)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()
