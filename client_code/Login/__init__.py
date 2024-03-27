from ._anvil_designer import LoginTemplate
from anvil import *
from anvil.google.drive import app_files
from anvil.tables import app_tables
from ..Map2_0 import Functions, Variables
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
import anvil.tables as tables
import anvil.tables.query as q

class Login(LoginTemplate):
  def __init__(self, **properties):
    with anvil.server.no_loading_indicator:
      self.init_components(**properties)
      Functions.create_loading_overlay()
      Functions.get_mapbox_token()
      self.user = anvil.server.call('get_current_user')
      self.hash = get_url_hash()

  def form_show(self, **event_args):
    if self.user is not None:
      Variables.user_role = self.user['role']
      
      if Variables.maintenance and not Variables.user_role == "admin":
        from .Maintenance import Maintenance
        alert(content=Maintenance(), dismissible=False, buttons=[], large=True)
        return

      open_form('Map2_0')
      return

    if len(self.hash) > 0:
      open_form('Map2_0', role='guest')
      return

    self.display_login_form()

  def display_login_form(self):
    self.login_main_grid.visible = True
    width = anvil.js.window.innerWidth if anvil.js.window.innerWidth > 0 else anvil.js.screen.width;
    height = anvil.js.window.innerHeight if anvil.js.window.innerHeight > 0 else anvil.js.screen.height;
    
    if width <= 998:
      self.email_icon.visible = False
      self.password_icon.visible = False
  
  def login_click(self, **event_args):
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(True)
      
      if self.passwort_input.text == "123456":
        self.forgot_password.raise_event('click')
        Functions.manipulate_loading_overlay(False)
        alert('Please update your password using the link in the email you received.', dismissible=False, large=True, role='custom_alert_big')
        return
        
      self.user = anvil.server.call('login_user', email=self.email_input.text, password=self.passwort_input.text, remember=self.remember_me.checked)
      if self.user is None:
        self.error.visible = True
        Functions.manipulate_loading_overlay(False)
        return
        
      Variables.user_role = self.user['role']
      open_form('Map2_0')
          
  def forgot_password_click(self, **event_args):
    with anvil.server.no_loading_indicator:
      response = anvil.server.call('handle_password_reset', self.email_input.text)  
      if response == 200:
        self.error.text = "Reset Link has been send to given Email if Email exists"
        self.error.visible = True
        return

      self.error.text = "Given E-Mail not found"
      self.error.visible = True
