import anvil.users
import anvil.server

@anvil.server.callable
def get_current_user():
  user = anvil.users.get_user()
  
  if user is not None and user['remember_me']:
    return user

  return None

@anvil.server.callable
def login_user(email, password, remember):
  try:
    user = anvil.users.login_with_email(email, password, remember=remember)
    user['remember_me'] = remember
    return user
  except anvil.users.AuthenticationFailed:
    return None

@anvil.server.callable
def handle_password_reset(email):
  try:
    anvil.users.send_password_reset_email(email)
    return 200
  except anvil.users.AuthenticationFailed:
    return 404