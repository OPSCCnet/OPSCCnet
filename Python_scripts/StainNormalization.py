#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 19:23:28 2022

@author: sebastian
"""
from __future__ import division
import argparse
import os,sys
import json
#import torchvision.transforms.functional as fn
from pathlib import Path
import cv2
import glob

import staintools
from staintools import ReinhardColorNormalizer
from multiprocessing.dummy import Pool
import multiprocessing
import cv2 as cv
from os import listdir
from os.path import join, isfile
#set directory of QuPath project
CPU_to_use = round(multiprocessing.cpu_count()*0.4) 
pwd = Path(__file__).parent
pwd2 = pwd.parent
default_dir = open(os.path.join(pwd2, "Project_dir.json"), 'r')
default_stainnormdir = json.load(default_dir)
input_folder = os.path.join(default_stainnormdir['path'], "tiles_tumor")
output_folder = os.path.join(default_stainnormdir['path'], "tiles_tumor_normalized")
#args---------------
parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', type=Path, help= 'Please insert directory for files to be processed for stain normalization here. Usually /tiles', default=input_folder)
parser.add_argument('-o', '--outdir', help="outputdir, default ./output_segmentation/", default=output_folder, type=Path)
args = parser.parse_args()   
data_dir = args.path
OUTPUT_DIR = args.outdir
os.makedirs(OUTPUT_DIR, exist_ok = True)
#
input_files = glob.glob(os.path.join(input_folder, '*.jpg'))
files = []
files = input_files
target = cv.imread(os.path.join(pwd, 'misc', 'reference.jpg'))
#print(os.path.join(root, 'Python_scripts', 'misc', '00-19108_12_5-A_HE---2019-12-18-15.58.07_HPV_positive_x92143_y17192_w1000_h1000.jpg'))
#target = staintools.LuminosityStandardizer.standardize(target) #optional

n=ReinhardColorNormalizer()
n.fit(target)
def transform_multi(image_name, output_path):         

    source = cv.imread(image_name)
    source = staintools.LuminosityStandardizer.standardize(source) #optional
    transformed = n.transform(source)
    newfname_class = "%s/%s.jpg" % (output_folder, os.path.basename(image_name)[0:-4])
    cv.imwrite(newfname_class, transformed)

image_names = [f for f in listdir(input_folder) if isfile(join(input_folder, f))]
if '.DS_Store' in image_names:
    image_names.remove('.DS_Store')
def convert(file):
    process_file = files.pop()
    print(transform_multi(process_file, output_folder))
def blockPrint():
    sys.stdout = open(os.devnull, 'w')
blockPrint()
if __name__ == '__main__':
    #pool = ThreadPool(multiprocessing.cpu_count()-64) slow, crashes
    pool = Pool(processes=CPU_to_use)
    pool.map(convert,files) 
