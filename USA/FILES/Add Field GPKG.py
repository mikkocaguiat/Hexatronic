from qgis.core import QgsVectorLayer, QgsField, QgsProject
from qgis.PyQt.QtWidgets import QFileDialog, QLineEdit, QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox, QDialog, QDialogButtonBox
from qgis.PyQt.QtGui import QIcon
from qgis.utils import iface

# Custom dialog for field properties input
class FieldPropertiesDialog(QDialog):
    def __init__(self, parent=None):
        super(FieldPropertiesDialog, self).__init__(parent)
        self.setWindowTitle("Add Field")
        self.setWindowIcon(QIcon.fromTheme("python"))
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # Field name input
        self.field_name_input = QLineEdit(self)
        layout.addWidget(QLabel("Field Name:"))
        layout.addWidget(self.field_name_input)
        
        # Field type dropdown
        self.field_type_combo = QComboBox(self)
        self.field_type_combo.addItems(['String', 'Integer', 'Double', 'Date', 'DateTime', 'Boolean'])
        layout.addWidget(QLabel("Field Type:"))
        layout.addWidget(self.field_type_combo)
        
        # Field length input
        self.field_length_spinbox = QSpinBox(self)
        self.field_length_spinbox.setMinimum(1)
        self.field_length_spinbox.setMaximum(255)
        layout.addWidget(QLabel("Field Length:"))
        layout.addWidget(self.field_length_spinbox)
        
        # Dialog buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)
        
    def get_field_properties(self):
        field_name = self.field_name_input.text()
        field_type = self.field_type_combo.currentText()
        field_length = self.field_length_spinbox.value()
        return field_name, field_type, field_length

# Open a file dialog for the user to select the GeoPackage file
gpkg_path, _ = QFileDialog.getOpenFileName(None, "Select GeoPackage file", "", "GeoPackage Files (*.gpkg)")

if not gpkg_path:
    iface.messageBar().pushMessage("Error", "No GeoPackage file selected. Exiting.", level=3)
    exit()

# Create an instance of the custom dialog and get the field properties
dialog = FieldPropertiesDialog()
if dialog.exec_() != QDialog.Accepted:
    iface.messageBar().pushMessage("Info", "Field creation canceled. Exiting.", level=1)
    exit()
field_name, field_type, field_length = dialog.get_field_properties()

# Open the GeoPackage file
layer = QgsVectorLayer(gpkg_path, '', 'ogr')

# Get the list of layer names in the GeoPackage
layer_names = layer.dataProvider().subLayers()

# Iterate through each layer and add the field if not present
for layer_name in layer_names:
    # Extract the layer name from the full path
    layer_name = layer_name.split('!!::!!')[1]

    # Load the layer by its name
    layer = QgsVectorLayer(gpkg_path + "|layername=" + layer_name, layer_name, "ogr")

    # Check if the field already exists in the layer
    if field_name not in layer.fields().names():
        # Add the field to the layer
        field = QgsField(field_name, eval('QVariant.' + field_type), '', field_length)
        layer.dataProvider().addAttributes([field])
        layer.updateFields()

# Save changes to the GeoPackage
QgsProject.instance().writeEntry('WFSLayers', gpkg_path, layer.source())
