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
    else:
      image = ''
    if image == '':
      self.icon_url = ''
      self.icon_label.foreground = 'theme:Red'
      self.error_icon.visible = True
      self.icon_is_error = True
    else:
      self.icon_label.foreground = 'theme:Gray 300'
      self.error_icon.visible = False
      self.icon_is_error = False
      self.icon_url = f'{self.app_url}/_/theme/Pins/{image}.png'
    self.icon_image.source = self.icon_url
    pass

  def text_change(self, **event_args):
    print(event_args['sender'] == self.object_name)
    print(len(self.text_area.text))
    print(len(self.object_name.text))
    if event_args['sender'] == self.object_name and len(self.text_area.text) == 0 and len(event_args['sender'].text) == 0:
      error = True
    elif event_args['sender'] == self.text_area and len(self.object_name.text) == 0 and len(event_args['sender'].text) == 0:
      error = True
    else:
      error = False
    print(error)
    if error:
      self.object.foreground = 'theme:Red'
      self.text_label.foreground = 'theme:Red'
      self.error_text.visible = True
      self.text_is_error = True
    else:
      self.object.foreground = 'theme:Gray 300'
      self.text_label.foreground = 'theme:Gray 300'
      self.error_text.visible = False
      self.text_is_error = False

  def confirm_click(self, **event_args):
    """This method is called when the button is clicked"""
    if not self.icon_is_error or not self.text_is_error:
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
    address = event_args['sender'].text
    if not address == '':
      results = anvil.server.call('coords_from_address', address)
      items = []
      for result in results['features']:
        items.append((result['properties']['display_name'], result))
      self.address_results.items = items
    pass



