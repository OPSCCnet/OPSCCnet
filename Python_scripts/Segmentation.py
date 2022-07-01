#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 20:49:40 2022

@author: sebastian
"""

import argparse
import os
import numpy as np
import torch
import json
#import torchvision.transforms.functional as fn
from pathlib import Path
from sm_import import InfModel
from scipy.special import expit as sigmoid
import cv2
import glob
from PIL import Image
from tqdm import tqdm

#set directory of QuPath project
pwd = Path(__file__).parent
pwd2 = pwd.parent
default_dir = open(os.path.join(pwd2, "Project_dir.json"), 'r')
default_segmentation = json.load(default_dir)
default_segmentation_dir_input = os.path.join(default_segmentation['path'], "tiles")
default_segmentation_dir_output = os.path.join(default_segmentation['path'], "tiles_segmented")
#args---------------
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=Path, help= 'Please insert directory for files to be processed for segmentation here. Usually /tiles', default=default_segmentation_dir_input)
parser.add_argument('-o', '--outdir', help="outputdir, default ./output_segmentation/", default=default_segmentation_dir_output, type=Path)
args = parser.parse_args()   
data_dir = args.path
#GPU--START
model_pwd = os.path.join(pwd,"model")
model_pwd_weights = os.path.join(model_pwd, "OPSCCnet_FPN_ResNet18.pth")
model = InfModel("FPN", "resnet18",encoder_weights="imagenet", in_channels=3, out_classes=1)
model.load_state_dict(torch.load(model_pwd_weights))
model.eval()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
threads = torch.get_num_threads()
if device =="cpu":
    #torch.set_num_threads(round(threads*0.6))
    torch.set_num_threads(8)
else:
    pass

model.to(device) #added
#GPU--END

#set dirs
OUTPUT_DIR = args.outdir
os.makedirs(OUTPUT_DIR, exist_ok = True)
input_files_path = args.path
input_files = glob.glob(os.path.join(input_files_path, '*.jpg'))
files = []
files = input_files
#batch
long_list = files
batch_size = 10
sub_list_length = batch_size
sub_lists = [
    long_list[i : i + sub_list_length]
    for i in range(0, len(long_list), sub_list_length)
]
#batch end
#process file func
def process_function(list):
    for item in list:
        fname = item
        newfname = "%s/%s_class.png" % (OUTPUT_DIR, os.path.basename(fname)[0:-4])
        img = Image.open(fname).convert("RGB")
        #img = fn.resize(img, size=[1024,1024])
        io = np.array(img) 
        io = np.moveaxis(io, -1, 0)
        io = torch.from_numpy(io)
        logits = model(io.to(device)).cpu().numpy()
        pr_mask = sigmoid(logits)
        pr_mask = np.asarray(pr_mask)
        pr_mask = pr_mask.astype(np.float32)
        pr_mask = pr_mask.squeeze().astype(np.uint8)*255
        #pr_mask = np.array(Image.fromarray(pr_mask).resize((4096, 4096), Image.NEAREST))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(pr_mask)
        if max_val > 0.0:
            cv2.imwrite(newfname,pr_mask)
        else:
            pass

with torch.no_grad():
    for sub_list in tqdm(sub_lists):
        partial_result = process_function(sub_list)


