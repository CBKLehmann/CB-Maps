from ._anvil_designer import Comp_SortTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Comp_Sort(Comp_SortTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.entries = properties['data']
    self.city_dropdown.items = self.entries.keys()

  def refresh_amount(self, **event_args):
    city_selected = False
    category_selected = False
    
    if not self.city_dropdown.selected_value == None:
      city = self.city_dropdown.selected_value
      city_selected = True

    if not self.category_dropdown.selected_value == None:
      category = self.category_dropdown.selected_value
      category_selected = True

    if city_selected and category_selected:
      self.amount = len(self.entries[city][category])
    elif city_selected:
      keys = self.entries[city].keys()
      self.amount = 0
      for key in keys:
        self.amount += len(self.entries[city][key])
    else:
      self.amount = 0

    if not self.custom_input.text == None:
      if self.custom_switch.selected and self.custom_input.text <= self.amount:
        self.amount = self.custom_input.text
        
    self.competitor_count.text = f"Found Competitor Amount: {self.amount}"

  def confirm_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    pass

