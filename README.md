# KMZ Tools

A QGIS plugin that provides powerful tools for creating KMZ files with embedded photos and combining multiple vector layers into a single KML/KMZ file.

## Description

KMZ Tools makes it easy to combine multiple vector layers into a single KMZ file which can be easily opened in Google Earth or any other GIS software. It also allows you to export individual shapefiles into KMZ format, including image files attached to the records. The directory path of images should be stored in any field of the layer, which can then be included in the KMZ along with the features.

## Features

- **Multiple Layers to KMZ**: Merge multiple vector layers into a single KML/KMZ file
- **Image Layer to KMZ**: Export vector layers with geotagged photos to KMZ format
- **Attribute Preservation**: Include all layer attributes in the KMZ output
- **Google Earth Compatible**: Generated KMZ files work seamlessly with Google Earth

## Requirements

- QGIS 3.0 or higher
- Python 3.6+

## Installation

### From QGIS Plugin Repository
1. Open QGIS
2. Go to **Plugins** → **Manage and Install Plugins**
3. Search for "KMZ Tools"
4. Click **Install Plugin**

### Manual Installation
1. Download the plugin from the [releases page](https://github.com/nirmalburlakoti/qgis-kmz-tools-plugin/releases)
2. Extract the ZIP file to your QGIS plugins directory:
   - Windows: `C:\Users\[username]\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - macOS: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in **Plugins** → **Manage and Install Plugins** → **Installed**

## Usage

### Image Layer to KMZ with Photos

This tool converts a vector layer with photo attributes to a KMZ file with embedded images.

1. Open the **Processing Toolbox** (Processing → Toolbox)
2. Navigate to **KMZ Tools** → **Image Layer to KMZ with Photos**
3. Configure the parameters:
   - **Input layer**: Select your vector layer
   - **Photo field**: Choose the field containing file paths to images
   - **Layer name**: Set a name for the layer in the KMZ
   - **Include all attributes**: Check to include all layer attributes in the description
   - **Output KMZ file**: Choose where to save the KMZ file
4. Click **Run**

#### Requirements for Photo Field
- The photo field must contain complete file paths to image files
- Images should be in common formats (JPG, PNG, etc.)
- File paths can use forward slashes (/) or backslashes (\)

### Multiple Layers to KMZ

This tool combines multiple vector layers into a single KMZ file.

1. Open the **Processing Toolbox**
2. Navigate to **KMZ Tools** → **Multiple Layers to KMZ**
3. Select the layers you want to combine
4. Configure output settings
5. Click **Run**

## Features in Detail

### Supported Geometry Types

- Point
- LineString
- Polygon
- All geometry types with Z coordinates

### Output Format

The generated KMZ files include:
- KML document with feature geometries
- Embedded photos in a `Photos/` directory
- Feature attributes as HTML tables
- Proper coordinate reference system (WGS84)

## Troubleshooting

### Photos Not Found
- Check that file paths in the photo field are correct
- Ensure image files exist at the specified locations
- Use absolute paths for best results

### Large File Sizes
- Consider resizing images before processing
- Use compressed image formats (JPEG with appropriate quality)

## Issues and Support

If you encounter any issues or have questions:

- Check the [Issues page](https://github.com/nirmalburlakoti/qgis-kmz-tools-plugin/issues)
- Create a new issue with:
  - QGIS version
  - Plugin version
  - Steps to reproduce the problem
  - Sample data (if possible)

## License

This project is licensed under the GNU General Public License v2.0 or later - see the [LICENSE](LICENSE) file for details.

## Author

**Nirmal Burlakoti**
- Email: snirmal33@yahoo.com
- GitHub: [@nirmalburlakoti](https://github.com/nirmalburlakoti)

## Changelog

### Version 1.0.0
- Released first version
- Added Image Layer to KMZ with Photos tool
- Added Multiple Layers to KMZ tool