from anvil.js.window import mapboxgl, MapboxGeocoder
from .. import Functions
from . import Mapbox_Variables

def initialise_mapbox(dom, marker_draggable):
  mapboxgl.accessToken = Mapbox_Variables.token
  Mapbox_Variables.map = initialise_map(dom)
  Mapbox_Variables.location_marker = initialise_location_marker(marker_draggable)
  Mapbox_Variables.geocoder = initialise_geocoder()

def initialise_map(dom):
  return mapboxgl.Map(
    {
      'container': dom,
      'style': "mapbox://styles/mapbox/light-v11",
      'center': [13.4092, 52.5167],
      'zoom': 8
    }
  )

def initialise_location_marker(marker_draggable):
  return mapboxgl.Marker(
    {
      'draggable': marker_draggable, 
      'element': Functions.create_marker_div(), 
      'anchor': 'bottom'
    }
  ).setLngLat([13.4092, 52.5167]).addTo(Mapbox_Variables.map)

def initialise_geocoder():
  geocoder = MapboxGeocoder(
    {
      'accessToken': Mapbox_Variables.token, 
      'marker': False
    }
  )
  Mapbox_Variables.map.addControl(geocoder)
  return geocoder