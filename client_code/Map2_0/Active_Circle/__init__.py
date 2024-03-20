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
  def __init__(self, uni_code, mapbox, **properties):
    self.init_components(**properties)
    self.tag = uni_code
    self.mapbox = mapbox

  def radius_change(self, **event_args):
    self.mapbox.getSource(f'radius_{self.tag}').setData(Functions.createGeoJSONCircle([13.4092, 52.5167], event_args['sender'].text))
