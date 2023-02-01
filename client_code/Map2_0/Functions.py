import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Variables, Layer, Images

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
  for el in checkbox:
    if isinstance(el, anvil.LinearPanel):
      for component in el.get_components():
        if isinstance(component, anvil.LinearPanel):
          for ele in component.get_components():
            self.change_icons(ele.text)
    elif isinstance(el, anvil.CheckBox):
      self.change_icons(el.text)


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