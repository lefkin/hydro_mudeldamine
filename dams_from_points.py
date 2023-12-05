import math
import re
# from qgis.core import *
# import qgis.utils
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QDialog, QFormLayout
from qgis.gui import QgsMapLayerComboBox
from qgis.core import QgsMapLayerProxyModel

dams = iface.activeLayer()

# Create dialog
new_dialog = QDialog()

# Add combobox for layer and field
map_layer_combo_box = QgsMapLayerComboBox()
map_layer_combo_box.setCurrentIndex(-1)
map_layer_combo_box.setFilters(QgsMapLayerProxyModel.VectorLayer)

# Create a form layout and add the two combobox
layout = QFormLayout()
layout.addWidget(map_layer_combo_box)

new_dialog.setLayout(layout)
new_dialog.exec_()  

ditch = map_layer_combo_box.currentLayer()
ditch.selectAll()

ditch_features = ditch.selectedFeatures()
geom_list = [g.geometry() for g in ditch_features]
ditch_geom = QgsGeometry().unaryUnion(geom_list)

# IMPORTANT fieldname!
def getlength(feat):
	try:
		# Specify a name for dam length field
		dam_length_field = 'Pikkus'
		m = float(re.match('\d', feat[dam_length_field]))
		ext = m.group()
	except:
		ext = 10

	return ext

def dam_coords(reference, distance, angle):
	angle = math.radians(angle)
	x = reference.x() + distance * math.sin(angle)
	y = reference.y() + distance * math.cos(angle)

	return QgsPoint(x, y)

dams.selectAll()
dam_features = dams.selectedFeatures()

id_nr = 1

#dams_layer = QgsVectorLayer('Polygon?crs=epsg:5652', 'dams', 'memory')
dams_layer = QgsVectorLayer('Linestring?crs=epsg:3301', 'dams', 'memory')
dams_provider = dams_layer.dataProvider()

dam_fields = QgsFields()
dam_fields.append(QgsField('id', QVariant.Int))
dam_fields.append(QgsField('tyyp',QVariant.String))
dams_provider.addAttributes(dam_fields)
dams_layer.updateFields()

dams_list = []

for d in dam_features:

	g = d.geometry()
#	tyyp = d.attribute('Tyyp')
	g.convertToSingleType()

	dist, point_on_ditch, atVert, leftof = ditch_geom.closestSegmentWithContext(g.asPoint())

	vertex = ditch_geom.vertexAt(atVert)
	print(id_nr, atVert)

	ditch_azimuth = QgsPoint(point_on_ditch).azimuth(vertex)

	if ditch_azimuth == 0:
		vertex = ditch_geom.vertexAt(atVert+1)
		ditch_azimuth = QgsPoint(point_on_ditch).azimuth(vertex)

	angle1 = ditch_azimuth + 90
	angle2 = ditch_azimuth + 270

	dam_length = getlength(d)

	dam_vertex1 = dam_coords(point_on_ditch, dam_length/2, angle1)
	dam_vertex2 = dam_coords(dam_vertex1, dam_length, angle2)

	p1 = '{} {}'.format(dam_vertex1.x(), dam_vertex1.y())
	p2 = '{} {}'.format(dam_vertex2.x(), dam_vertex2.y())

	dam_geom = QgsGeometry.fromWkt('Linestring({}, {})'.format(p1, p2))

	dam_feat = QgsFeature()
#	dam_feat.setGeometry(dam_geom.buffer(1, 0, 2, 3, 1))
	dam_feat.setGeometry(dam_geom)
#	dam_feat.setAttributes([id_nr, tyyp])
	dam_feat.setAttributes([id_nr])

	id_nr += 1

	dams_list.append(dam_feat)
	
dams_provider.addFeatures(dams_list)
dams_layer.updateExtents()
QgsProject.instance().addMapLayer(dams_layer)