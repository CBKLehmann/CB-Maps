from ._anvil_designer import Name_Share_LinkTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Name_Share_Link(Name_Share_LinkTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.input.text = properties['searched_address']

    # Any code you write here will run before the form opens.

  def confirm_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.raise_event('x-close-alert', value = self.input.text)
    pass

