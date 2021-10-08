from ._anvil_designer import Form1Template
from anvil import *
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import mapboxgl, MapboxGeocoder, document
import anvil.js
import anvil.http
import anvil.server


class Form1(Form1Template):
  
  def __init__(self, **properties):
    
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    self.dom = anvil.js.get_dom_node(self.spacer_1)
    self.time_dropdown.items = [("5 minutes", "5"), ("10 minutes", "10"), ("30 minutes", "30"), ("60 minutes", "60"), ("5 minutes layers", "-1")]
    self.token = "pk.eyJ1IjoiYnJvb2tlbXllcnMiLCJhIjoiY2tsamtiZ3l0MW55YjJvb2lsbmNxaWo0dCJ9.9iOO0aFkAy0TAP_qjtSE-A"


  def form_show(self, **event_args):
    
    """This method is called when the HTML panel is shown on the screen"""
    mapboxgl.accessToken = self.token
    self.mapbox = mapboxgl.Map({'container': self.dom,
                                'style': 'mapbox://styles/mapbox/outdoors-v11',
                                'center': [13.4092, 52.5167],
                                'zoom': 16})

    self.marker = mapboxgl.Marker({'color': '#0000FF', 'draggable': True})
    self.marker.setLngLat([13.4092, 52.5167]).addTo(self.mapbox)
    
    self.geocoder = MapboxGeocoder({'accessToken': mapboxgl.accessToken,
                                    'marker': False})
    
    self.mapbox.addControl(self.geocoder)
  
    self.geocoder.on('result', self.move_marker)
    self.marker.on('drag', self.marker_dragged) 
    
    
  def move_marker(self, result):
    lnglat = result['result']['geometry']['coordinates']
    self.marker.setLngLat(lnglat)
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    
  def marker_dragged(self, drag):
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    
  def get_iso(self, profile, contours_minutes):
    if not self.mapbox.getSource('iso'):
      self.mapbox.addSource('iso', {'type': 'geojson',
                                    'data': {'type': 'FeatureCollection',
                                             'features': []}
                                   }
                           )
      self.mapbox.addLayer({'id': 'isoLayer',
                            'type': 'fill',
                            'source': 'iso',
                            'layout': {},
                            'paint': {
                            'fill-color': '#ebb400',
                            'fill-opacity': 0.3
                            }
                           })
    
    lnglat = self.marker.getLngLat()
    response_string = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lnglat.lng},{lnglat.lat}?"
    
    if contours_minutes == "-1":
      response_string = response_string + f"contours_minutes=5,10,15,20"
    else:
      response_string = response_string + f"contours_minutes={contours_minutes}"
      
    response_string += f"&polygons=true&access_token={self.token}"
    
    response = anvil.http.request(response_string,json=True)
    
    self.mapbox.getSource('iso').setData(response)

  def time_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

  def profile_dropdown_change(self, **event_args):
    """This method is called when an item is selected"""
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

  def file_loader_1_change(self, file, **event_args):
    
    """This method is called when a new file is loaded into this FileLoader"""
    markercount = 1
    self.token = "pk.eyJ1IjoiYnJvb2tlbXllcnMiLCJhIjoiY2tsamtiZ3l0MW55YjJvb2lsbmNxaWo0dCJ9.9iOO0aFkAy0TAP_qjtSE-A"
    
    anvil.server.call('my_image_classifier', (file))
    
    while markercount <=  anvil.server.call('get_amount_of_adresses'):

      el = document.createElement('div')
      width = 50
      height = 50
      el.className = 'marker'
      
      if anvil.server.call('get_type_of_icon', markercount) == 'CapitalBay':
        el.style.backgroundImage = f'url(https://anvil.works/new-build/apps/ZETGHZB6W4UN4LYK/code/assets/haus.png/{width}/{height}/)'
      else:
        el.style.backgroundImage = f'url(https://anvil.works/new-build/apps/ZETGHZB6W4UN4LYK/code/assets/evil.png/{width}/{height}/)'
      el.style.width = f'{width}px'
      el.style.height = f'{height}px'
      el.style.backgroundSize = '100%'

      req_str = anvil.server.call('get_request_string', markercount)
      response_string = req_str + f'.json?access_token={self.token}'
      response = anvil.http.request(response_string,json=True)
      coordinates = response['features'][0]['geometry']['coordinates']
      
#       if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
#         self.marker_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
#       elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
#         self.marker_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
#       elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
#         self.marker_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
#       elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
#         self.marker_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
#       elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
#         self.marker_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
#       elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
#         self.marker_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
#       elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
#         self.marker_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})
        
#       self.marker_static.setLngLat(coordinates).addTo(self.mapbox)
      mapboxgl.Marker(el).setLngLat(coordinates).addTo(self.mapbox)
      markercount += 1
    
    pass

