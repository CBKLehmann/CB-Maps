#Import of different Modules
from ._anvil_designer import Map2_0Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil.js.window import mapboxgl, MapboxGeocoder, document
import anvil.js
import anvil.http
import json
from .. import Variables

#Definition of every function inside Map2_0
class Map2_0(Map2_0Template):
  
  #Set Form properties and Data Bindings
  def __init__(self, **properties):
    
    self.init_components(**properties)
    self.dom = anvil.js.get_dom_node(self.spacer_1)
    self.time_dropdown.items = [("5 minutes", "5"), ("10 minutes", "10"), ("30 minutes", "30"), ("60 minutes", "60"), ("5 minutes layers", "-1")]
    self.token = "pk.eyJ1IjoiYnJvb2tlbXllcnMiLCJhIjoiY2tsamtiZ3l0MW55YjJvb2lsbmNxaWo0dCJ9.9iOO0aFkAy0TAP_qjtSE-A"

  #This method is called when the HTML panel is shown on the screen
  def form_show(self, **event_args):
  
    #Initiate Map
    mapboxgl.accessToken = self.token
    self.mapbox = mapboxgl.Map({'container': self.dom,
                                'style': 'mapbox://styles/mapbox/outdoors-v11',
                                'center': [13.4092, 52.5167],
                                'zoom': 8})

    #Initiate Marker
    self.marker = mapboxgl.Marker({'color': '#0000FF', 'draggable': True})
    self.marker.setLngLat([13.4092, 52.5167]).addTo(self.mapbox)
    
    #Initiate Geocoder
    self.geocoder = MapboxGeocoder({'accessToken': mapboxgl.accessToken,
                                    'marker': False})
    self.mapbox.addControl(self.geocoder)
  
    #Initiate Listeners for different Functions  
    self.geocoder.on('result', self.move_marker)
    self.marker.on('drag', self.marker_dragged) 
    self.mapbox.on('mousemove', 'bundeslaender', self.mousemove)
    self.mapbox.on('mouseleave', 'bundeslaender', self.mouseleave)
    self.mapbox.on('mousemove', 'regierungsbezirke', self.mousemove)
    self.mapbox.on('mouseleave', 'regierungsbezirke', self.mouseleave)
    self.mapbox.on('mousemove', 'landkreise', self.mousemove)
    self.mapbox.on('mouseleave', 'landkreise', self.mouseleave)
    self.mapbox.on('click', 'bundeslaender', self.popup)
    self.mapbox.on('click', 'regierungsbezirke', self.popup)
    self.mapbox.on('click', 'landkreise', self.popup)
    self.mapbox.on('click', self.poi)
    
    #Get Geocoordinates for all Federal states
    jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
    #Add Mapsource for Federal states
    self.mapbox.addSource ('bundeslaender', {
      'type': 'geojson',
      'data': jsonfile
    })
    
    #Add filled Layer for Federal states
    self.mapbox.addLayer({
      'id': 'bundeslaender',
      'type': 'fill',
      'source': 'bundeslaender',
      'layout': {
          'visibility': 'visible'
      },
      'paint': {
        'fill-color': '#0080ff',
        'fill-opacity': [
              'case',
              ['boolean', ['feature-state', 'hover'], False],
              0.75,
              0.5
        ]
      }
    }); 

    #Add outlined Layer for Federal states
    self.mapbox.addLayer({
        'id': 'outlineBL',
        'type': 'line',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
            'line-color': '#000',
            'line-width': 2
        }
    });
    
    #Get Geocoordinates for all government districts 
    jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
    
    #Add Mapsource for government districts
    self.mapbox.addSource ('regierungsbezirke', {
      'type': 'geojson',
      'data': jsonfile
    })
    
    #Add filled Layer for government districts
    self.mapbox.addLayer({
      'id': 'regierungsbezirke',
      'type': 'fill',
      'source': 'regierungsbezirke',
      'layout': {
          'visibility': 'none'
      },
      'paint': {
        'fill-color': '#0080ff',
        'fill-opacity': [
              'case',
              ['boolean', ['feature-state', 'hover'], False],
              0.75,
              0.5
        ]
      }
    }); 

    #Add outlined Layer for government districts
    self.mapbox.addLayer({
        'id': 'outlineRB',
        'type': 'line',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
            'line-color': '#000',
            'line-width': 1
        }
    });
    
    #Get Geocoordinates for all rural districts
    jsonfile = anvil.server.call('get_geojson', 'landkreise')
    
    #Add Mapsource for rural districts
    self.mapbox.addSource ('landkreise', {
      'type': 'geojson',
      'data': jsonfile
    })
    
    #Add filled Layer for rural districts
    self.mapbox.addLayer({
      'id': 'landkreise',
      'type': 'fill',
      'source': 'landkreise',
      'layout': {
          'visibility': 'none'
      },
      'paint': {
        'fill-color': '#0080ff',
        'fill-opacity': [
              'case',
              ['boolean', ['feature-state', 'hover'], False],
              0.75,
              0.5
        ]
      }
    }); 

    #Add outlined Layer for rural districts
    self.mapbox.addLayer({
        'id': 'outlineLK',
        'type': 'line',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
            'line-color': '#000',
            'line-width': 0.5
        }
    });

  #This method is called when the Geocoder was used 
  def move_marker(self, result):
    
    #Set iso-Layer for new coordinates
    lnglat = result['result']['geometry']['coordinates']
    self.marker.setLngLat(lnglat)
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    
  #This method is called when the draggable Marker was moved
  def marker_dragged(self, drag):
    
    #Set iso-Layer for new Markerposition
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
  
  #This method is called when the draggable Marker was moved or when the Geocoder was used
  def get_iso(self, profile, contours_minutes):
    
    #Check if isoLayer is already constructed
    if not self.mapbox.getSource('iso'):
      
      #Construct Mapsource for isoLayer
      self.mapbox.addSource('iso', {'type': 'geojson',
                                    'data': {'type': 'FeatureCollection',
                                             'features': []}
                                   }
                           )
      
      #Construct and add isoLayer
      self.mapbox.addLayer({'id': 'isoLayer',
                            'type': 'fill',
                            'source': 'iso',
                            'layout': {},
                            'paint': {
                            'fill-color': '#ebb400',
                            'fill-opacity': 0.3
                            }
                           })
    
    #Get iso-coordinates based of the marker-coordinates
    lnglat = self.marker.getLngLat()
    request_string = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lnglat.lng},{lnglat.lat}?"
    
    #Check which iso-mode is currently active
    if contours_minutes == "-1":
      
      #Build request_string
      request_string = request_string + f"contours_minutes=5,10,15,20"
      
    else:
      
      #Build request_string
      request_string = request_string + f"contours_minutes={contours_minutes}"
    
    #Build request_string
    request_string += f"&polygons=true&access_token={self.token}"
    
    #Get Data from request
    response = anvil.http.request(request_string,json=True)
    
    #Attach Data to iso-source
    self.mapbox.getSource('iso').setData(response)
  
  #This method is called when the Mouse is moved inside an active Map-Layer 
  def mousemove(self, mousemove):
    
    #Get Global Variables from Variables
    global Variables
    hoveredStateId = Variables.hoveredStateId
    layer = Variables.activeLayer
    
    #Check if Mouse was moved inside active Map-Layer
    if len(mousemove.features) > 0:
      
      #Check if Layer is already hovered
      if hoveredStateId != None:
        
        #Check if active Layer is Bundesländer
        if layer == 'bundeslaender':
          
          #Change hover-State to False
          self.mapbox.setFeatureState({'source': 'bundeslaender', 'id': Variables.hoveredStateId}, {'hover': False})
          
        #Check if active Layer is Regierungsbezirke  
        elif layer == 'regierungsbezirke':
          
          #Change hover-State to False
          self.mapbox.setFeatureState({'source': 'regierungsbezirke', 'id': Variables.hoveredStateId}, {'hover': False})          
        
        #Check if active Layer is Landkreise
        elif layer == 'landkreise':
          
          #Change hover-State to False
          self.mapbox.setFeatureState({'source': 'landkreise', 'id': Variables.hoveredStateId}, {'hover': False})          
      
      #Change global hoveredStateID to new active Layer-id
      Variables.hoveredStateId = mousemove.features[0].id
      
      #Check if active Layer is Bundesländer
      if layer == 'bundeslaender':
        
        #Change hover-State to True
        self.mapbox.setFeatureState({'source': 'bundeslaender', 'id': Variables.hoveredStateId}, {'hover': True})
    
      #Check if active Layer is Regierungsbezirke
      elif layer == 'regierungsbezirke':     
      
        #Change hover-State to True      
        self.mapbox.setFeatureState({'source': 'regierungsbezirke', 'id': Variables.hoveredStateId}, {'hover': True})
       
      #Check if active Layer is Landkreise
      elif layer == 'landkreise': 
          
        #Change hover-State to True  
        self.mapbox.setFeatureState({'source': 'landkreise', 'id': Variables.hoveredStateId}, {'hover': True})
        
  #This method is called when the Mouse is leaving an active Map-Layer      
  def mouseleave(self, mouseleave):
    
    #Get Global Variables from Module 1
    global Variables
    
    #Check if Layer is already hovered
    if Variables.hoveredStateId != None:
      
      #Check if active Layer is Bundesländer
      if Variables.activeLayer == 'bundeslaender':
        
        #Change hover-State to False and set global-variable 'hoveredStateId' to None
        self.mapbox.setFeatureState({'source': 'bundeslaender', 'id': Variables.hoveredStateId}, {'hover': False})
        Variables.hoveredStateId = None
      
      #Check if active Layer is Regierungsbezirke
      elif Variables.activeLayer == 'regierungsbezirke': 

        #Change hover-State to False and set global-variable 'hoveredStateId' to None
        self.mapbox.setFeatureState({'source': 'regierungsbezirke', 'id': Variables.hoveredStateId}, {'hover': False})
        Variables.hoveredStateId = None        
      
      #Check if active Layer is Landkreise
      elif Variables.activeLayer == 'landkreise':  

        #Change hover-State to False and set global-variable 'hoveredStateId' to None
        self.mapbox.setFeatureState({'source': 'landkreise', 'id': Variables.hoveredStateId}, {'hover': False})
        Variables.hoveredStateId = None

  #This method is called when the Time-Dropdown-Menu has changed  
  def time_dropdown_change(self, **event_args):
    
    #Set iso-Layer for new Time-Option
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

  #This method is called when the Profile-Dropdown-Menu has changed  
  def profile_dropdown_change(self, **event_args):
    
   #Set iso-Layer for new Profile-Option 
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

  #This method is called when a new file is loaded into the FileLoader 
  def file_loader_upload_change(self, file, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
    
    #Call Server-Function to safe the File  
    anvil.server.call('save_local_excel_file', file)
    
    #Initialise Variables
    markercount = 1
    cb_marker = []
    kk_marker = []
    h_marker = []
    kh_marker = []
    s_marker = []
    lg_marker = []
    
    #Add Marker while Markercount is under Amount of Adresses inside provided File
    while markercount <= anvil.server.call('get_amount_of_adresses'):
      
      #Get Coordinates of provided Adress for Marker
      req_str = anvil.server.call('get_request_string', markercount)
      req_str += f'.json?access_token={self.token}'
      coords = anvil.http.request(req_str,json=True)
      coordinates = coords['features'][0]['geometry']['coordinates']
      
      #Create HTML Element for Marker
      el = document.createElement('div')
      width = 20
      height = 20
      el.className = 'marker'
      el.style.width = f'{width}px'
      el.style.height = f'{height}px'
      el.style.backgroundSize = '100%'
      el.style.backgroundrepeat = 'no-repeat'
       
      #Check which Icon the provided Adress has
      if anvil.server.call('get_type_of_icon', markercount) == 'CapitalBay':
        
        #Create Icon
        el.className = 'markerCB'
        el.style.backgroundImage = f'url(data:image/jpeg;base64,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)'
        
        #Check wich Markercolor the provided Adress has and color the Marker
        if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
          self.markerCB_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
          self.markerCB_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
          self.markerCB_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
          self.markerCB_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
          self.markerCB_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
          self.markerCB_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
          self.markerCB_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})
        
        #Add Marker to the Map
        newmarker = self.markerCB_static.setLngLat(coordinates).addTo(self.mapbox)
        
        #Add Icon to the Map
        newicon = mapboxgl.Marker(el).setLngLat(coordinates).setOffset([0,-22]).addTo(self.mapbox)
        
        #Add Marker and Icon to Marker-Array
        cb_marker.append(newmarker)
        cb_marker.append(newicon)
      
      #Check which Icon the provided Adress has
      elif anvil.server.call('get_type_of_icon', markercount) == 'Konkurrent':
        
        #Create Icon
        el.className = 'markerKK'
        el.style.backgroundImage = f'url(data:image/jpeg;base64,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)'
        
        #Check wich Markercolor the provided Adress has and color the Marker
        if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
          self.markerKK_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
          self.markerKK_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
          self.markerKK_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
          self.markerKK_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
          self.markerKK_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
          self.markerKK_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
          self.markerKK_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})
        
        #Add Marker to the Map
        newmarker = self.markerKK_static.setLngLat(coordinates).addTo(self.mapbox)
        
        #Add Icon to the Map
        newicon = mapboxgl.Marker(el).setLngLat(coordinates).setOffset([0,-22]).addTo(self.mapbox)
        
        #Add Marker and Icon to Marker-Array
        kk_marker.append(newmarker)
        kk_marker.append(newicon)
        
      #Check which Icon the provided Adress has
      elif anvil.server.call('get_type_of_icon', markercount) == 'Hotel':
         
        #Create Icon 
        el.className = 'markerH'
        el.style.backgroundImage = f'url(data:image/jpeg;base64,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)'
        
        #Check wich Markercolor the provided Adress has and color the Marker
        if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
          self.markerH_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
          self.markerH_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
          self.markerH_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
          self.markerH_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
          self.markerH_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
          self.markerH_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
          self.markerH_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})      
        
        #Add Marker to the Map
        newmarker = self.markerH_static.setLngLat(coordinates).addTo(self.mapbox)
        
        #Add Icon to the Map
        newicon = mapboxgl.Marker(el).setLngLat(coordinates).setOffset([0,-22]).addTo(self.mapbox)
        
        #Add Marker to Marker-Array
        h_marker.append(newmarker)
        h_marker.append(newicon)
      
      #Check which Icon the provided Adress has
      elif anvil.server.call('get_type_of_icon', markercount) == 'Krankenhaus':     
        
        #Create Icon
        el.className = 'markerKH'
        el.style.backgroundImage = f'url(data:image/jpeg;base64,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tQwXYHjcPle/i3/EiccBd82N5Z4x9ATAMr60OJp7wqo9uFCfxxbA8Plip8bnv0UBsBwBsIxDvfp+iw71mkP9ph1geKWIONKt8/mvvts3iu/QMjr9+r6btJuq6Pk0ALAKvVRFr8bvpl+o8bl7owgAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAFjGRJVyT1i1VpWiWeP9QD7NKkWrxuePiUZ9t28UAbCM7a1e7gmrtrPZiyr3CKCWqojY3uznnrFqdd6+UQTAMr5prJN7wqrtGVvKPQGosTqf/755vL7bN4oAWMZrpxaiEfW7lVRFxEVT87lnADV20dR8NGp4G7EZKV476fy3HAGwjFNb3Xjj1vr9Ir1hy3ycNtLNPQOosdNHunFRDS+kl2xtx+4aP77dKAJgBa6YnqvV7aSXjXfirdPHc88ANoG3zRyP82r0KOAV4534J9NzuWfUggBYgUak+Oc7Z+OyLe1oDvHjgEakuGRLO35k52yt370LDI9WleKHd83GG6faQ/04tFWluHxrO96984g3P69QK/eAumhEiitmjsdFU/NxV3siHloYiUO9Zhzr522orY1+bGv147zRxdg3tRintNz2BwarGSnetu14vH7LQtw1NxYPLo7FbK8xFOe/Ha1e7BlditdumY9dTbf9T4YAOEm7W714y/TxeMt07iUAG+vUVjeumOnGFeEW+2bgEQAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFKga9AH3XvX+l6dGeldEujyienFEjA/6awBAARYiqicj0ieqfvOGz9344/cO8uADC4Bvfvu1oxPbJ38xpbgm3FkAgEFKVVX9xshU80fu+qUfmx/EAQcSABe+69dHUpr9oyri0kEcDwD4f6Wo7hzb0rx0EBEwmFfq/SO/4OIPAOurirRvaa73wcEca432/tB1L0vN6gsR0RrAHgDghaWoYu89N/zU59dykDXfAUjN6upw8QeAjVJFineu9SCDeATg1j8AbKzL1nqAQQTAiwdwDABg5c6MSGt6jD+IAJgawDEAgJUbPfc914+u5QA+rw8ABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRpEABwbwDEAgJVbfPj693TWcoC1B0CVnljzMQCAk/F4RJXWcoC1B0Bq3LLmYwAAK1ZVseZr75oDoNdIN0bE0lqPAwCsSL/fr25Y60HWHAD3/fpPfTkifmWtxwEAlpciPvT5D//k/Ws9zkA+BbD19Pb7UqQ/HsSxAID/vxTxqaPj4/9yEMdqDuIgf/PJT/Zf9pbXfaxzrLUlonpl+HghAAxSL6L6taPj4+94+PofXRzEAatBHOS59v7QdS+LVuOqlNLlEXFWRMwM+msAQAGORhWPpxR/2oz+jXd/6Kf/KvcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANjs/jeh55l/kNaILQAAAABJRU5ErkJggg==)'
        
        #Check wich Markercolor the provided Adress has and color the Marker
        if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
          self.markerKH_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
          self.markerKH_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
          self.markerKH_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
          self.markerKH_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
          self.markerKH_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
          self.markerKH_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
          self.markerKH_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})         
     
        #Add Marker to the Map
        newmarker = self.markerKH_static.setLngLat(coordinates).addTo(self.mapbox)
        
        #Add Icon to the Map
        newicon = mapboxgl.Marker(el).setLngLat(coordinates).setOffset([0,-22]).addTo(self.mapbox)
        
        #Add Marker to Marker-Array
        kh_marker.append(newmarker)
        kh_marker.append(newicon)
      
      #Check which Icon the provided Adress has
      elif anvil.server.call('get_type_of_icon', markercount) == 'Laden':     
        
        #Create Icon
        el.className = 'markerLG'
        el.style.backgroundImage = f'url(data:image/jpeg;base64,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Ybcl6hgAGtD+x0d2duSsOUan6I/96wGJiJJIAGaHONY5qzan7YH+V8JuThxwDUCDxFdOnwWwoPSN7u/ap+RnVSPrAoiIqOWEDmRmiX/kRj9TwxmAKWr7k4H7s23aMrNTOyJYPSKi0AgBmDO0I5keYzEH/6njDMA05P/zwEEAi8rf6rpOlsQj9jB6uFMQEVEwhAD0DtFvtGv35R84ui3s9sQVA0ATCl88/jyABaXvLurBoPU9tyJukhWZZRYgIvKZAPScZml58RutTdxf+A/9vWE3Ke4YAHzQdn9vP4DbAKDy9Z7F0N0/d6S4BZbqkbbKKhcaZGt3uyIiSgwN0HQhYaKqm+K4yKhfIJP5Wtt/7O0Pu2lJwgDgs/xX+g8DGPd90+p/Le0uWXZ3kO3p6MAnYRirgzwmUTOq7ZlvmvMw2MpjzHKwYD0KN7XyGHFXKIiD5jzn+UAPOtMcaP/swYFAj0lEREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREQt8/8BLWa4HcZ152cAAAAASUVORK5CYII=)'
        
        #Check wich Markercolor the provided Adress has and color the Marker
        if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
          self.markerLG_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
          self.markerLG_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
          self.markerLG_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
          self.markerLG_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
          self.markerLG_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
          self.markerLG_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
          self.markerLG_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})    
        
        #Add Marker to the Map
        newmarker = self.markerLG_static.setLngLat(coordinates).addTo(self.mapbox)
        
        #Add Icon to the Map
        newicon = mapboxgl.Marker(el).setLngLat(coordinates).setOffset([0,-22]).addTo(self.mapbox)
        
        #Add Marker to Marker-Array
        lg_marker.append(newmarker)
        lg_marker.append(newicon)
      
      #Check which Icon the provided Adress has
      elif anvil.server.call('get_type_of_icon', markercount) == 'Schule':       
        
        #Create Icon
        el.className = 'markerS'
        el.style.backgroundImage = f'url(data:image/jpeg;base64,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)'
        
        #Check wich Markercolor the provided Adress has and color the Marker
        if anvil.server.call('get_color_of_marker', markercount) == 'Rot':
          self.markerS_static = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Gelb':  
          self.markerS_static = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Grün':  
          self.markerS_static = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Blau':  
          self.markerS_static = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Lila':  
          self.markerS_static = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Orange':  
          self.markerS_static = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
        elif anvil.server.call('get_color_of_marker', markercount) == 'Dunkelgrün':  
          self.markerS_static = mapboxgl.Marker({'color': '#00B050', 'draggable': False})
        
        #Add Marker to the Map
        newmarker = self.markerS_static.setLngLat(coordinates).addTo(self.mapbox)
      
        #Add Icon to the Map
        newicon = mapboxgl.Marker(el).setLngLat(coordinates).setOffset([0,-22]).addTo(self.mapbox)
        
        #Add Marker to Marker-Array
        s_marker.append(newmarker)
        s_marker.append(newicon)

      #Create Popup for Marker and add it to the Map
      info_text = anvil.server.call('get_informationtext', markercount)
      popup = mapboxgl.Popup({'closeOnClick': False, 'offset': 25})
      popup.setHTML(info_text)
      popup_static = mapboxgl.Popup({'closeOnClick': False, 'offset': 5, 'className': 'static-popup', 'closeButton': False, 'anchor': 'top'}).setText(info_text).setLngLat(coords['features'][0]['geometry']['coordinates'])
      popup_static.addTo(self.mapbox)
      
      #Increase Markercount
      markercount += 1
    
    #Add Marker-Arrays to global Variable Marker
    Variables.marker.update({'cb_marker': cb_marker, 'kk_marker': kk_marker, 'h_marker': h_marker, 'kh_marker': kh_marker, 's_marker': s_marker, 'lg_marker': lg_marker})
    
  #This method is called when the Button for toggling the Marker-Popups got clicked    
  def button_infos_click(self, **event_args):
    
    #Call JS-Function for Show or Hide Popup
    anvil.js.call('hide_show_Popup')   
      
  #This method is called when the Button for changing the Map-Style to "Satellite Map" got clicked    
  def radio_button_sm_clicked(self, **event_args):

    #Get Global Variables from Variables
    global Variables
    
    #Change Map-Style to "Satellite Map"    
    self.mapbox.setStyle('mapbox://styles/mapbox/satellite-streets-v11')
    
    #Check which Layer is active
    if Variables.activeLayer == 'bundeslaender':
    
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'visible'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
    elif Variables.activeLayer == 'regierungsbezirke':
      
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'visible'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
    elif Variables.activeLayer == 'landkreise':
      
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'visible'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
    elif Variables.activeLayer == None:
      
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
  #This method is called when the Button for changing the Map-Style to "Outdoor Map" got clicked
  def radio_button_om_clicked(self, **event_args):
    
    #Get Global Variables from Variables
    global Variables
    
    #Change Map-Style to "Outdoor Map"
    self.mapbox.setStyle('mapbox://styles/mapbox/outdoors-v11')
    
    #Check which Layer is active
    if Variables.activeLayer == 'bundeslaender':
    
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'visible'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
    elif Variables.activeLayer == 'regierungsbezirke':
      
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'visible'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
    elif Variables.activeLayer == 'landkreise':
      
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'visible'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'visible'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
    
    elif Variables.activeLayer == None:
      
      #Get Geocoordinates for all Federal states
      jsonfile = anvil.server.call('get_geojson', 'bundeslaender')
    
      #Add Mapsource for Federal states
      self.mapbox.addSource ('bundeslaender', {
        'type': 'geojson',
        'data': jsonfile
      })
    
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': 'bundeslaender',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': 'bundeslaender',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      });
      
      #Get Geocoordinates for all government districts
      jsonfile = anvil.server.call('get_geojson', 'regierungsbezirke')
      
      #Add Mapsource for government districts
      self.mapbox.addSource ('regierungsbezirke', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': 'regierungsbezirke',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': 'regierungsbezirke',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      });
      
      #Get Geocoordinates for all rural districts
      jsonfile = anvil.server.call('get_geojson', 'landkreise')
      
      #Add Mapsource for rural districts
      self.mapbox.addSource ('landkreise', {
        'type': 'geojson',
        'data': jsonfile
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': 'landkreise',
        'layout': {
            'visibility': 'none'
        },
        'paint': {
          'fill-color': '#0080ff',
          'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], False],
                0.75,
                0.5
          ]
        }
      }); 
      
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': 'landkreise',
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      });
      
  #This method is called when the Check Box for CapitalBay-Icons is checked or unchecked
  def check_box_cb_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_cb.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['cb_marker']:
        
        el.addTo(self.mapbox)
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['cb_marker']:
        
        el.remove()

  #This method is called when the Check Box for Konkurrent-Icons is checked or unchecked      
  def check_box_kk_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_kk.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['kk_marker']:
        
        el.addTo(self.mapbox)
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['kk_marker']:
        
        el.remove()

  #This method is called when the Check Box for Hotel-Icons is checked or unchecked      
  def check_box_h_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_h.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['h_marker']:
        
        el.addTo(self.mapbox)
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['h_marker']:
        
        el.remove()

  #This method is called when the Check Box for Krankenhaus-Icons is checked or unchecked      
  def check_box_kh_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_kh.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['kh_marker']:
        
        el.addTo(self.mapbox)
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['kh_marker']:
        
        el.remove()

  #This method is called when the Check Box for Schule-Icons is checked or unchecked     
  def check_box_s_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_s.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['s_marker']:
        
        el.addTo(self.mapbox)
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['s_marker']:
        
        el.remove()

  #This method is called when the Check Box for Geschäfte-Icons is checked or unchecked      
  def check_box_g_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_g.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['lg_marker']:
        
        el.addTo(self.mapbox)
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['lg_marker']:
        
        el.remove()

  #This method is called when the Check Box for All-Icons is checked or unchecked      
  def check_box_all_change(self, **event_args):
    
    #Get global Variables from "Variables"
    global Variables
      
    #Check if Check Box is checked or unchecked  
    if self.check_box_all.checked == True:
        
      #Show Marker and Icon
      for el in Variables.marker['cb_marker']:
        el.addTo(self.mapbox)
        
      #Show Marker and Icon
      for el in Variables.marker['kk_marker']:
        el.addTo(self.mapbox)
        
      #Show Marker and Icon
      for el in Variables.marker['h_marker']:
        el.addTo(self.mapbox)  
        
      #Show Marker and Icon
      for el in Variables.marker['kh_marker']:
        el.addTo(self.mapbox)  
        
      #Show Marker and Icon
      for el in Variables.marker['s_marker']:
        el.addTo(self.mapbox)  
      
      #Show Marker and Icon
      for el in Variables.marker['g_marker']:
        el.addTo(self.mapbox)
      
      #Check every Checkbox for every Icon
      self.check_box_cb.checked = True
      self.check_box_kk.checked = True
      self.check_box_h.checked = True
      self.check_box_kh.checked = True
      self.check_box_s.checked = True
      self.check_box_g.checked = True
        
    else:
        
      #Hide Marker and Icon
      for el in Variables.marker['cb_marker']:
        el.remove()
        
     #Hide Marker and Icon
      for el in Variables.marker['kk_marker']:
        el.remove()
        
      #Hide Marker and Icon
      for el in Variables.marker['h_marker']:
        el.remove()  
        
      #Hide Marker and Icon
      for el in Variables.marker['kh_marker']:
        el.remove()  
      
      #Hide Marker and Icon
      for el in Variables.marker['s_marker']:
        el.remove()
      
      #Hide Marker and Icon
      for el in Variables.marker['g_marker']:
        el.remove()
      
      #Uncheck every Checkbox for every Icon
      self.check_box_cb.checked = False
      self.check_box_kk.checked = False
      self.check_box_h.checked = False
      self.check_box_kh.checked = False
      self.check_box_s.checked = False
      self.check_box_g.checked = False     
    
  #This method is called when the Check Box for Bundesländer-Layer is checked or unchecked
  def check_box_bl_change(self, **event_args):
    
    #Get Global Variables from Variables
    global Variables
    
    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('bundeslaender', 'visibility')

    #Check if Layer is visible or not
    if visibility == 'visible':
      
      #Hide active Layer
      self.mapbox.setLayoutProperty('bundeslaender', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineBL', 'visibility', 'none')
      
      #Set active Layer to None
      Variables.activeLayer = None
      
    else:
      
      #Set Visibility of Layer to visible and every other Layer to None
      self.mapbox.setLayoutProperty('bundeslaender', 'visibility', 'visible')
      self.mapbox.setLayoutProperty('outlineBL', 'visibility', 'visible')
      self.mapbox.setLayoutProperty('regierungsbezirke', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineRB', 'visibility', 'none')
      self.mapbox.setLayoutProperty('landkreise', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineLK', 'visibility', 'none')
      
      #Uncheck Check Box from other Layers
      self.check_box_rb.checked = False
      self.check_box_lk.checked = False
      
      #Set active Layer to Bundesländer
      Variables.activeLayer = 'bundeslaender'

  #This method is called when the Check Box for Regierungsbezirke-Layer is checked or unchecked     
  def check_box_rb_change(self, **event_args):
    
    #Get Global Variables from Variables
    global Variables
    
    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('regierungsbezirke', 'visibility')
    
    #Check if Layer is visible or not
    if visibility == 'visible':
      
      #Hide active Layer
      self.mapbox.setLayoutProperty('regierungsbezirke', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineRB', 'visibility', 'none')
      
      #Set active Layer to None
      Variables.activeLayer = None
      
    else:
      
      #Set Visibility of Layer to visible and every other Layer to None
      self.mapbox.setLayoutProperty('regierungsbezirke', 'visibility', 'visible')
      self.mapbox.setLayoutProperty('outlineRB', 'visibility', 'visible')
      self.mapbox.setLayoutProperty('bundeslaender', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineBL', 'visibility', 'none')
      self.mapbox.setLayoutProperty('landkreise', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineLK', 'visibility', 'none')
      
      #Uncheck Check Box from other Layers
      self.check_box_bl.checked = False
      self.check_box_lk.checked = False
      
      #Set active Layer to Regierungsbezirke
      Variables.activeLayer = 'regierungsbezirke'

  #This method is called when the Check Box for Landkreise-Layer is checked or unchecked  
  def check_box_lk_change(self, **event_args):
    
    #Get Global Variables from Variables
    global Variables
    
    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('landkreise', 'visibility')
    
    #Check if Layer is visible or not
    if visibility == 'visible':
      
      #Hide active Layer
      self.mapbox.setLayoutProperty('landkreise', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineLK', 'visibility', 'none')
      
      #Set active Layer to None
      Variables.activeLayer = None
      
    else:
      
      #Set Visibility of Layer to visible and every other Layer to None
      self.mapbox.setLayoutProperty('landkreise', 'visibility', 'visible')
      self.mapbox.setLayoutProperty('outlineLK', 'visibility', 'visible')
      self.mapbox.setLayoutProperty('bundeslaender', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineBL', 'visibility', 'none')
      self.mapbox.setLayoutProperty('regierungsbezirke', 'visibility', 'none')
      self.mapbox.setLayoutProperty('outlineRB', 'visibility', 'none')
      
      #Uncheck Check Box from other Layers
      self.check_box_bl.checked = False
      self.check_box_rb.checked = False
      
      #Set active Layer to Landkreise
      Variables.activeLayer = 'landkreise'

  #This method is called when the Button Icons is clicked
  def button_icons_click(self, **event_args):
    
    #Check if Checkbox-Panel is visible or not
    if self.linear_panel_2.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.linear_panel_2.visible = False
      self.button_icons.icon = 'fa:angle-right'
      
    else:
      
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.linear_panel_2.visible = True
      self.button_icons.icon = 'fa:angle-down'

  #This method is called when the Button Icons is clicked    
  def button_overlay_click(self, **event_args):
    
    #Check if Checkbox-Panel is visible or not
    if self.linear_panel_1.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.linear_panel_1.visible = False
      self.button_overlay.icon = 'fa:angle-right'
      
    else:
      
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.linear_panel_1.visible = True
      self.button_overlay.icon = 'fa:angle-down'
    
  #This method is called when the User clicked a Part of a Map-Layer  
  def popup(self, click):
    
    #Check which Layer is active
    if click.features[0].layer.source == 'bundeslaender':
      
      #Create Popup and add it to the Map
      bl_name = click.features[0].properties.name
      bl_id = click.features[0].id
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}').addTo(self.mapbox)
    
    #Check which Layer is active
    elif click.features[0].layer.source == 'regierungsbezirke':
      
      #Create Popup and add it to the Map
      bl_name = click.features[0].properties.NAME_1
      rb_name = click.features[0].properties.NAME_2
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}<br><b>Regierungsbezirk:</b> {rb_name}').addTo(self.mapbox)
    
     #Check which Layer is active
    elif click.features[0].layer.source == 'landkreise':
      
      #Create Popup and add it to the Map
      bl_name = click.features[0].properties.NAME_1
      rb_name = click.features[0].properties.NAME_2
      lk_name = click.features[0].properties.NAME_3
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}<br><b>Regierungsbezirk:</b> {rb_name}<br><b>Landkreis:</b> {lk_name}').addTo(self.mapbox)
  
  #This method is called when the User clicked on a Point of Interest on the Map
  def poi(self, click):
    
    global Variables
    
    #Get all Layers on the Map
    layers = self.mapbox.getStyle().layers
    
    #Get all Features (Point of Interest) of selected Layers on clicked Point
    features = self.mapbox.queryRenderedFeatures(click.point, {'layers': ['poi-label', 'transit-label', 'landuse', 'national-park']})
    
    #Check if no POI was clicked and no Layer is active
    if not features == [] and Variables.activeLayer == None and hasattr(features[0].properties, 'name') == True:
    
      #Create Popup on clicked Point with Information about the Point of Interest
      popup = mapboxgl.Popup().setLngLat(click.lngLat).setHTML('you clicked here: <br/>' + features[0].properties.name).addTo(self.mapbox)