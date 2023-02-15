from ._anvil_designer import Market_Study_NH_HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Market_Study_NH_Home(Market_Study_NH_HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.marker_coords = properties['marker_coords']

  def btn_click(self, **event_args):
    print(event_args['sender'].text)
    if event_args['sender'].text == 'Dismiss':
      response = []
    else:
      response = [{
        'name': self.name_input.text,
        'platz_voll_pfl': self.beds_no_input.text,
        'ez': self.single_room_input.text,
        'dz': self.double_room_input.text,
        'anz_vers_pat': self.patients_input.text,
        'occupancy': self.occupancy_input.text,
        'baujahr': self.construction_year_input.text,
        'status': self.status_input.text,
        'betreiber': self.operator_input.text,
        'invest': self.invest_cost_input.text,
        'mdk_note': self. mdk_grade_input.text,
        'coords': self.marker_coords
      }, 0, 'home']
    self.raise_event('x-close-alert', value = response)



