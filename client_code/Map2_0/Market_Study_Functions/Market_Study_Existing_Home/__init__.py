from ._anvil_designer import Market_Study_Existing_HomeTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Market_Study_Existing_Home(Market_Study_Existing_HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.found_label.text = f'Found the following Object for {properties["topic"]} with less than 10 meters distance to set Marker:'
    self.object_label.text = f'{properties["entry"][0]["name"]}'

  def btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=event_args['sender'].text)
