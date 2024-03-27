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
      self.user = anvil.users.get_user()
      Functions.create_loading_overlay()

  def form_show(self, **event_args):
    if self.user is not None:
      Variables.user_role = self.user['role']
      open_form('Map2_0', role=self.user['role'])
    else:
      hash = get_url_hash()
      if len(hash) > 0:
        open_form('Map2_0', role='guest')
      else:
        self.login_main_grid.visible = True
        width = anvil.js.window.innerWidth if anvil.js.window.innerWidth > 0 else anvil.js.screen.width;
        height = anvil.js.window.innerHeight if anvil.js.window.innerHeight > 0 else anvil.js.screen.height;
        if width <= 998:
          self.email_icon.visible = False
          self.password_icon.visible = False
    
  def login_click(self, **event_args):
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(True)
      try:
        if self.passwort_input.text == "123456":
          self.forgot_password.raise_event('click')
          Functions.manipulate_loading_overlay(False)
          alert('Please update your password using the link in the email you received.', dismissible=False, large=True, role='custom_alert_big')
        else:
          # self.user = anvil.users.login_with_email(self.email_input.text, self.passwort_input.text, remember=self.remember_me.checked)
          self.user = anvil.users.login_with_email(self.email_input.text, self.passwort_input.text, remember=False)
          if self.user:
            Variables.user_role = self.user['role']
            open_form('Map2_0')
      except anvil.users.AuthenticationFailed:
          self.error.visible = True
          Functions.manipulate_loading_overlay(False)

  def forgot_password_click(self, **event_args):
    with anvil.server.no_loading_indicator:
      reset = anvil.users.send_password_reset_email(self.email_input.text)
      self.error.text = "Reset Link has been send to given Email if Email exists"
      self.error.visible = True