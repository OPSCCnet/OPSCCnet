#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 10 20:49:40 2022

@author: sebastian
"""

import argparse
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import  load_model
import pandas as pd
import datetime
import json
from pathlib import Path
from os.path import exists
from zipfile import ZipFile
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  #represss tf messages
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

def get_default_paths():
    """
    Ermittelt die Standardverzeichnisse für den Input und den Output.
    """
    pwd = Path(__file__).parent
    pwd2 = pwd.parent
    with open(os.path.join(pwd2, "Project_dir.json"), 'r') as default_dir_file:
        default_classification = json.load(default_dir_file)
    
    default_input = os.path.join(default_classification['path'], "tiles_tumor_normalized")
    default_output = os.path.join(default_classification['path'], "OPSCCnet")
    
    return default_input, default_output

def parse_arguments(default_input, default_output):
    """
    Parst die übergebenen Argumente oder setzt Standardwerte.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=Path, 
                        help='Insert directory for files to be processed. Usually QUPATHPROJECTDIR/tumor_tiles_normalized', 
                        default=default_input)
    parser.add_argument('-o', '--outdir', help="Output dir, default is ./output/", 
                        default=default_output, type=Path)
    
    return parser.parse_args()

def list_files_in_directory(data_dir):
    """
    Listen Sie Dateien in einem Verzeichnis auf und verarbeiten Sie sie für die Vorhersage.
    """
    full_list = pd.DataFrame(os.listdir(data_dir))
    full_list.rename(columns={0: 'Filename'}, inplace=True)
    full_list['Filename_raw'] = full_list['Filename'].apply(lambda x: str(x).split(' [')[-2])
    return full_list

def setup_model():
    """
    Setzt das Modell und die notwendigen Dateien auf.
    """
    pwd = os.path.dirname(__file__)
    model_pwd = os.path.join(pwd, "model")
    
    # Überprüfen und Extrahieren des Hauptmodells
    model_zip_path = os.path.join(model_pwd, "best_model.zip")
    if not exists(os.path.join(model_pwd, "best_model.data-00000-of-00001")):
        with ZipFile(model_zip_path, "r") as zipObj:
            zipObj.extractall(model_pwd)
            
    # Überprüfen und Extrahieren der Variablen
    model_vars_path = os.path.join(model_pwd, "variables")
    if not exists(os.path.join(model_vars_path, "variables.data-00000-of-00001")):
        with ZipFile(os.path.join(model_vars_path, "variables.zip"), "r") as zipObj:
            zipObj.extractall(model_vars_path)
            
    model = load_model(model_pwd, compile=False)
    model.load_weights(os.path.join(model_pwd, "best_model"))
    
    return model

def make_predictions(model, data_dir):
    """
    Führen Sie Vorhersagen mit dem gegebenen Modell aus.
    """
    batch_size = 32
    test_ds = tf.keras.preprocessing.image_dataset_from_directory(
        data_dir,
        color_mode="rgb",
        labels=[0, 1],  # Möglicherweise nicht notwendig, da label_mode=None gesetzt ist.
        label_mode=None,
        batch_size=batch_size,
        image_size=(224, 224),
        shuffle=False,
        seed=None,
        validation_split=None,
        subset=None,
        interpolation="bilinear",
        follow_links=True,
        crop_to_aspect_ratio=False,
    )
    
    all_predictions = []

    for images in test_ds:
        batch_predictions = model.predict(images, verbose=0, max_queue_size=32, workers=68)
        all_predictions.extend(batch_predictions)

    all_file_paths = test_ds.file_paths

    return np.array(all_predictions), all_file_paths

def create_dataframe(filenames, filenames_raw, filenames_supertile, prediction_class0, prediction_class1):
    finaldf = pd.DataFrame({
        'Filename': filenames,
        'Filename_raw': filenames_raw,
        'Filename_supertile': filenames_supertile,
        'HPV_0': prediction_class0, 
        'HPV_1': prediction_class1
    })

    return finaldf

def analyze_and_save_predictions(all_predictions, all_file_paths, full_list, outdir, default_input, default_classification_dir_output, OUTPUT_DIR):
    # Analyse der Vorhersagen
    filenames, filenames_raw, filenames_supertile = extract_file_names(all_file_paths)
    prediction_class0, prediction_class1 = split_predictions(all_predictions)

    finaldf = create_dataframe(filenames, filenames_raw, filenames_supertile, prediction_class0, prediction_class1)
    finaldf_aggregate = aggregate_dataframe(finaldf)
    default_input, default_classification_dir_output = get_default_paths()

    # Daten speichern
    save_aggregated_data(finaldf_aggregate, default_classification_dir_output)
    save_for_visualization(finaldf, full_list, OUTPUT_DIR)

def extract_file_names(filenames):
    filenames_raw = []
    filenames_supertile = []
    for line in filenames:
        Type = line.split(" [")
        Type_supertile = line.split(".jpg")
        x = Type[0]
        y = Type_supertile[0]
        filenames_raw.append(x)
        filenames_supertile.append(y)
    return filenames, filenames_raw, filenames_supertile

def split_predictions(predictions):
    prediction_class0 = predictions[:, 0]
    prediction_class1 = predictions[:, 1]
    return prediction_class0, prediction_class1

