from ._anvil_designer import Active_CircleTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from ... import Functions
from anvil_extras.storage import local_storage

class Active_Circle(Active_CircleTemplate):
  def __init__(self, uni_code, mapbox, marker, layers, visible, circle_radius = 5, **properties):
    self.init_components(**properties)
    self.tag = uni_code
    self.mapbox = mapbox
    self.marker = marker
    self.layers = layers
    self.circle_radius = circle_radius
    self.radius.text = circle_radius
    self.radius.raise_event('change')
    self.active_switch.checked = visible
    self.active_switch.raise_event('change')

  def radius_change(self, **event_args):
    if event_args['sender'].text is not None:
      self.circle_radius = event_args['sender'].text
      self.update_circle()
      self.active_switch.checked = True
      self.active_switch.raise_event('change')
      new_storage = local_storage['distance_circles']
      new_storage[self.tag]['distance'] = event_args['sender'].text
      local_storage['distance_circles'] = new_storage

  def active_switch_change(self, **event_args):
    for layer in self.layers:
      self.mapbox.setLayoutProperty(layer, "visibility", "visible" if event_args['sender'].checked else "none")
    new_storage = local_storage['distance_circles']
    new_storage[self.tag]['visible'] = True if event_args['sender'].checked else False
    local_storage['distance_circles'] = new_storage

  def update_circle(self):
    self.mapbox.getSource(f'source_{self.tag}').setData(
        Functions.createGeoJSONCircle(
          [self.marker['_lngLat']['lng'], self.marker['_lngLat']['lat']], 
          self.circle_radius
        )['data']
      )