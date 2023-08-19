#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 19:23:28 2022

@author: sebastian
"""
# Importieren der erforderlichen Bibliotheken und Module
from __future__ import division
import argparse
import os, sys
import json
#import torchvision.transforms.functional as fn  # Wird nicht verwendet, daher kommentiert
from pathlib import Path
import cv2
import glob
import staintools
from staintools import ReinhardColorNormalizer
from multiprocessing.dummy import Pool
import multiprocessing

# Festlegen der globalen Einstellungen und Standardverzeichnisse

# Anzahl der zu verwendenden CPU-Kerne (40% der verfügbaren Kerne)
CPU_to_use = round(multiprocessing.cpu_count() * 0.4)

# Bestimmen des aktuellen Verzeichnisses und des übergeordneten Verzeichnisses
pwd = Path(__file__).parent
pwd2 = pwd.parent

# Laden des Standardverzeichnisses aus der JSON-Datei
with open(os.path.join(pwd2, "Project_dir.json"), 'r') as default_dir_file:
    default_stainnormdir = json.load(default_dir_file)

# Festlegen der Standardverzeichnisse für Ein- und Ausgabe
input_folder = os.path.join(default_stainnormdir['path'], "tiles_tumor")
output_folder = os.path.join(default_stainnormdir['path'], "tiles_tumor_normalized")

# Argumentparser-Definition, um Befehlszeilenargumente für das Skript zu ermöglichen
parser = argparse.ArgumentParser(description='Skript zur Farbnormalisierung von Bildern mit staintools.')

# Pfad des Eingabeverzeichnisses
parser.add_argument('-p', '--path', type=Path, 
                    help='Bitte Verzeichnispfad für die zu verarbeitenden Bilder zur Farbnormalisierung eingeben. Standardmäßig /tiles',
                    default=input_folder)

# Pfad des Ausgabeverzeichnisses
parser.add_argument('-o', '--outdir', 
                    help='Ausgabeverzeichnis. Standardmäßig ./output_segmentation/', 
                    default=output_folder, type=Path)

args = parser.parse_args()

# Pfade für Datenverzeichnis und Ausgabeverzeichnis aus den Argumenten extrahieren
data_dir = args.path
OUTPUT_DIR = args.outdir

# Ausgabeverzeichnis erstellen, falls es nicht existiert
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Laden aller JPG-Dateien im Eingabeverzeichnis
input_files = glob.glob(os.path.join(input_folder, '*.jpg'))

# Liste der zu verarbeitenden Dateien (könnte in Zukunft angepasst oder erweitert werden)
files = input_files
print(f"Applying stain normalization to a total of {len(input_files)} images.")

# Laden des Referenzbildes für die Farbnormalisierung
target = cv2.imread(os.path.join(pwd, 'misc', 'reference.jpg'))
#target = staintools.LuminosityStandardizer.standardize(target) #optional

# Initialisieren des ReinhardColorNormalizer für die Farbnormalisierung
n = ReinhardColorNormalizer()
n.fit(target)

def transform_multi(image_name, output_path):
    """
    Funktion zur Durchführung der Farbnormalisierung auf einem Bild.
    
    Parameter:
    - image_name: Pfad des Eingabebildes.
    - output_path: Verzeichnis, in dem das normalisierte Bild gespeichert werden soll.
    
    Rückgabewert:
    - None
    """
    # Bild laden
    source = cv2.imread(image_name)
    
    # Luminositätsstandardisierung (optional)
    source = staintools.LuminosityStandardizer.standardize(source)
    
    # Farbnormalisierung
    transformed = n.transform(source)
    
    # Speichern des normalisierten Bildes
    newfname_class = "%s/%s.jpg" % (output_folder, os.path.basename(image_name)[0:-4])
    cv2.imwrite(newfname_class, transformed)

def convert(file):
    """
    Funktion zur Verarbeitung eines Bildes.
    
    Parameter:
    - file: Dateipfad des zu verarbeitenden Bildes.
    
    Rückgabewert:
    - None
    """
    process_file = files.pop()
    transform_multi(process_file, output_folder)

if __name__ == '__main__':
    # Verwenden von Multiprocessing, um die Bildverarbeitung zu beschleunigen
    pool = Pool(processes=CPU_to_use)
    pool.map(convert, files)
