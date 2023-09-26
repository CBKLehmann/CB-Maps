from anvil import *


''' Head Class for all Map related Sub-Classes '''
class Basic_App_Informations:
  def __init__(self, map):
    self.map = Map(map)
    self.marker = Marker(map)


''' Map Class for all relevant Map Informations '''
class Map:
  def __init__(self, map):
    self.unique_code = server.call('get_unique_code')
    self.searched_address = js.call('getSearchedAddress').split(",")[0]
    self.get_bounding_box_from_iso_layer(map.mapbox.getSource('iso')['_data']['features'][0]['geometry']['coordinates'][0])
    self.iso_time = map.time_dropdown.selected_value if not map.time_dropdown.selected_value == "-1" else "20"
    self.iso_movement = map.profile_dropdown.selected_value.lower()

  def get_bounding_box_from_iso_layer(self, iso_layer):
    self.bounding_box = [0, 0, 0, 0]
    for point in iso_layer:
      if point[0] < self.bounding_box[1] or self.bounding_box[1] == 0:
        self.bounding_box[1] = point[0]
      if point[0] > self.bounding_box[3] or self.bounding_box[3] == 0:
        self.bounding_box[3] = point[0]
      if point[1] < self.bounding_box[0] or self.bounding_box[0] == 0:
        self.bounding_box[0] = point[1]
      if point[1] > self.bounding_box[2] or self.bounding_box[2] == 0:
        self.bounding_box[2] = point[1]


''' Marker Class for all relevant Marker Informations '''
class Marker:
  def __init__(self, map):
    self.zipcode = "n.a."
    self.district = "n.a."
    self.city = "n.a."
    self.federal_state = "n.a."
    
    self.longitude = dict(map.marker['_lngLat'])['lng']
    self.latitude = dict(map.marker['_lngLat'])['lat']
    self.get_home_marker_location_informations(self.longitude, self.latitude, map.token)

  def get_home_marker_location_informations(self, longitude, latitude, token):
    request = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{longitude},{latitude}.json?access_token={token}"
    response = http.request(request, json=True)
    marker_context = response['features'][0]['context']
    for category in marker_context:
      if "postcode" in category['id']:
        self.zipcode = category['text']
      elif "locality" in category['id']:
        self.district = category['text']
      elif "place" in category['id']:
        self.city = category['text']
      elif "region" in category['id']:
        self.federal_state = category['text']
    if self.federal_state == "n.a.":
      self.federal_state = self.city
    if self.district == "n.a":
      self.district = self.city