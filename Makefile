PLUGIN_NAME   := kmz_tools
VERSION       := $(shell grep '^version=' metadata.txt | cut -d= -f2)
DIST_DIR      := dist
ZIP_NAME      := $(PLUGIN_NAME)_$(VERSION).zip

# Files and directories to include in the plugin ZIP
PLUGIN_FILES  := __init__.py \
                 kmz_tools_processing.py \
                 kmz_tools_provider.py \
                 package_layers_algorithm.py \
                 image_layer_to_kmz_algorithm.py \
                 geotagged_images_algorithm.py \
                 metadata.txt \
                 logo.svg

.PHONY: all package clean

all: package

## package – build a distributable ZIP ready for upload to the QGIS Plugin Repository
package: $(DIST_DIR)/$(ZIP_NAME)

$(DIST_DIR)/$(ZIP_NAME): $(PLUGIN_FILES)
	@mkdir -p $(DIST_DIR)
	@rm -f $(DIST_DIR)/$(ZIP_NAME)
	@zip -j $(DIST_DIR)/$(ZIP_NAME) $(PLUGIN_FILES)
	@echo "Plugin packaged → $(DIST_DIR)/$(ZIP_NAME)"

## clean – remove build artifacts
clean:
	@rm -rf $(DIST_DIR)
	@echo "Cleaned dist directory"
