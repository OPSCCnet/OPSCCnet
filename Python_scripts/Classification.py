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
def main():
    #set directory of QuPath project
    pwd = Path(__file__).parent
    pwd2 = pwd.parent
    default_dir = open(os.path.join(pwd2, "Project_dir.json"), 'r')
    default_classification = json.load(default_dir)
    default_classification_dir_input = os.path.join(default_classification['path'], "tiles_tumor_normalized")
    default_classification_dir_output = os.path.join(default_classification['path'], "OPSCCnet")
    #args---------------
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=Path, help= 'Please insert directory for files to be processed here. Usually QUPATHPROJECTDIR/tumor_tiles_normalized', default=default_classification_dir_input)
    parser.add_argument('-o', '--outdir', help="outputdir, default ./output/", default=default_classification_dir_output, type=Path)
    args = parser.parse_args()   
    data_dir = args.path
    print(data_dir)
    full_list = pd.DataFrame(os.listdir(data_dir))
    full_list.rename( columns={0:'Filename'}, inplace=True )
    def split_filename1(file_name):
        part1 = str(file_name).split(' [')
        filename_raw = part1[-2]
        return filename_raw
    full_list['Filename_raw'] = full_list['Filename'].apply(lambda x: split_filename1(x))
    #print info on tiles to be processed
    print("Amount of tiles per virtual whole slide image:", full_list.groupby('Filename_raw').size())
    #set directory for model
    pwd = os.path.dirname(__file__)
    model_pwd = os.path.join(pwd,"model")
    model_pwd_weights = os.path.join(model_pwd, "best_model")
    model_pwd_weightszip = os.path.join(model_pwd, "best_model.zip")
    #unzip model if not unzipped
    file_exists_model = exists(os.path.join(model_pwd, "best_model.data-00000-of-00001"))
    if file_exists_model == False:
        with ZipFile(model_pwd_weightszip, "r") as zipObj:
            zipObj.extractall(model_pwd)
    else:
        pass
    #unzip variables if not unzipped
    model_pwd_weights_var = os.path.join(model_pwd, "variables")
    model_pwd_weights_var_zip = os.path.join(model_pwd_weights_var, "variables.zip")
    file_exists_var = exists(os.path.join(model_pwd_weights_var, "variables.data-00000-of-00001"))
    if file_exists_var == False:
        print('Apperently running OPSCC.net for the first time. Unzipping model files.')
        with ZipFile(model_pwd_weights_var_zip, "r") as zipObj:
            zipObj.extractall(model_pwd_weights_var)
    else:
        pass
    #load model
    model = load_model(model_pwd, compile = False)
    model.load_weights(model_pwd_weights)
    #inference params, image from directory
    batch_size = 32
    test_ds = tf.keras.preprocessing.image_dataset_from_directory(
    data_dir,
    color_mode="rgb",
    labels = [0,1],
    label_mode = None,
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
    numberofimages= (len(full_list))
    steps_calc = numberofimages/batch_size
    prediction = model.predict_generator(test_ds,verbose=1,steps=steps_calc, max_queue_size = 32, workers=68)
    #predicted_class = np.argmax(prediction,axis=1)
    OUTPUT_DIR = args.outdir
    os.makedirs(OUTPUT_DIR, exist_ok = True)
    #export
    #prednames = [0,1]
    filenames = test_ds.file_paths
    filenames_raw = list(range(0))
    filenames_supertile = list(range(0))
    for line in filenames:
        Type = line.split(" [")
        Type_supertile = line.split(".jpg")
        x = Type[0]
        y = Type_supertile[0]
        filenames_raw.append(x)
        filenames_supertile.append(y)
    prediction_class0 = np.squeeze(np.delete(prediction, 1, 1))
    prediction_class1 = np.squeeze(np.delete(prediction, 0, 1))
    finaldf = pd.DataFrame({'Filename': filenames,'Filename_raw': filenames_raw,'Filename_supertile':filenames_supertile,'HPV_0': prediction_class0, 'HPV_1': prediction_class1})
    finaldf_aggregate = finaldf.groupby(['Filename_raw'], as_index=False).median()
    finaldf_aggregate_variance = finaldf.groupby(['Filename_raw'], as_index=False).var()
    finaldf_aggregate['HPV1_variance']=finaldf_aggregate_variance[["HPV_1"]]
    finaldf_aggregate_sum = finaldf.groupby(['Filename_raw'], as_index=False).sum()
    tiles_input = finaldf.groupby(['Filename_raw'], as_index=False).size()
    #confidence = finaldf_aggregate_sum.HPV_1.div(tiles_input.size)
    #finaldf_aggregate_pred = finaldf_aggregate[["HPV_0", "HPV_1"]] #array containing classes
    #prediction_case = finaldf_aggregate_pred.to_numpy() #prediction case based
    #prediction_case_class = np.argmax(prediction_case,axis=1)
    #finaldf_aggregate['class_pred'] = prediction_case_class
    finaldf_aggregate['tumor_tiles_used_for_prediction'] = tiles_input['size']
    finaldf_aggregate['tile_class_HPV_positive'] = round(finaldf_aggregate_sum['HPV_1'] / tiles_input['size'] * 100, 2)
    finaldf_aggregate['tile_class_HPV_negative'] = round(finaldf_aggregate_sum['HPV_0'] / tiles_input['size'] * 100, 2)
    finaldf_aggregate['HPV-association-score'] =  round(finaldf_aggregate['tile_class_HPV_positive'] * np.log2((np.reciprocal(finaldf_aggregate['HPV1_variance']))),2)
    finaldf_aggregate['combined_class_without_stage'] = finaldf_aggregate.apply(lambda x: 'high' if x['HPV-association-score'] >= 267.7 else \
                                     ('low' if x['HPV-association-score']<= 107.45 else 'intermediate'), axis=1)
    finaldf_aggregate['combined_class_stageI_stageII_UICC8th'] = finaldf_aggregate.apply(lambda x: 'high' if x['HPV-association-score'] >= 299.85 else \
                                     ('low' if x['HPV-association-score']<= 135.47 else 'intermediate'), axis=1)
    finaldf_aggregate['combined_class_stageIII_stageIV_UICC8th'] = finaldf_aggregate.apply(lambda x: 'high' if x['HPV-association-score'] >= 208.52 else \
                                     ('low' if x['HPV-association-score']<= 100.65 else 'intermediate'), axis=1)
    finaldf_aggregate['HPV_prediction'] = finaldf_aggregate.apply(lambda x: 'HPV-associated' if x['HPV1_variance'] <= 0.08 and x['tile_class_HPV_positive'] >=50  else \
                                     ('No HPV-association' if x['HPV1_variance']<= 0.08 and x['tile_class_HPV_positive'] < 50 else 'uncertain'), axis=1)
    def split_filename2(file_name):
        part1 = str(file_name).split('/')
        filename_raw = part1[-1]
        return filename_raw 
    finaldf_aggregate['Filename_raw'] = finaldf_aggregate['Filename_raw'].apply(lambda x: split_filename2(x))
    filename_output = os.path.join(default_classification_dir_output, datetime.datetime.now().strftime("%Y%m%d-%H%M%S.csv"))
    finaldf_aggregate.drop(finaldf_aggregate.columns[[1,2,3]], axis=1, inplace = True)
    finaldf_aggregate.to_csv(filename_output, sep=";",index=False)
    #visualization part, export dedicated files
    #prepare sheet for visualization
    def split_filename_visual_combine(file_name):
        part1 = str(file_name).split(' [')
        part1 = [item.replace("]", "").replace("x=", "").replace("y=", "").replace("h=", "").replace("w=", "") for item in part1]
        file_name = part1[-1]
        part1 = str(file_name).split(',')
        h = part1[-4]
        w = part1[-3]
        y = part1[-2]
        x = part1[-1]
        return h, w, y, x
    def split_filename_WSI(file_name):
        part1 = str(file_name).split(' [')
        return part1[-2]
    finaldf['Filename_raw'] = finaldf['Filename_supertile'].apply(lambda x: split_filename2(x))
    finaldf['Filename_WSI'] = finaldf['Filename_raw'].apply(lambda x: split_filename_WSI(x))
    finaldf['x'], finaldf['y'], finaldf['w'], finaldf['h'],  = zip(*finaldf['Filename_raw'].apply(lambda x: split_filename_visual_combine(x)))
    df = full_list.groupby('Filename_raw', as_index = False).size()
    for idx, row in df.iterrows():
        finaldf_WSI = finaldf[finaldf['Filename_WSI']==row['Filename_raw']]
        output = pd.DataFrame({'x': finaldf_WSI['x'],'y': finaldf_WSI['y'],'width': finaldf_WSI['w'],'height': finaldf_WSI['h'],'HPV_1': finaldf_WSI['HPV_1'],'HPV_0': finaldf_WSI['HPV_0']})
        filename_output = "%s/%s.csv" % (OUTPUT_DIR, row['Filename_raw'])
        output.to_csv(filename_output, index=False)
if __name__ == '__main__':
    main()
