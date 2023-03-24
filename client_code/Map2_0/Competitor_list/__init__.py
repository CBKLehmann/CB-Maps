from ._anvil_designer import Competitor_listTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Competitor_list(Competitor_listTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    for competitor in properties['competitors']:
      row = DataRowPanel(item={
        "operator": competitor['operator'],
        "address": f"{competitor['address']}, {competitor['zip']} {competitor['city']}",
        "distance": competitor['distance'],
        "360_operator": competitor['360_operator'],
        "living_concept": competitor['living_concept'],
        "equipment": competitor['equiment'],
        "note": competitor['note'],
        "community_spaces": competitor['community_spaces'],
        "furnishing": competitor['furnishing'],
        "services": competitor['services'],
        "apartments": competitor['apartments'],
        "size_range_m2": competitor['size_range_sqm'],
        "rent_per_m2_range": competitor['rent_range_sqm'],
        "rent_per_month_range": competitor['rent_range_month'],
        "created": competitor['created'],
        "updated": competitor['updated']
      })
      self.competitor_panel.add_component(row)

    # Any code you write here will run before the form opens.
