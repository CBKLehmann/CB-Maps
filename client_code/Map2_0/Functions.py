import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Variables, Layer, Images
from anvil.js.window import document

global Variables, Layer, Images

def show_hide_marker(self, check_box, marker_id):
  #Show or Hide markers from given Excel Table
  
  for el in Variables.marker[marker_id]['marker']:
    if marker_id in Variables.marker.keys():
      if check_box:
        el.addTo(self.mapbox)
      else:
        el.remove()


def change_active_Layer(self, layer, inactive_layer, visibility, other_checkbox):
  #This method is called when the active Layer is changed

  for layer_entry in layer:
    self.mapbox.setLayoutProperty(layer_entry, 'visibility', visibility)
    for inactive_layer_entries in inactive_layer:
      for inactive_layer_entry in inactive_layer_entries:
        self.mapbox.setLayoutProperty(inactive_layer_entry, 'visibility', 'none')

  for checkbox in other_checkbox:
    checkbox.checked = False

  if visibility == 'visible':
    Variables.activeLayer = layer[0]
  else:
    Variables.activeLayer = None

    
def refresh_icons(self):
    
  checkbox =  self.poi_category.get_components()
  for panel in checkbox:
    if isinstance(panel, anvil.GridPanel):
      for component in panel.get_components():
        if not component.text == 'Select All':
          self.change_icons(component.text)


def create_bounding_box(self):
  
  # Get Data of Iso-Layer
  iso = dict(self.mapbox.getSource('iso'))

  # Create empty Bounding Box
  bbox = [0, 0, 0, 0]

  # Check every element in Iso-Data
  for el in iso['_data']['features'][0]['geometry']['coordinates'][0]:

    # Check if South-Coordinate of Element is lower then the lowest South-Coordinate of Bounding Box and BBox-Coordinate is not 0
    if el[0] < bbox[1] or bbox[1] == 0:

      # Set BBox-Coordinate to new Element-Coordinate
      bbox[1] = el[0]

    # Check if South-Coordinate of Element is higher then the highest South-Coordinate of Bounding Box and BBox-Coordinate is not 0
    if el[0] > bbox[3] or bbox[3] == 0:

      # Set BBox-Coordinate to new Element-Coordinate
      bbox[3] = el[0]

    # Check if North-Coordinate of Element is lower then the lowest North-Coordinate of Bounding Box and BBox-Coordinate is not 0
    if el[1] < bbox[0] or bbox[0] == 0:

      # Set BBox-Coordinate to new Element-Coordinate
      bbox[0] = el[1]

    # Check if North-Coordinate of Element is higher then the highest North-Coordinate of Bounding Box and BBox-Coordinate is not 0
    if el[1] > bbox[2] or bbox[2] == 0:

      # Set BBox-Coordinate to new Element-Coordinate
      bbox[2] = el[1]
      
  return bbox


def manipulate_loading_overlay(self, state):
    html = document.getElementsByClassName('anvil-root-container')[0]
    if state:
      if not Variables.loading:
        self.loading = document.createElement('div')
        self.loading.style.width = '100vw'
        self.loading.style.height = '100vh'
        self.loading.style.backgroundColor = 'rgba(62, 62, 62, .3)'
        self.loading.style.zIndex = '10000'
        self.loading.style.cursor = 'wait'
        self.loading.style.position = 'fixed'
        self.loading.style.top = '0'
        self.loading.style.left = '0'
        html.appendChild(self.loading)
        Variables.loading = True
    else:
      html.removeChild(self.loading)
      Variables.loading = False