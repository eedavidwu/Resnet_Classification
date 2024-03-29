import torch
from torch import nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau

from data import Worker
from utils import Trainer
from utils import TrainParams
from network import resnet34, resnet18, resnet50

import os
from os import listdir, getcwd
from os.path import join
import numpy as np

# Hyper-params
wd=getcwd()
data_root = os.path.join(wd, 'data')
model_path = './models/model_34/'
num_workers = 2
init_lr = 0.01
lr_decay = 0.8
momentum = 0.9
weight_decay = 0.000
nesterov = True

# Set Training parameters
#num_classes=9
batch_size=120  #batch_size per GPU, if use GPU mode; resnet34: batch_size=120

params = TrainParams()
params.max_epoch = 200
params.criterion = nn.CrossEntropyLoss()

params.gpus = [0]  

batch_size = batch_size if len(params.gpus) == 0 else batch_size*len(params.gpus)

params.save_dir = model_path
params.ckpt = None
params.save_freq_epoch = 20

# load data
print("Loading dataset...")
train_data = Worker(data_root,train=True)
print('num of train images:', len(train_data.images_path))
#print('num of train labels:', len(train_data.images_labels))
val_data = Worker(data_root,train=False)
print('num of val images:', len(val_data.images_path))
#print('num of val labels:', len(val_data.images_labels))


train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True, num_workers=num_workers)

# batch_size=120, 1GPU Memory < 7000M
#print('train dataset len: {}'.format(len(train_dataloader.dataset)))

val_dataloader = DataLoader(val_data, batch_size=batch_size, shuffle=False, num_workers=num_workers)
#print('val dataset len: {}'.format(len(val_dataloader.dataset)))

# models
#model = resnet18(pretrained=False, modelpath=model_path)  # batch_size=120, 1GPU Memory < 7000M

model = resnet34(pretrained=False, modelpath=model_path)  # batch_size=120, 1GPU Memory < 7000M

#model = resnet50(pretrained=False, modelpath=model_path)  # batch_size=120, 1GPU Memory < 7000M

print(model)

# optimizer
print("Training with sgd")
params.optimizer = torch.optim.SGD(model.parameters(), lr=init_lr,
                                   momentum=momentum,
                                   weight_decay=weight_decay,
                                   nesterov=nesterov)

# Train
params.lr_scheduler = ReduceLROnPlateau(params.optimizer, 'min', factor=lr_decay, patience=10, cooldown=10, verbose=True)
trainer = Trainer(model, params, train_dataloader, val_dataloader)
trainer.train(params)

