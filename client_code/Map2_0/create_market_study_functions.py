from anvil import *

class Basic_App_Informations:
  self.bounding_box = [0, 0, 0, 0]
  
  def __init__(self, map):
    self.nursing_homes_checked = map.pdb_data_cb.checked
    self.assisted_living_checked = map.pdb_data_al.checked
    self.unique_code = server.call('get_unique_code')
    self.searched_address = js.call('getSearchedAddress')
    self.iso_layer = map.mapbox.getSource('iso')['_data']['features'][0]['geometry']['coordinates'][0]
    self.marker = Marker(map)
    self.get_bounding_box_from_iso_layer()

  def get_bounding_box_from_iso_layer(self):
    for point in self.iso_layer:
      if point[0] < self.bounding_box[1] or self.bounding_box[1] == 0:
        self.bounding_box[1] = point[0]
      if point[0] > self.bounding_box[3] or self.bounding_box[3] == 0:
        self.bounding_box[3] = point[0]
      if point[1] < self.bounding_box[0] or self.bounding_box[0] == 0:
        self.bounding_box[0] = point[1]
      if point[1] > self.bounding_box[2] or self.bounding_box[2] == 0:
        self.bounding_box[2] = point[1]


class Marker:
  self.marker_context = None
  
  def __init__(self, map):
    self.marker_coords_lng = dict(map.marker['_lngLat'])['lng']
    self.marker_coords_lat = dict(map.marker['_lngLat'])['lat']
    self.marker_coords = {
      "lng": (dict(map.marker['_lngLat'])['lng']),
      "lat": (dict(map.marker['_lngLat'])['lat'])
    }
    self.get_marker_context(map)

  def get_marker_context(self, map):
    request = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{self.marker_coords_lng},{self.marker_coords_lat}.json?access_token={map.token}"
    response = http.request(request, json=True)
    self.marker_context = response['features'][0]['context']
    
      