from ._anvil_designer import ChatGPTTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ChatGPT(ChatGPTTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.generated_text.text = properties['generated_text']

  def confirm_btn_click(self, **event_args):
    self.raise_event('x-close-alert', value=self.generated_text.text)