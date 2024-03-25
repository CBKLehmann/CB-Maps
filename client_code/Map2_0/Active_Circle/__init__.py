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

class Active_Circle(Active_CircleTemplate):
  def __init__(self, uni_code, mapbox, marker, layers, **properties):
    self.init_components(**properties)
    self.tag = uni_code
    self.mapbox = mapbox
    self.marker = marker
    self.layers = layers
    self.circle_radius = 5

  def radius_change(self, **event_args):
    if event_args['sender'].text is not None:
      self.circle_radius = event_args['sender'].text
      self.update_circle()

  def active_switch_change(self, **event_args):
    for layer in self.layers:
      self.mapbox.setLayoutProperty(layer, "visibility", "visible" if event_args['sender'].checked else "none")

  def update_circle(self):
    self.mapbox.getSource(f'source_{self.tag}').setData(
        Functions.createGeoJSONCircle(
          [self.marker['_lngLat']['lng'], self.marker['_lngLat']['lat']], 
          self.circle_radius
        )['data']
      )