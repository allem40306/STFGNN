# -*- coding:utf-8 -*-

import time
import json
import argparse

import numpy as np
import mxnet as mx

from utils_4n0_3layer_12T_res import (construct_model, generate_data,
                       masked_mae_np, masked_mape_np, masked_mse_np)

parser = argparse.ArgumentParser()
parser.add_argument("--config", type=str, help='configuration file')
parser.add_argument("--test", action="store_true", help="test program")
args = parser.parse_args()

config_filename = args.config


# load config
with open(config_filename, 'r') as f:
    config = json.loads(f.read())

# print(json.dumps(config, sort_keys=True, indent=4))

net = construct_model(config)

batch_size = config['batch_size']
num_of_vertices = config['num_of_vertices']
num_of_features = config['num_of_features']
predict_features = config['predict_features']
graph_signal_matrix_filename = config['graph_signal_matrix_filename']
if isinstance(config['ctx'], list):
    ctx = [mx.gpu(i) for i in config['ctx']]
elif isinstance(config['ctx'], int):
    ctx = mx.gpu(config['ctx'])

#  load data
loaders = []
true_values = []
for idx, (x, y) in enumerate(generate_data(graph_signal_matrix_filename, num_of_features=num_of_features)):
    if args.test:
        x = x[: 100]
        y = y[: 100]
    y = y[:, :, :, 0:predict_features]
    # y = y.squeeze(axis=-1)
    print(x.shape, y.shape)
    loaders.append(
        mx.io.NDArrayIter(
            x, y if idx == 0 else None,
            batch_size=batch_size,
            shuffle=(idx == 0),
            label_name='label'
        )
    )
    if idx == 0:
        training_samples = x.shape[0]
    else:
        true_values.append(y)

train_loader, val_loader, test_loader = loaders
val_y, test_y = true_values

# load model
epochs = 200
if args.test:
    epochs = 5

print(f'STFGNN_{config_filename.replace("/","_")}')
sym, arg_params, aux_params = mx.model.load_checkpoint(f'STFGNN_{config_filename.replace("/","_")}', epochs)

mod = mx.mod.Module(
    sym,
    data_names=['data'],
    label_names=['label'],
    context=ctx
)

mod.bind(
    data_shapes=[(
        'data',
        (batch_size, config['points_per_hour'], num_of_vertices, num_of_features)
    ), ],
    label_shapes=[(
        'label',
        (batch_size, config['points_per_hour'], num_of_vertices, predict_features)
    )]
)

mod.set_params(arg_params, aux_params)

# test
test_loader.reset()
prediction = mod.predict(test_loader)[1].asnumpy()
np.savez_compressed(f"{config_filename.split('/')[1]}_result.npz", test = test_y, prediction = prediction)
filename = f"{config_filename.split('/')[1]}.csv"
outfile = open(filename, "w")
outfile.write("MAE,MAPE,RMSE\n")
tmp_info = []
for idx in range(config['num_for_predict']):
    y, x = test_y[:, : idx + 1, :], prediction[:, : idx + 1, :]
    tmp_info.append((
        masked_mae_np(y, x, 0),
        masked_mape_np(y, x, 0),
        masked_mse_np(y, x, 0) ** 0.5
    ))
    outfile.write(f"{masked_mae_np(y, x, 0)},{masked_mape_np(y, x, 0)},{masked_mse_np(y, x, 0) ** 0.5}\n")
