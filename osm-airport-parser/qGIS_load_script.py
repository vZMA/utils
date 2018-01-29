import os.path, glob

wkt_files = 'd:\\src\\vzma\\utils\\osm-airport-parser\\qgis_files\\*.wkt'

layers=[]
for file in glob.glob(wkt_files):
  uri = "file:///" + file + "?delimiter=%s&wktField=%s&geomType=auto&useHeader=no&crs=epsg:4326" % (";", "field_2")
  vlayer = QgsVectorLayer(uri, os.path.basename(file), "delimitedtext")
  vlayer.addAttributeAlias(0,'name')
  vlayer.addAttributeAlias(1,'wkt')
  layers.append(vlayer)

QgsMapLayerRegistry.instance().addMapLayers(layers)

