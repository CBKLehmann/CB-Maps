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

  def btn_click(self, **event_args):
    print(event_args['sender'].text)
    if event_args['sender'].text == 'Dismiss':
      



