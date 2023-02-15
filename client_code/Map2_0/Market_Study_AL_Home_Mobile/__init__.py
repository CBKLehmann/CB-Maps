from ._anvil_designer import Market_Study_AL_Home_MobileTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Market_Study_AL_Home_Mobile(Market_Study_AL_Home_MobileTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.marker_coords = properties['marker_coords']

  def btn_click(self, **event_args):
    if event_args['sender'].text == 'Dismiss':
      response = []
    else:
      response = [{
        'name': self.name_input.text,
        'operator': self.operator_input.text,
        'type': self.type_input.text,
        'city': self.city_input.text,
        'status': self.status_input.text,
        'number_apts': self.apartment_count_input.text,
        'coords': self.marker_coords
      }, 0, 'home']
    self.raise_event('x-close-alert', value = response)
