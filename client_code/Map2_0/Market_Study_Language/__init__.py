from ._anvil_designer import Market_Study_LanguageTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Market_Study_Language(Market_Study_LanguageTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def continue_btn_click(self, **event_args):
    versions = []
    if self.english_check.checked:
      versions.append("en")
    if self.german_check.checked:
      versions.append("de")
    self.raise_event('x-close-alert', value = versions)