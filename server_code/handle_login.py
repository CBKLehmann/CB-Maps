import anvil.users
import anvil.server

@anvil.server.callable
def get_current_user():
  return anvil.users.get_user(allow_remembered=False)
