import tensorflow.contrib.tensorrt as trt
from tf_trt_models.detection import build_detection_graph
from jetson_config import MODEL, DATA_DIR, CONFIG_FILE, CHECKPOINT_FILE, SERIAL_FILE

print('Freezing tensorflow graph...')

frozen_graph, input_names, output_names = build_detection_graph(
    config=CONFIG_FILE,
    checkpoint=CHECKPOINT_FILE,
    score_threshold=0.3,
    batch_size=1
)

print('Tensorflow graph frozen successfully')

print('Creating inference graph...')
trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)

print('Inference graph created successfully')

print('Writing inference graph to file')

with open(SERIAL_FILE, 'wb') as f:
    f.write(trt_graph.SerializeToString())

print('Serialized inference graph has been written to {}'.format(SERIAL_FILE))
print('Please start launch script to use compiled graph')