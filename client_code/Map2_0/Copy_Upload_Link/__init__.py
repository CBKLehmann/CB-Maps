from ._anvil_designer import Copy_Upload_LinkTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Copy_Upload_Link(Copy_Upload_LinkTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.link.text = properties['link']

    # Any code you write here will run before the form opens.

  def copy_click(self, **event_args):
    """This method is called when the button is clicked"""
    anvil.js.call('copy_to_clipboard', self.link.text)
    self.raise_event('x-close-alert')
    pass

