from ._anvil_designer import Change_Cluster_ColorTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Change_Cluster_Color(Change_Cluster_ColorTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    for component in properties['components']:
      if type(component) == Label:
        print(component.foreground)
      else:
        print(component.text)
