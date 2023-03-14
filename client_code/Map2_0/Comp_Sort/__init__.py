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
    marker_coords = properties['marker_coords']
    self.city_dropdown.items = self.entries.keys()
    city = anvil.server.call('address_from_coords', marker_coords[0], marker_coords[1])
    self.city_dropdown.selected_value = city

  def refresh_amount(self, **event_args):
    city_selected = False
    category_selected = False
    self.city = self.city_dropdown.selected_value
    self.category = self.category_dropdown.selected_value
    
    if not self.city == "None":
      city_selected = True

    if not self.category == None:
      category_selected = True

    if city_selected and category_selected:
      self.amount = len(self.entries[self.city][self.category])
    elif city_selected:
      keys = self.entries[self.city].keys()
      self.amount = 0
      for key in keys:
        self.amount += len(self.entries[self.city][key])
    else:
      self.amount = 0

    if not self.custom_input.text == None:
      if self.custom_switch.selected and self.custom_input.text <= self.amount:
        self.amount = self.custom_input.text

    if self.amount > 0:
      if not self.category == None:
        self.competitor_list.clear()
        for i in range(self.amount):
          if len(f"{self.entries[self.city][self.category][i]['distance']}") > 5:
            distance = f"{self.entries[self.city][self.category][i]['distance']}"[:5]
          else:
            distance = self.entries[self.city][self.category][i]['distance']
          row = DataRowPanel(item={
            "address": self.entries[self.city][self.category][i]['address'],
            "zip": self.entries[self.city][self.category][i]['zip'],
            "operator": self.entries[self.city][self.category][i]['operator'],
            "360_operator": self.entries[self.city][self.category][i]['360_operator'],
            "apartments": self.entries[self.city][self.category][i]['apartments'],
            "distance": f"{distance} km"
          })
          self.competitor_list.add_component(row)
        
    self.competitor_count.text = f"Found Competitor Amount: {self.amount}"

  def confirm_btn_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    pass

