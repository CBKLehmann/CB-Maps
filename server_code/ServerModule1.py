import anvil.users
import anvil.server
from anvil import URLMedia

@anvil.server.callable
def get_app_url():
  app_url = anvil.server.get_app_origin()
  return app_url