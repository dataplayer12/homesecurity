import tensorflow.contrib.tensorrt as trt
from tf_trt_models.detection import build_detection_graph
from tx2_config import MODEL, DATA_DIR, CONFIG_FILE, CHECKPOINT_FILE, SERIAL_FILE
from common.colors import cprint

cprint('Freezing tensorflow graph...','blue')
try:
    frozen_graph, input_names, output_names = build_detection_graph(
        config=CONFIG_FILE,
        checkpoint=CHECKPOINT_FILE,
        score_threshold=0.3,
        batch_size=1
    )
    cprint('Tensorflow graph frozen successfully','green')
except Exception as e:
    cprint('Failed to freeze graph','error')
    cprint(str(e),'error')


cprint('Creating inference graph...','blue')

try:
    trt_graph = trt.create_inference_graph(
        input_graph_def=frozen_graph,
        outputs=output_names,
        max_batch_size=1,
        max_workspace_size_bytes=1 << 25,
        precision_mode='FP16',
        minimum_segment_size=50
    )
    cprint('Inference graph created successfully','green')
except Exception as e:
    cprint('Failed to create inference graph','error')
    cprint(str(e),'error')


cprint('Writing inference graph to file','blue')

with open(SERIAL_FILE, 'wb') as f:
    f.write(trt_graph.SerializeToString())

cprint('Serialized inference graph has been written to {}'.format(SERIAL_FILE),'green')
cprint('Model: {} has been compiled successfully. Please start the launch script to use it.'.format(MODEL),'green')