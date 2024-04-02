from ._anvil_designer import ErrorTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Error(ErrorTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.heading.text = properties['title']
    self.message.text = properties['message']

  def cancel_click(self, **event_args):
    self.raise_event('x-close-alert')
