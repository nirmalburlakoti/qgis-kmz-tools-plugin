"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterString,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsField,
                       QgsFields,
                       QgsCoordinateReferenceSystem)
from qgis.PyQt.QtCore import QVariant
import os
import shutil
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import zipfile
import tempfile
from datetime import datetime

class GeotaggedImagesToKmzAlgorithm(QgsProcessingAlgorithm):
    
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_KMZ = 'OUTPUT_KMZ'
    LAYER_NAME = 'LAYER_NAME'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)
    
    def createInstance(self):
        return GeotaggedImagesToKmzAlgorithm()
    
    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm.
        """
        return 'geotagged_images_to_kmz'
    
    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Convert Geotagged Images to KMZ')
    
    def group(self):
        """
        Returns the name of the group this algorithm belongs to.
        """
        return self.tr('KMZ Tools')
    
    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to.
        """
        return 'kmz_tools'
    
    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm.
        """
        return self.tr("Converts a folder of geotagged images to a KMZ file with placemark points.")
    
    def initAlgorithm(self, config=None):
        """
        Define the inputs and outputs of the algorithm.
        """
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_FOLDER,
                self.tr('Input folder with geotagged images'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )
        
        self.addParameter(
            QgsProcessingParameterString(
                self.LAYER_NAME,
                self.tr('Layer name'),
                defaultValue='Geotagged Photos'
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_KMZ,
                self.tr('Output KMZ file'),
                fileFilter='KMZ files (*.kmz)'
            )
        )
    
    def get_exif_data(self, image_path):
        """Extract GPS coordinates and other EXIF data from image"""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            
            if exif_data is not None:
                result = {}
                for tag, value in exif_data.items():
                    tag_name = TAGS.get(tag, tag)
                    if tag_name == 'GPSInfo':
                        gps_data = {}
                        for gps_tag in value:
                            sub_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                            gps_data[sub_tag_name] = value[gps_tag]
                        result['GPSInfo'] = gps_data
                    elif tag_name == 'DateTime':
                        result['DateTime'] = value
                    elif tag_name == 'DateTimeOriginal':
                        result['DateTimeOriginal'] = value
                return result
        except Exception:
            pass
        return None
    
    def convert_to_degrees(self, value):
        """Convert GPS coordinates to decimal degrees"""
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)
    
    def get_coordinates(self, exif_data):
        """Extract latitude and longitude from EXIF data"""
        if not exif_data or 'GPSInfo' not in exif_data:
            return None, None
            
        gps_data = exif_data['GPSInfo']
        lat = gps_data.get('GPSLatitude')
        lat_ref = gps_data.get('GPSLatitudeRef')
        lon = gps_data.get('GPSLongitude')
        lon_ref = gps_data.get('GPSLongitudeRef')
        
        if lat and lon and lat_ref and lon_ref:
            lat = self.convert_to_degrees(lat)
            if lat_ref != 'N':
                lat = -lat
                
            lon = self.convert_to_degrees(lon)
            if lon_ref != 'E':
                lon = -lon
                
            return lat, lon
        return None, None
    
    def get_datetime(self, exif_data):
        """Extract datetime from EXIF data"""
        if not exif_data:
            return None
            
        # Try DateTimeOriginal first, then DateTime
        datetime_str = exif_data.get('DateTimeOriginal') or exif_data.get('DateTime')
        if datetime_str:
            try:
                # Convert EXIF datetime format to readable format
                dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                return datetime_str
        return None
    
    def create_kml_content(self, features, layer_name):
        """Create KML content from features"""
        kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>{layer_name}</name>
    <description>Geotagged Photos</description>
"""
        
        for feature in features:
            name = feature['name']
            description = feature['description']
            lat, lon = feature['coordinates']
            
            kml_content += f"""    <Placemark>
      <name>{name}</name>
      <description><![CDATA[{description}]]></description>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>
"""
        
        kml_content += """  </Document>
</kml>"""
        return kml_content
    
    def processAlgorithm(self, parameters, context, feedback):
        """
        Process the algorithm.
        """
        input_folder = self.parameterAsFile(parameters, self.INPUT_FOLDER, context)
        output_kmz = self.parameterAsFileOutput(parameters, self.OUTPUT_KMZ, context)
        layer_name = self.parameterAsString(parameters, self.LAYER_NAME, context)
        
        # Supported image extensions
        image_extensions = ['.jpg', '.jpeg', '.tiff', '.tif']
        
        features = []
        processed_count = 0
        
        # Create temporary directory for organizing files
        temp_dir = tempfile.mkdtemp()
        photos_dir = os.path.join(temp_dir, 'Photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        try:
            # Process images in the folder
            for filename in os.listdir(input_folder):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    image_path = os.path.join(input_folder, filename)
                    
                    feedback.pushInfo(f'Processing: {filename}')
                    
                    exif_data = self.get_exif_data(image_path)
                    lat, lon = self.get_coordinates(exif_data)
                    
                    if lat is not None and lon is not None:
                        # Get datetime from EXIF
                        datetime_str = self.get_datetime(exif_data)
                        
                        feature = {
                            'name': os.path.splitext(filename)[0],
                            'filename': filename,
                            'datetime': datetime_str or 'Unknown',
                            'coordinates': (lat, lon)
                        }
                        features.append(feature)
                        
                        # Copy image to Photos directory
                        dest_path = os.path.join(photos_dir, filename)
                        shutil.copy2(image_path, dest_path)
                        
                        processed_count += 1
                    else:
                        feedback.pushInfo(f'No GPS data found in: {filename}')
            
            if not features:
                raise QgsProcessingException('No geotagged images found in the specified folder.')
            
            # Create KML content
            kml_content = self.create_kml_content(features, layer_name)
            
            # Write KML file to temp directory
            kml_path = os.path.join(temp_dir, 'doc.kml')
            with open(kml_path, 'w', encoding='utf-8') as kml_file:
                kml_file.write(kml_content)
            
            # Create KMZ file with photos
            with zipfile.ZipFile(output_kmz, 'w', zipfile.ZIP_DEFLATED) as kmz:
                # Add KML file
                kmz.write(kml_path, 'doc.kml')
                
                # Add all photos
                for filename in os.listdir(photos_dir):
                    photo_path = os.path.join(photos_dir, filename)
                    kmz.write(photo_path, f'Photos/{filename}')
                    
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        feedback.pushInfo(f'Successfully processed {processed_count} geotagged images')
        feedback.pushInfo(f'KMZ file created with embedded photos: {output_kmz}')
        
        return {self.OUTPUT_KMZ: output_kmz}