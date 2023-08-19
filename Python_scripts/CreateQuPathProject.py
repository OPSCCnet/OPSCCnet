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
def parse_arguments():
    parser = argparse.ArgumentParser(description="Tool zum Erstellen eines QuPath-Projekts und Hinzufügen von Bildern.")
    parser.add_argument('-i', '--ipath', required=True, type=Path, 
                        help='Bitte Verzeichnispfad für die in das QuPath-Projekt einzufügenden Bilder eingeben.')
    parser.add_argument('-p', '--projdir', required=True, type=Path,
                        help="Bitte das Verzeichnis des Projekts eingeben.")
    return parser.parse_args()

def get_filtered_image_list(input_files_path):
    # Supported image formats as per https://bio-formats.readthedocs.io/en/stable/supported-formats.html
    supported_formats = ['.ndpi', '.ndpis', '.svs', '.afi', '.vsi', '.dcm', '.dicom', '.jp2' ,'.j2k', '.jpf', '.tif', '.tiff', '.ome.tiff', '.ome.tif', '.ome.tf2', '.ome.tf8', '.ome.btf', '.bif', '.czi']
    problematic_formats = ['.scn']
    
    # Retrieve all files and filter by supported formats
    all_files = glob.glob(os.path.join(input_files_path, '*'))
    images = [file for file in all_files if file.lower().endswith(tuple(supported_formats))]
    
    # Check for problematic formats and issue a warning
    problematic_files = [file for file in all_files if file.lower().endswith(tuple(problematic_formats))]
    if problematic_files:
        print(f"WARNING: Found {len(problematic_files)} files with problematic formats (e.g., .scn). It's recommended to first create a QuPath project using Openslide, as Bioformats might have issues with these file types.")
    
    return images

def prepare_example_resources(project_dir, images):
    from paquo.projects import QuPathProject
    from paquo.images import QuPathImageType

    with QuPathProject(project_dir, mode="x") as qp:
        for img_fn in images:
            qp.add_image(img_fn, image_type=QuPathImageType.BRIGHTFIELD_H_E)


if __name__ == "__main__":
    args = parse_arguments()
    
    # Projektverzeichnis erstellen (falls nicht vorhanden)
    os.makedirs(args.projdir, exist_ok=True)
    
    images = get_filtered_image_list(args.ipath)
    
    print(f"Found {len(images)} supported image files in the directory.")
    pprint.pprint(images)
    
    try:
        prepare_example_resources(args.projdir, images)
    except FileExistsError:
        print("\nEs gibt bereits eine Projektdatei in diesem Verzeichnis. Mit den bereits vorhandenen Projektdaten wird gearbeitet!")
        
