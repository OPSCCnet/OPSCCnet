#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:25:58 2022

@author: sebastian
"""
import os
import argparse
from pathlib import Path
import glob
import pprint
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--ipath', type=Path, help= 'Please insert directory for files to be included in the QuPath project.')
parser.add_argument('-p', '--projdir', help="Please insert the project directory.",type=Path)
args = parser.parse_args()   
project_dir = args.projdir
os.makedirs(project_dir, exist_ok = True)
images = input_files_path = args.ipath
images = glob.glob(os.path.join(input_files_path, '*'))
print("Found ", len(images), "files in the image directory. Did not check which type of files, all file-types included!")
pprint.pprint(images)
def prepare_example_resources():
    """build an example project"""
    from paquo.projects import QuPathProject
    from paquo.images import QuPathImageType
    with QuPathProject(project_dir, mode="x") as qp:
        for img_fn in images:
            qp.add_image(img_fn, image_type=QuPathImageType.BRIGHTFIELD_H_E)

if __name__ == "__main__":
    try:
        prepare_example_resources()
    except FileExistsError:
        print("")
        print("There is already a project file within this directory. Working with the already existing project data!")
        
