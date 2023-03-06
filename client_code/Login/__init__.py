from ._anvil_designer import LoginTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Login(LoginTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    hash = get_url_hash()
    print(hash)
    if not len(hash) == 0:
      open_form('Map2_0', role='guest')
    # Any code you write here will run before the form opens.

  def login_click(self, **event_args):
    try:
      user = anvil.users.login_with_email(self.email_input.text, self.passwort_input.text, remember=self.remember_me.checked)
      if user:
        open_form('Map2_0', role=dict(user)['role'])
    except anvil.users.AuthenticationFailed:
      self.error.visible = True
    pass

  def forgot_password_click(self, **event_args):
    reset = anvil.users.send_password_reset_email(self.email_input.text)
    self.error.text = "Reset Link has been send to given Email if Email exists"
    self.error.visible = True
    pass

