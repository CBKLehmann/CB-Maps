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
    print(topic)
    
    if topic == 'Health':
      image = 'Pin_Healthcare'
    elif topic == 'Shopping & Grocery':
      image = 'Pin_Shopping'
    elif topic == 'Food & Drink':
      image = 'Pin_Food'
    elif topic == 'Transport':
      image = 'Pin_PublicTrans'
    elif topic == 'Services':
      image = 'Pin_Neutral'
    elif topic == 'Outdoor':
      image = 'Pin_Special'
    elif topic == 'Information':
      image = 'Pin_Information'
    self.icon_url = f'{self.app_url}/_/theme/Pins/{image}.png'
    self.icon_image.source = self.icon_url
    pass

  def confirm_click(self, **event_args):
    """This method is called when the button is clicked"""
    response = {
      'icon': self.icon_url,
      'name': self.object_name.text,
      'text': self.text_area.text,
      'address': self.address_results.selected_value
    }
    self.raise_event('x-close-alert', value = response)
    pass

  def address_input_lost_focus(self, **event_args):
    """This method is called when the TextBox loses focus"""
    print(event_args['sender'].text)
    address = event_args['sender'].text
    if not address == '':
      results = anvil.server.call('coords_from_address', address)
      items = []
      for result in results['features']:
        items.append((result['properties']['display_name'], result))
      self.address_results.items = items
    pass



