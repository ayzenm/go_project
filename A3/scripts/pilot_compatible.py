"""Same dense-only pilot invoked in Colab, after prepare_compatible.py."""
import os
import random
import time
os.environ['TF_NUM_INTRAOP_THREADS'] = '2'
os.environ['TF_NUM_INTEROP_THREADS'] = '2'
import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
random.seed(0)
np.random.seed(0)
tf.set_random_seed(0)
from tensorflow.keras.datasets import mnist
from lottery_ticket.foundations import save_restore
from lottery_ticket.mnist_fc import lottery_experiment

if __name__ == '__main__':
    (x, y), (xt, yt) = mnist.load_data()
    save_restore.save_network('/content/A3_compat/data/mnist',
                              dict(x_train=x, y_train=y, x_test=xt, y_test=yt))
    print('Devices', tf.config.list_physical_devices('GPU'), flush=True)
    tick = time.perf_counter()
    lottery_experiment.train(output_dir='/content/A3_compat/pilot_output',
        mnist_location='/content/A3_compat/data/mnist', iterations=0, train_order_seed=0)
    print('TRAINING_SECONDS', time.perf_counter()-tick, flush=True)
