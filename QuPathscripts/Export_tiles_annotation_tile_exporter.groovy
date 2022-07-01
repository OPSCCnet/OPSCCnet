import qupath.lib.images.servers.LabeledImageServer

def imageData = getCurrentImageData()

// Define output path (relative to project)
def name = GeneralTools.getNameWithoutExtension(imageData.getServer().getMetadata().getName())
def pathOutput = buildFilePath(PROJECT_BASE_DIR, 'tiles_tumor')
mkdirs(pathOutput)

// Define output resolution
//double requestedPixelSize = 0.2465

// Convert to downsample
double downsample = 1 //requestedPixelSize / imageData.getServer().getPixelCalibration().getAveragedPixelSize()


// Create an exporter that requests corresponding tiles from the original & labeled image servers
new TileExporter(imageData)
    .downsample(downsample)     // Define export resolution
    .imageExtension('.jpg')     // Define file extension for original pixels (often .tif, .jpg, '.png' or '.ome.tif')
    .tileSize(224, 224)              // Define size of each tile, in pixels
//    .labeledServer(labelServer) // Define the labeled image server to use (i.e. the one we just built)
    //.annotatedTilesOnly(true)  // If true, only export tiles if there is a (labeled) annotation present
    .annotatedCentroidTilesOnly(true)
    .overlap(0)                // Define overlap, in pixel units at the export resolution
    .writeTiles(pathOutput)     // Write tiles to the specified directory

println('Exporting tumor tiles for the following virtual whole slide image: ' + name)
