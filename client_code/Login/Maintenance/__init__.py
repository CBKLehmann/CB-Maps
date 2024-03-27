from ._anvil_designer import MaintenanceTemplate
from anvil import *

class Maintenance(MaintenanceTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
