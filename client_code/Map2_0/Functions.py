import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Variables, Layer, Images

global Variables, Layer, Images

def show_hide_marker(self, check_box, marker_id):
  #Show or Hide markers from given Excel Table

  for el in Variables.marker[marker_id]:
    if marker_id in Variables.marker:
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