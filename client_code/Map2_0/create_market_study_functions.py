from anvil import *

class Basic_App_Informations:
  def __init__(self, map_self):
    self.nursing_homes_checked = map_self.pdb_data_cb.checked
    self.assisted_living_checked = map_self.pdb_data_al.checked
    self.unique_code = server.call('get_unique_code')
    self.searched_address = js.call('getSearchedAddress')
    self.marker_coords_lng = dict(map_self.marker['_lngLat'])['lng']
    self.marker_coords.lat = dict(map_self.marker['_lngLat'])['lat']
    self.marker_coords = {
      "lng": (dict(map_self.marker['_lngLat'])['lng']),
      "lat": (dict(map_self.marker['_lngLat'])['lat'])
    }



def get_basic_app_informations(self):
  Basic_App_Informations(self)
