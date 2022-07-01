def path_OPSCCnet = args[0]
boolean prettyPrint = true
def gson = GsonTools.getInstance(prettyPrint)
def path_project = buildFilePath(PROJECT_BASE_DIR)


def path = path_project + "/OPSCC_dir.json"
def file = new File(path)
file.write(gson.toJson(path_OPSCCnet))

//println("Done! OPSCC.net directory is set to: " + path_OPSCCnet)

def path_opscc_folder = path_OPSCCnet + "/Project_dir.json"
def file_project = new File(path_opscc_folder)
file_project.write(gson.toJson(['path': path_project]))
//println("Done! Current project file is set to: " + path_project)
createAnnotationsFromPixelClassifier(path_OPSCCnet.toString() + "/QuPathscripts/misc/tissue_background.json", 0.0, 0.0) 

//def path_OPSCCnet = Dialogs.getChooser(null).promptForDirectory("Please select the main directory of OPSCC.net that includes relevant scripts.")
//def selectedDir = Dialogs.promptForDirectory("Please select the main directory of OPSCC.net that includes relevant scripts.")

import qupath.lib.images.servers.LabeledImageServer

def imageData = getCurrentImageData()

// Define output path (relative to project)
def name = GeneralTools.getNameWithoutExtension(imageData.getServer().getMetadata().getName())
def pathOutput = buildFilePath(PROJECT_BASE_DIR, 'tiles')
mkdirs(pathOutput)

double requestedPixelSize = 2.2

// Convert output resolution to a downsample factor
double pixelSize = imageData.getServer().getPixelCalibration().getAveragedPixelSize()
double downsample = requestedPixelSize / pixelSize


// Create an exporter that requests corresponding tiles from the original & labeled image servers
new TileExporter(imageData)
    .downsample(downsample)     // Define export resolution
    .imageExtension('.jpg')     // Define file extension for original pixels (often .tif, .jpg, '.png' or '.ome.tif')
    .tileSize(1024, 1024)              // Define size of each tile, in pixels
//    .labeledServer(labelServer) // Define the labeled image server to use (i.e. the one we just built)
    .annotatedTilesOnly(true)  // If true, only export tiles if there is a (labeled) annotation present
    //.annotatedCentroidTilesOnly(true)
    .overlap(256)                // Define overlap, in pixel units at the export resolution
    .writeTiles(pathOutput)     // Write tiles to the specified directory

//println('Done! Removing tissue masks')
println('Exporting image tiles for the following virtual whole slide image: ' + name)
selectAnnotations()
clearSelectedObjects(true);
getProjectEntry().saveImageData(getCurrentImageData())
