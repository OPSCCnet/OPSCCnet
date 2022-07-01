import qupath.lib.gui.viewer.overlays.HierarchyOverlay
import qupath.lib.gui.viewer.OverlayOptions
import qupath.lib.gui.images.servers.RenderedImageServer
import qupath.lib.gui.scripting.QPEx
import qupath.lib.color.ColorMaps
import qupath.lib.gui.tools.MeasurementMapper
def colorMapper = ColorMaps.getColorMaps().find {it.getKey() == "Magma"}.getValue()
def name = "HPV_1" // Set to null to reset
double minValue = 0.0
double maxValue = 1.0
def detections = getDetectionObjects()
def mapper = new MeasurementMapper(colorMapper, name, detections)
mapper.setDisplayMinValue(minValue)
mapper.setDisplayMaxValue(maxValue)
options = new OverlayOptions()
options.setMeasurementMapper(mapper)
options.setFillDetections(true)
options.setOpacity(0.7)
double downsample = 40

def imageData = getCurrentImageData()
def imageName = getProjectEntry().getImageName() + '.png'
def path = buildFilePath(PROJECT_BASE_DIR, "rendered")
mkdirs(path)
def path2 = buildFilePath(path, imageName)
//mkdirs(path)

def display = new qupath.lib.display.ImageDisplay(imageData)
def labelServer = new RenderedImageServer.Builder(imageData)
   .display(display)   
   .downsamples(downsample)
   .layers(new HierarchyOverlay(null, options, imageData))
   .build()
println('Running visualization for the following virtual whole slide image: ' + getProjectEntry().getImageName())

writeImage(labelServer,path2)

