/* Read a CSV file containing detection objects and measurement values for them in the range 0 to 1 */

import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs
import qupath.lib.regions.ImagePlane
import qupath.lib.objects.classes.PathClassFactory
import qupath.lib.gui.dialogs.Dialogs
import java.io.BufferedReader
import java.io.FileReader
import java.io.IOException
import java.lang.Integer
import java.lang.Float
import qupath.lib.objects.PathObjects
import qupath.lib.regions.ImagePlane
import javax.imageio.ImageIO

// Get the main QuPath data structures
// Get the main QuPath data structures
def imageData = getCurrentImageData()
def hierarchy = imageData.getHierarchy()
def server = imageData.getServer()


/* The CSV header line should be as follows:
 * x,y,width,height,VALUENAME1,VALUENAME2,...
 * The VALUENAMEs are used as the labels for the detection object measurements.
 * 
 * The first value is used to label each object as a positive detection (>=0.5)
 * or negative detection (<0.5).
 */

/* Get the location of the CSV file */ 
def pathOutput = buildFilePath(PROJECT_BASE_DIR, 'OPSCCnet')
def includeText = server.getMetadata().getName().replace('.ndpi', '.csv').replace('.svs', '.csv').replace('.tiff', '.csv')

def dirOutput = new File(pathOutput)
if (!dirOutput.isDirectory()) {
    print dirOutput + ' is not a valid directory!'
    return
}
def files = dirOutput.listFiles({f -> f.isFile() && f.getName().contains(includeText)} as FileFilter) as List
if (files.isEmpty()) {
    print 'No mask files found in ' + dirOutput
    return
}

def csvfile = pathOutput + "/" + includeText

//int z = 0
//int t = 0
def plane = ImagePlane.getDefaultPlane()
def pathclass0 = PathClassFactory.getPathClass("HPV-", 0x800000)
def pathclass1 = PathClassFactory.getPathClass("HPV+", 0x008000)
def roi = ROIs.createRectangleROI(0, 0, 0, 0, plane)
def detection = PathObjects.createDetectionObject(roi, pathclass0)

// create a reader
try (BufferedReader br = new BufferedReader(new FileReader(csvfile))) {
    // CSV file delimiter
    String DELIMITER = ","
    String line, valuename
    String[] headers
    int i, x, y, width, height
    float value
    def detections = []

    // read CSV header line
    if ((line = br.readLine()) != null) {
        headers = line.split(DELIMITER)
        if (headers.length < 5 ||
            ! headers[0].equals("x") || ! headers[1].equals("y") ||
            ! headers[2].equals("width") || ! headers[3].equals("height")) {
            Dialogs.showErrorMessage(
                "CSV error", "The CSV header line is invalid; should be 'x,y,width,height,VALUENAME1,...'")
            return
        }
    } else {
        Dialogs.showErrorMessage("CSV error", "The CSV file is empty")
        return
    }

    // Create dummy detection objects to make the measurement limits 0 and 1
    roi = ROIs.createRectangleROI(0, 0, 1, 1, plane)
    detection = PathObjects.createDetectionObject(roi, pathclass0)
    for (i = 4; i < headers.length; i++) {
        detection.getMeasurementList().putMeasurement(headers[i], 0.0)
    }
    detection.getMeasurementList().close()
    detections.add(detection)

    roi = ROIs.createRectangleROI(0, 0, 1, 1, plane)
    detection = PathObjects.createDetectionObject(roi, pathclass1)
    for (i = 4; i < headers.length; i++) {
        detection.getMeasurementList().putMeasurement(headers[i], 1.0)
    }
    detection.getMeasurementList().close()
    detections.add(detection)

    int linenum = 1
    while ((line = br.readLine()) != null) {
        linenum++
        String[] columns = line.split(DELIMITER)
        if (columns.length != headers.length) {
            Dialogs.showErrorMessage("CSV file error",
                "CSV file line " + linenum + " has incorrect number of fields")
            break
        }

        x = Integer.parseInt(columns[0])
        y = Integer.parseInt(columns[1])
        width = Integer.parseInt(columns[2])
        height = Integer.parseInt(columns[3])
        
        roi = ROIs.createRectangleROI(x, y, width, height, plane)
 
        // Use the first value to determine the PathClass
        value = Float.parseFloat(columns[4])
        if (value < 0.5) {
            detection = PathObjects.createDetectionObject(roi, pathclass0)
        } else {
            detection = PathObjects.createDetectionObject(roi, pathclass1)
        }
 
        for (i = 4; i < headers.length; i++) {
            value = Float.parseFloat(columns[i])
            detection.getMeasurementList().putMeasurement(headers[i], value)
        }
        detection.getMeasurementList().close()
        detections.add(detection)
    }

    addObjects(detections)
} catch (IOException ex) {
    Dialogs.showErrorMessage("File open error", ex.getMessage())
}



getProjectEntry().saveImageData(getCurrentImageData())
