from ._anvil_designer import Color_for_ClusterTemplate
from anvil import *
import anvil.users
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Color_for_Cluster(Color_for_ClusterTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.cluster_name.text = properties['cluster']
    self.color_dropdown.items = properties['colors']
    self.app_url = anvil.server.call('get_app_url')
    self.color = ''
    self.source = ''

    # Any code you write here will run before the form opens.

  def color_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    choosen_color = event_args['sender'].selected_value
    if choosen_color == 'blue':
      self.color = '#234ce2'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_blue.png'
    elif choosen_color == 'green':
      self.color = '#438e39'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_green.png'
    elif choosen_color == 'grey':
      self.color = '#b3b3b3'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_grey.png'
    elif choosen_color == 'lightblue':
      self.color = '#2fb2e0'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_lightblue.png'
    elif choosen_color == 'orange':
      self.color = '#fc9500'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_orange.png'
    elif choosen_color == 'pink':
      self.color = '#e254b7'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_pink.png'
    elif choosen_color == 'red':
      self.color = '#d32f2f'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_red.png'
    elif choosen_color == 'white':
      self.color = '#ffffff'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_white.png'
    elif choosen_color == 'yellow':
      self.color = '#f4de42'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_yellow.png'
    elif choosen_color == 'gold':
      self.color = '#ccb666'
      self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_gold.png'

    self.color_point.foreground = self.color
    self.marker.source = self.source
    pass

  def button_1_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not self.color_dropdown.selected_value == None:
      self.raise_event('x-close-alert', value=[self.color_dropdown.selected_value, self.color, self.source])
    pass


