#!/bin/bash
QuPathApp="INSERT QUPATH DIRECTORY TO APP HERE"
while getopts i:o:p: flag
do
    case "${flag}" in
        i) WSIdir=${OPTARG};;
        o) OPSCCdir=${OPTARG};;
        p) ProjectDir=${OPTARG};;
    esac
done
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\n
░█████╗░██████╗░░██████╗░█████╗░░█████╗░░░░███╗░░██╗███████╗████████╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗░░░████╗░██║██╔════╝╚══██╔══╝
██║░░██║██████╔╝╚█████╗░██║░░╚═╝██║░░╚═╝░░░██╔██╗██║█████╗░░░░░██║░░░
██║░░██║██╔═══╝░░╚═══██╗██║░░██╗██║░░██╗░░░██║╚████║██╔══╝░░░░░██║░░░
╚█████╔╝██║░░░░░██████╔╝╚█████╔╝╚█████╔╝██╗██║░╚███║███████╗░░░██║░░░
░╚════╝░╚═╝░░░░░╚═════╝░░╚════╝░░╚════╝░╚═╝╚═╝░░╚══╝╚══════╝░░░╚═╝░░░\nThe following parameters have been set:"
echo "QuPath APP directory: $QuPathApp";
echo "Directory for virtual whole slide images: $WSIdir";
echo "OPSCCnet directory: $OPSCCdir";
echo "QuPath project directory: $ProjectDir";
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nBuilding QuPath project.\nSTEP 1/9\n<<<<<<<<<<>>>>>>>>>>>"
python "$OPSCCdir/Python_scripts/CreateQuPathProject.py" -i $WSIdir -p $ProjectDir
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nExporting tissue tiles for segmentation.\nSTEP 2/9\n<<<<<<<<<<>>>>>>>>>>>"
$QuPathApp --quiet --log OFF script "$OPSCCdir/QuPathscripts/Export_tiles_annotation_after_tissue_detection_tile_exporter_final.groovy" \
--project "$ProjectDir/project.qpproj" \
--args $OPSCCdir
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nRunning segmentation of viable tumor areas.\nSTEP 3/9\n<<<<<<<<<<>>>>>>>>>>>" 
python "$OPSCCdir/Python_scripts/Segmentation.py"
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nImporting masks into QuPath.\nSTEP 4/9\n<<<<<<<<<<>>>>>>>>>>>" 
$QuPathApp --quiet --log OFF script "$OPSCCdir/QuPathscripts/import_binary_masks.groovy" \
--project "$ProjectDir/project.qpproj"
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nExporting tumor tiles.\nSTEP 5/9\n<<<<<<<<<<>>>>>>>>>>>"
$QuPathApp --quiet --log OFF script "$OPSCCdir/QuPathscripts/Export_tiles_annotation_tile_exporter.groovy" \
--project "$ProjectDir/project.qpproj"
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nStain normalization of tumor tiles.\nSTEP 6/9\n<<<<<<<<<<>>>>>>>>>>>"
python "$OPSCCdir/Python_scripts/StainNormalization.py"
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nClassifying tumor tiles for HPV-association.\nSTEP 7/9\n<<<<<<<<<<>>>>>>>>>>>" 
python "$OPSCCdir/Python_scripts/Classification.py"
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nVisualizing results and saving them into QuPath project.\n<<<<<<<<<<>>>>>>>>>>>\nSTEP 8/9" 
$QuPathApp --quiet --log OFF script "$OPSCCdir/QuPathscripts/Visualize_tiles_directory.groovy" \
--project "$ProjectDir/project.qpproj"
echo -e "\n<<<<<<<<<<>>>>>>>>>>>\nRendering results.\nSTEP 9/9\nRendered results (prediction heatmaps) will be saved to $ProjectDir/rendered\nTabular results can be found at $ProjectDir/OPSCCnet\n<<<<<<<<<<>>>>>>>>>>>" 
$QuPathApp --quiet --log OFF script "$OPSCCdir/QuPathscripts/Export_render_image_no_viewer.groovy" \
--project "$ProjectDir/project.qpproj"


