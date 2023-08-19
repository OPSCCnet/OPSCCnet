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

# Setzen des Projektverzeichnisses
pwd = Path(__file__).parent
pwd2 = pwd.parent
default_dir = open(os.path.join(pwd2, "Project_dir.json"), 'r')
default_segmentation = json.load(default_dir)
default_segmentation_dir_input = os.path.join(default_segmentation['path'], "tiles")
default_segmentation_dir_output = os.path.join(default_segmentation['path'], "tiles_segmented")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Script zur Bildsegmentierung mit einem vortrainierten Modell.")
    
    parser.add_argument('-p', '--path', type=Path, 
                        help='Verzeichnis für zu verarbeitende Bilder zur Segmentierung. Standardmäßig /tiles', 
                        default=default_segmentation_dir_input)
    
    parser.add_argument('-o', '--outdir', type=Path,
                        help='Ausgabeverzeichnis. Standardmäßig ./output_segmentation/', 
                        default=default_segmentation_dir_output)
    
    return parser.parse_args()

args = parse_arguments()
data_dir = args.path

def initialize_model():
    model_pwd = os.path.join(pwd, "model")
    model_pwd_weights = os.path.join(model_pwd, "OPSCCnet_FPN_ResNet18.pth")
    
    model = InfModel("FPN", "resnet18", encoder_weights="imagenet", in_channels=3, out_classes=1)
    model.load_state_dict(torch.load(model_pwd_weights))
    model.eval()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    threads = torch.get_num_threads()
    
    if device == "cpu":
        # Nutzen Sie die verfügbaren CPU-Kerne effizient, anstatt den Wert zu verhärten.
        torch.set_num_threads(max(1, int(threads * 0.6)))
    # Falls in der Zukunft eine besondere GPU-Verarbeitung benötigt wird, kann sie hier hinzugefügt werden.

    # Wrap the model using nn.DataParallel for efficient GPU utilization
    model = torch.nn.DataParallel(model)
    model.to(device)
    
    return model, device

model, device = initialize_model()

def prepare_data(data_dir):
    input_files_path = data_dir
    input_files = glob.glob(os.path.join(input_files_path, '*.jpg'))
    files = input_files
    
    # Anzahl der Bilder anzeigen
    print(f"Segmenting a total of {len(files)} images.")
    
    batch_size = 10
    sub_lists = [
        files[i: i + batch_size]
        for i in range(0, len(files), batch_size)
    ]
    
    return sub_lists

data_batches = prepare_data(data_dir)


def process_function(batch, model, device, OUTPUT_DIR):
    for item in batch:
        fname = item
        newfname = f"{OUTPUT_DIR}/{os.path.basename(fname)[:-4]}_class.png"
        
        img = Image.open(fname).convert("RGB")
        io = np.array(img)
        io = np.moveaxis(io, -1, 0)
        io = torch.from_numpy(io)
        
        logits = model(io.to(device)).cpu().numpy()
        pr_mask = sigmoid(logits)
        pr_mask = pr_mask.astype(np.float32)
        pr_mask = pr_mask.squeeze().astype(np.uint8) * 255
        
        min_val, max_val, _, _ = cv2.minMaxLoc(pr_mask)
        if max_val > 0.0:
            cv2.imwrite(newfname, pr_mask)


OUTPUT_DIR = args.outdir
os.makedirs(OUTPUT_DIR, exist_ok=True)

with torch.no_grad():
    for batch in tqdm(data_batches):
        process_function(batch, model, device, OUTPUT_DIR)