def aggregate_dataframe(finaldf):
    finaldf_aggregate = finaldf.groupby(['Filename_raw'], as_index=False).median()
    finaldf_aggregate_variance = finaldf.groupby(['Filename_raw'], as_index=False).var()
    finaldf_aggregate['HPV1_variance'] = finaldf_aggregate_variance[["HPV_1"]]
    finaldf_aggregate_sum = finaldf.groupby(['Filename_raw'], as_index=False).sum()
    tiles_input = finaldf.groupby(['Filename_raw'], as_index=False).size()
    
    finaldf_aggregate['tumor_tiles_used_for_prediction'] = tiles_input['size']
    finaldf_aggregate['tile_class_HPV_positive'] = round(finaldf_aggregate_sum['HPV_1'] / tiles_input['size'] * 100, 2)
    finaldf_aggregate['tile_class_HPV_negative'] = round(finaldf_aggregate_sum['HPV_0'] / tiles_input['size'] * 100, 2)
    finaldf_aggregate['HPV-association-score'] = round(finaldf_aggregate['tile_class_HPV_positive'] * np.log2((np.reciprocal(finaldf_aggregate['HPV1_variance']))),2)
    
    # Here we classify the scores into three categories: high, low, and intermediate based on thresholds
    classify_scores(finaldf_aggregate)
    
    return finaldf_aggregate

def classify_scores(finaldf_aggregate):
    finaldf_aggregate['combined_class_without_stage'] = finaldf_aggregate.apply(lambda x: 'high' if x['HPV-association-score'] >= 267.7 else ('low' if x['HPV-association-score']<= 107.45 else 'intermediate'), axis=1)
    finaldf_aggregate['combined_class_stageI_stageII_UICC8th'] = finaldf_aggregate.apply(lambda x: 'high' if x['HPV-association-score'] >= 299.85 else ('low' if x['HPV-association-score']<= 135.47 else 'intermediate'), axis=1)
    finaldf_aggregate['combined_class_stageIII_stageIV_UICC8th'] = finaldf_aggregate.apply(lambda x: 'high' if x['HPV-association-score'] >= 208.52 else ('low' if x['HPV-association-score']<= 100.65 else 'intermediate'), axis=1)
    finaldf_aggregate['HPV_prediction'] = finaldf_aggregate.apply(lambda x: 'HPV-associated' if x['HPV1_variance'] <= 0.08 and x['tile_class_HPV_positive'] >=50  else ('No HPV-association' if x['HPV1_variance']<= 0.08 and x['tile_class_HPV_positive'] < 50 else 'uncertain'), axis=1)

def split_filename2(file_name):
    part1 = str(file_name).split('/')
    filename_raw = part1[-1]
    return filename_raw

def save_aggregated_data(finaldf_aggregate, default_classification_dir_output):
    finaldf_aggregate['Filename_raw'] = finaldf_aggregate['Filename_raw'].apply(lambda x: split_filename2(x))
    filename_output = os.path.join(default_classification_dir_output, datetime.datetime.now().strftime("%Y%m%d-%H%M%S.csv"))
    finaldf_aggregate.drop(finaldf_aggregate.columns[[1,2,3]], axis=1, inplace=True)
    finaldf_aggregate.to_csv(filename_output, sep=";", index=False)

def save_for_visualization(finaldf, full_list, OUTPUT_DIR):

    def split_filename_visual_combine(file_name):
        parts = str(file_name).split(' [')
        cleaned_string = parts[-1].replace("]", "").replace("x=", "").replace("y=", "").replace("h=", "").replace("w=", "")
        cleaned_parts = cleaned_string.split(',')
        h = cleaned_parts[-4]
        w = cleaned_parts[-3]
        y = cleaned_parts[-2]
        x = cleaned_parts[-1]
        return h, w, y, x

    def split_filename_WSI(file_name):
        parts = str(file_name).split(' [')
        return parts[-2]

    # Anwendung der Hilfsfunktionen auf das DataFrame

    finaldf['Filename_raw'] = finaldf['Filename_supertile'].apply(lambda x: split_filename2(x))
    finaldf['Filename_WSI'] = finaldf['Filename_raw'].apply(lambda x: split_filename_WSI(x))
    finaldf['x'], finaldf['y'], finaldf['w'], finaldf['h'], = zip(*finaldf['Filename_raw'].apply(lambda x: split_filename_visual_combine(x)))
    
    df = full_list.groupby('Filename_raw', as_index=False).size()
    for idx, row in df.iterrows():
        finaldf_WSI = finaldf[finaldf['Filename_WSI'] == row['Filename_raw']]
        output = pd.DataFrame({
            'x': finaldf_WSI['x'],
            'y': finaldf_WSI['y'],
            'width': finaldf_WSI['w'],
            'height': finaldf_WSI['h'],
            'HPV_1': finaldf_WSI['HPV_1'],
            'HPV_0': finaldf_WSI['HPV_0']
        })
        filename_output = f"{OUTPUT_DIR}/{row['Filename_raw']}.csv"
        output.to_csv(filename_output, index=False)



def main():
    # Pfadinformationen holen und Argumente parsen
    default_input, default_classification_dir_output = get_default_paths()
    args = parse_arguments(default_input, default_classification_dir_output)
    OUTPUT_DIR = args.outdir
    os.makedirs(OUTPUT_DIR, exist_ok = True)
    # Datenverzeichnis auflisten
    full_list = list_files_in_directory(args.path)
    grouped_data = full_list.groupby('Filename_raw').size()
    output_message = ", ".join([f"{key}: {value} tiles" for key, value in grouped_data.items()])
    print(f"Amount of tiles per virtual whole slide image: {output_message}")
    
    # Modell initialisieren
    model = setup_model()
    
    # Vorhersagen treffen
    predictions, all_file_paths = make_predictions(model, args.path)

    
    # Vorhersagen analysieren und Daten speichern
    analyze_and_save_predictions(predictions, all_file_paths, full_list,args.outdir, default_input, default_classification_dir_output, OUTPUT_DIR)



# Hauptfunktionsaufruf
if __name__ == '__main__':
    main()

