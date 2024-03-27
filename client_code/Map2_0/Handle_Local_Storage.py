from anvil_extras.storage import local_storage

def load_local_storage_settings():
  change_map_style()

def change_map_style():
  map_style = local_storage.get('map_style')