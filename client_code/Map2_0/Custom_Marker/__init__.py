from ._anvil_designer import Custom_MarkerTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Custom_Marker(Custom_MarkerTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.app_url = properties['url']

    # Any code you write here will run before the form opens.

  def icon_drop_down_change(self, **event_args):
    """This method is called when an item is selected"""
    topic = event_args['sender'].selected_value
    if topic == 'Nursing Home':
      image = 'Pflegeheim@4x'
    elif topic == 'Assisted Living':
      image = 'Betreutes_Wohnen@4x'
    elif topic == 'Nursing School':
      image = 'Pflegeschule@4x'
    elif topic == 'University':
      image = 'Universität@4x'
    elif topic == 'Cafe':
      image = 'Cafe@4x'
    elif topic == 'Cluster':
      image = 'CB_MapPin_orange'
    self.icon_url = f'{self.app_url}/_/theme/Pins/{image}.png'
    self.icon_image.source = self.icon_url
    pass

  def confirm_click(self, **event_args):
    """This method is called when the button is clicked"""
    response = {
      'icon': self.icon_url,
      'name': self.object_name.text,
      'text': self.text_area.text
    }
    self.raise_event('x-close-alert', value = response)
    pass

