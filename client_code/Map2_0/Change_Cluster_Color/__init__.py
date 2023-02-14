from ._anvil_designer import Change_Cluster_ColorTemplate
from anvil import *
import anvil.users
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
    self.last_cluster = ""
    self.app_url = anvil.server.call('get_app_url')
    self.confirm = Button(text='confirm')
    self.confirm.add_event_handler('click', self.confirm_btn_click)
    self.colors = ['blue', 'green', 'grey', 'lightblue', 'orange', 'pink', 'red', 'white', 'yellow', 'gold']
    self.selects = []
    self.heading.tag.color = ''
    self.heading.tag.type = 'Heading'
    self.spacer_1.tag.color = ''
    self.spacer_1.tag.type = 'Spacer'
    self.confirm.tag.color = ''
    self.confirm.tag.type = 'Button'
    for component in properties['components']:
      if type(component) == Label:
        if component.foreground == '#234ce2':
          self.color = 'blue'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_blue.png'
        elif component.foreground == '#438e39':
          self.color = 'green'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_green.png'
        elif component.foreground == '#b3b3b3':
          self.color = 'grey'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_grey.png'
        elif component.foreground == '#2fb2e0':
          self.color = 'lightblue'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_lightblue.png'
        elif component.foreground == '#fc9500':
          self.color = 'orange'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_orange.png'
        elif component.foreground == '#e254b7':
          self.color = 'pink'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_pink.png'
        elif component.foreground == '#d32f2f':
          self.color = 'red'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_red.png'
        elif component.foreground == '#ffffff':
          self.color = 'white'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_white.png'
        elif component.foreground == '#f4de42':
          self.color = 'yellow'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_yellow.png'
        elif component.foreground == '#ccb666':
          self.color = 'gold'
          self.source = f'{self.app_url}/_/theme/Pins/CB_MapPin_gold.png'

        if self.color in self.colors:
          self.colors.remove(self.color)
        point = Label(icon='fa:circle', align='center', foreground=component.foreground)
        image = Image(source=self.source, height=40)
        self.grid_panel_1.add_component(point, row=self.last_cluster, col_xs=9, width_xs=1)
        self.grid_panel_1.add_component(image, row=self.last_cluster, col_xs=10, width_xs=2)
        self.select.foreground = 'theme:Gray 300'
        self.select.tag.color = self.color
        self.select.tag.type = 'select'
        self.label.tag.color = self.color
        self.label.tag.type = 'label'
        image.tag.color = self.color
        image.tag.type = 'image'
        image.tag.source = self.source
        point.tag.color = self.color
        point.tag.type = 'point'
      else:
        self.last_cluster = component.text
        self.label = Label(text=self.last_cluster)
        self.select = DropDown(items=self.colors, include_placeholder=True, selected_value=None, placeholder='Choose a new color')
        self.select.add_event_handler('change', self.change_color)
        self.selects.append(self.select)
        self.grid_panel_1.add_component(self.label, row=self.last_cluster, col_xs=1, width_xs=5)
        self.grid_panel_1.add_component(self.select, row=self.last_cluster, col_xs=6, width_xs=3)
    self.grid_panel_1.add_component(self.confirm, row='confirm', col_xs=5, width_xs=2)

    for select in self.selects:
      select.items = self.colors

  def change_color(self, **event_args):
    self.oldColor = event_args['sender'].tag.color
    if event_args['sender'].selected_value == 'blue':
      color = '#234ce2'
      colorName = 'blue'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_blue.png'
    elif event_args['sender'].selected_value == 'green':
      color = '#438e39'
      colorName = 'green'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_green.png'
    elif event_args['sender'].selected_value == 'grey':
      color = '#b3b3b3'
      colorName = 'grey'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_grey.png'
    elif event_args['sender'].selected_value == 'lightblue':
      color = '#2fb2e0'
      colorName = 'lightblue'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_lightblue.png'
    elif event_args['sender'].selected_value == 'orange':
      color = '#fc9500'
      colorName = 'orange'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_orange.png'
    elif event_args['sender'].selected_value == 'pink':
      color = '#e254b7'
      colorName = 'pink'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_pink.png'
    elif event_args['sender'].selected_value == 'red':
      color = '#d32f2f'
      colorName = 'red'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_red.png'
    elif event_args['sender'].selected_value == 'white':
      color = '#ffffff'
      colorName = 'white'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_white.png'
    elif event_args['sender'].selected_value == 'yellow':
      color = '#f4de42'
      colorName = 'yellow'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_yellow.png'
    elif event_args['sender'].selected_value == 'gold':
      color = '#ccb666'
      colorName = 'gold'
      source = f'{self.app_url}/_/theme/Pins/CB_MapPin_gold.png'

    for component in self.grid_panel_1.get_components():
      if component.tag.type == 'point':
        if component.tag.color == self.oldColor:
          component.foreground = color
          component.tag.color = colorName
      elif component.tag.type == 'image':
        if component.tag.color == self.oldColor:
          component.tag.color = colorName
          component.tag.source = source
          component.source = source
      elif component.tag.type == 'select':
        if component.tag.color == self.oldColor:
          component.tag.color = colorName
        items = component.items
        items.remove(colorName)
        items.append(self.oldColor)
        component.items = items
        component.selected_value = None
      elif component.tag.type == 'label':
        if component.tag.color == self.oldColor:
          component.tag.color = colorName
    
  def confirm_btn_click(self, **event_args):
    response = {}
    color_arr = []
    for component in self.grid_panel_1.get_components():
      if component.tag.type == 'label':
        cluster = component.text
        color = component.tag.color
        color_arr.append(color)
      elif component.tag.type == 'point':
        color_code = component.foreground
        color_arr.append(color_code)
      elif component.tag.type == 'image':
        pin = component.tag.source
        color_arr.append(pin)
      if len(color_arr) == 3:
        response[cluster] = color_arr
        color_arr = []
    self.raise_event('x-close-alert', value=response)