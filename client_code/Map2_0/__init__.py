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
from .. import Variables, Layer

#Get global Variables
global Variables, Layer

#Definition of every function inside Map2_0
class Map2_0(Map2_0Template):

  ##### General Functions #####  
  
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
      self.mapbox.on('mousemove', 'bundeslaender', self.change_hover_state)
      self.mapbox.on('mouseleave', 'bundeslaender', self.change_hover_state)
      self.mapbox.on('mousemove', 'regierungsbezirke', self.change_hover_state)
      self.mapbox.on('mouseleave', 'regierungsbezirke', self.change_hover_state)
      self.mapbox.on('mousemove', 'landkreise', self.change_hover_state)
      self.mapbox.on('mouseleave', 'landkreise', self.change_hover_state)
      self.mapbox.on('mousemove', 'gemeinden', self.change_hover_state)
      self.mapbox.on('mouseleave', 'gemeinden', self.change_hover_state)
      self.mapbox.on('mousemove', 'bezirke', self.change_hover_state)
      self.mapbox.on('mouseleave', 'bezirke', self.change_hover_state)
      self.mapbox.on('click', 'bundeslaender', self.popup)
      self.mapbox.on('click', 'regierungsbezirke', self.popup)
      self.mapbox.on('click', 'landkreise', self.popup)
      self.mapbox.on('click', 'gemeinden', self.popup)
      self.mapbox.on('click', 'bezirke', self.popup)
      self.mapbox.on('click', self.poi)
      self.mapbox.on('styledata', self.place_layer)
 
  #####  General Functions  #####
  ###############################
  ##### Check-Box Functions #####

    #This method is called when the Check Box for CapitalBay-Icons is checked or unchecked
    def check_box_cb_change(self, **event_args):
    
      #Call Function to show or hide Markers
      self.show_hide_marker(self.check_box_cb.checked, 'cb_marker')

    #This method is called when the Check Box for Konkurrent-Icons is checked or unchecked      
    def check_box_kk_change(self, **event_args):
    
      #Call Function to show or hide Markers
      self.show_hide_marker(self.check_box_kk.checked, 'kk_marker')

    #This method is called when the Check Box for Hotel-Icons is checked or unchecked      
    def check_box_h_change(self, **event_args):
    
      #Call Function to show or hide Markers
      self.show_hide_marker(self.check_box_h.checked, 'h_marker')

    #This method is called when the Check Box for Krankenhaus-Icons is checked or unchecked      
    def check_box_kh_change(self, **event_args):
    
      #Call Function to show or hide Markers
      self.show_hide_marker(self.check_box_kh.checked, 'kh_marker')

    #This method is called when the Check Box for Schule-Icons is checked or unchecked     
    def check_box_s_change(self, **event_args):
    
      #Call Function to show or hide Markers
      self.show_hide_marker(self.check_box_s.checked, 's_marker')

    #This method is called when the Check Box for Geschäfte-Icons is checked or unchecked      
    def check_box_g_change(self, **event_args):
    
      #Call Function to show or hide Markers
      self.show_hide_marker(self.check_box_g.checked, 'lg_marker')

    #This method is called when the Check Box for All-Icons is checked or unchecked      
    def check_box_all_change(self, **event_args):
      
      #Get all Marker-Categoried and Status of Checkbox
      marker = self.icon_categories.get_components()
      check_box = self.check_box_all.checked
      
      #Loop through every Marker-Category
      for el in marker:
        
        #Call Function to show or hide Markers on Map
        self.show_hide_marker(check_box, el.tooltip)
        
        #Check every Checkbox for every Icon
        el.checked = check_box
    
    #This method is called when the Check Box for Bundesländer-Layer is checked or unchecked
    def check_box_bl_change(self, **event_args):
      
      #Get Visibility of Layer
      visibility = self.mapbox.getLayoutProperty('bundeslaender', 'visibility')
      
      #Check state of visibility
      if visibility == 'none':
      
        #Change Active Layer to show
        self.change_active_Layer(['bundeslaender', 'outlineBL'], [['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'visible', [self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_dt])
      
      #Check state of visibility
      elif visibility == 'visible':
      
        #Change Active Layer to hide
        self.change_active_Layer(['bundeslaender', 'outlineBL'], [['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'none', [self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_dt])

    #This method is called when the Check Box for Regierungsbezirke-Layer is checked or unchecked
    def check_box_rb_change(self, **event_args):
      
      #Get Visibility of Layer
      visibility = self.mapbox.getLayoutProperty('regierungsbezirke', 'visibility')
      
      #Check state of visibility
      if visibility == 'none':
      
        #Change Active Layer to show
        self.change_active_Layer(['regierungsbezirke', 'outlineRB'], [['bundeslaender', 'outlineBL'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'visible', [self.check_box_bl, self.check_box_lk, self.check_box_gm, self.check_box_dt])
      
      #Check state of visibility
      elif visibility == 'visible':
      
        #Change Active Layer to hide
        self.change_active_Layer(['regierungsbezirke', 'outlineRB'], [['bundeslaender', 'outlineBL'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'none', [self.check_box_bl, self.check_box_lk, self.check_box_gm, self.check_box_dt])

    #This method is called when the Check Box for Landkreise-Layer is checked or unchecked
    def check_box_lk_change(self, **event_args):

      #Get Visibility of Layer
      visibility = self.mapbox.getLayoutProperty('landkreise', 'visibility')
      
      #Check state of visibility
      if visibility == 'none':
      
        #Change Active Layer to show
        self.change_active_Layer(['landkreise', 'outlineLK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_gm, self.check_box_dt])
      
      #Check state of visibility
      elif visibility == 'visible':
      
        #Change Active Layer to hide
        self.change_active_Layer(['landkreise', 'outlineLK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_gm, self.check_box_dt])

    #This method is called when the Check Box for Gemeinden-Layer is checked or unchecked
    def check_box_gm_change(self, **event_args):
      
      #Get Visibility of Layer
      visibility = self.mapbox.getLayoutProperty('gemeinden', 'visibility')
      
      #Check state of visibility
      if visibility == 'none':
      
        #Change Active Layer to show
        self.change_active_Layer(['gemeinden', 'outlineGM'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['bezirke', 'outlineBK']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_dt])
      
      #Check state of visibility
      elif visibility == 'visible':
      
        #Change Active Layer to hide
        self.change_active_Layer(['gemeinden', 'outlineGM'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['bezirke', 'outlineBK']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_dt])
    
    #This method is called when the Check Box for Gemeinden-Layer is checked or unchecked
    def check_box_dt_change(self, **event_args):

            #Get Visibility of Layer
      visibility = self.mapbox.getLayoutProperty('bezirke', 'visibility')
      
      #Check state of visibility
      if visibility == 'none':
      
        #Change Active Layer to show
        self.change_active_Layer(['bezirke', 'outlineBK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_gm])
      
      #Check state of visibility
      elif visibility == 'visible':
      
        #Change Active Layer to hide
        self.change_active_Layer(['bezirke', 'outlineBK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_gm])
        
    #This method is called when the Check Box for POI 'doctors' is checked or unchecked
    def check_box_doc_change(self, **event_args):
    
      #Call create_icons-Function to set the Icons on Map and save last BBox of doctors
      Variables.last_bbox_doc = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, 'doctors', 'https://wiki.openstreetmap.org/w/images/7/71/Doctors-14.svg')
  
    #This method is called when the Check Box for POI 'dentist' is checked or unchecked
    def check_box_den_change(self, **event_args):
    
      #Call create_icons-Function to set the Icons on Map and save last BBox of dentist
      Variables.last_bbox_den = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, 'dentist', 'https://wiki.openstreetmap.org/w/images/8/86/Dentist-14.svg')
    
    #This method is called when the Check Box for POI 'clinic' is checked or unchecked
    def check_box_cli_change(self, **event_args):
   
      #Call create_icons-Function to set the Icons on Map and save last BBox of clinics
      Variables.last_bbox_cli = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, 'clinic', 'data:image/jpeg;base64,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tQwXYHjcPle/i3/EiccBd82N5Z4x9ATAMr60OJp7wqo9uFCfxxbA8Plip8bnv0UBsBwBsIxDvfp+iw71mkP9ph1geKWIONKt8/mvvts3iu/QMjr9+r6btJuq6Pk0ALAKvVRFr8bvpl+o8bl7owgAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAACAAgkAACiQAFjGRJVyT1i1VpWiWeP9QD7NKkWrxuePiUZ9t28UAbCM7a1e7gmrtrPZiyr3CKCWqojY3uznnrFqdd6+UQTAMr5prJN7wqrtGVvKPQGosTqf/755vL7bN4oAWMZrpxaiEfW7lVRFxEVT87lnADV20dR8NGp4G7EZKV476fy3HAGwjFNb3Xjj1vr9Ir1hy3ycNtLNPQOosdNHunFRDS+kl2xtx+4aP77dKAJgBa6YnqvV7aSXjXfirdPHc88ANoG3zRyP82r0KOAV4534J9NzuWfUggBYgUak+Oc7Z+OyLe1oDvHjgEakuGRLO35k52yt370LDI9WleKHd83GG6faQ/04tFWluHxrO96984g3P69QK/eAumhEiitmjsdFU/NxV3siHloYiUO9Zhzr522orY1+bGv147zRxdg3tRintNz2BwarGSnetu14vH7LQtw1NxYPLo7FbK8xFOe/Ha1e7BlditdumY9dTbf9T4YAOEm7W714y/TxeMt07iUAG+vUVjeumOnGFeEW+2bgEQAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFEgAAECBBAAAFKga9AH3XvX+l6dGeldEujyienFEjA/6awBAARYiqicj0ieqfvOGz9344/cO8uADC4Bvfvu1oxPbJ38xpbgm3FkAgEFKVVX9xshU80fu+qUfmx/EAQcSABe+69dHUpr9oyri0kEcDwD4f6Wo7hzb0rx0EBEwmFfq/SO/4OIPAOurirRvaa73wcEca432/tB1L0vN6gsR0RrAHgDghaWoYu89N/zU59dykDXfAUjN6upw8QeAjVJFineu9SCDeATg1j8AbKzL1nqAQQTAiwdwDABg5c6MSGt6jD+IAJgawDEAgJUbPfc914+u5QA+rw8ABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRIAAFAgAQAABRpEABwbwDEAgJVbfPj693TWcoC1B0CVnljzMQCAk/F4RJXWcoC1B0Bq3LLmYwAAK1ZVseZr75oDoNdIN0bE0lqPAwCsSL/fr25Y60HWHAD3/fpPfTkifmWtxwEAlpciPvT5D//k/Ws9zkA+BbD19Pb7UqQ/HsSxAID/vxTxqaPj4/9yEMdqDuIgf/PJT/Zf9pbXfaxzrLUlonpl+HghAAxSL6L6taPj4+94+PofXRzEAatBHOS59v7QdS+LVuOqlNLlEXFWRMwM+msAQAGORhWPpxR/2oz+jXd/6Kf/KvcgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANjs/jeh55l/kNaILQAAAABJRU5ErkJggg==')
  
    #This method is called when the Check Box for POI 'hospital' is checked or unchecked
    def check_box_hos_change(self, **event_args):
    
      #Call create_icons-Function to set the Icons on Map and save last BBox of hospital
      Variables.last_bbox_hos = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, 'hospital', 'https://wiki.openstreetmap.org/w/images/3/33/Hospital-14.svg')

    #This method is called when the Check Box for POI 'nursing_home' is checked or unchecked
    def check_box_nur_change(self, **event_args):
      
      #Call create_icons-Function to set the Icons on Map and save last BBox of nursing_home
      Variables.last_bbox_nur = self.create_icons(self.check_box_nur.checked, Variables.last_bbox_nur, 'nursing-home', 'data:image/jpeg;base64,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')
  
    #This method is called when the Check Box for POI 'pharmacy' is checked or unchecked
    def check_box_pha_change(self, **event_args):
      
      #Call create_icons-Function to set the Icons on Map and save last BBox of pharmacy
      Variables.last_bbox_pha = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, 'pharmacy', 'https://wiki.openstreetmap.org/w/images/1/1e/Pharmacy-14.svg')
  
    #This method is called when the Check Box for POI 'social_facility' is checked or unchecked
    def check_box_soc_change(self, **event_args):
      
      #Call create_icons-Function to set the Icons on Map and save last BBox of social_facility
      Variables.last_bbox_soc = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, 'social_facility', 'https://wiki.openstreetmap.org/w/images/0/0e/Social_facility-14.svg')
  
    #This method is called when the Check Box for POI 'doctors' is checked or unchecked
    def check_box_vet_change(self, **event_args):
      
      #Call create_icons-Function to set the Icons on Map and save last BBox of veterinary
      Variables.last_bbox_vet = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, 'veterinary', 'https://wiki.openstreetmap.org/w/images/f/fc/Veterinary-14.svg')
      
    #This method is called when the Check Box for POI based on HFCIG is checked or unchecked
    def checkbox_poi_x_hfcig_change(self, **event_args):
      
      #Get all categories of healthcare_poi_container
      checkbox =  self.poi_categories_healthcare_container.get_components()
      
      #Check if checkbox is checked
      if self.checkbox_poi_x_hfcig.checked == True:
        
        #Get Data of Iso-Layer
        iso = dict(self.mapbox.getSource('iso'))
        
        #Create empty Bounding Box
        bbox = [0, 0, 0, 0]
      
        #Check every element in Iso-Data
        for el in iso['_data']['features'][0]['geometry']['coordinates'][0]:
      
          #Check if South-Coordinate of Element is lower then the lowest South-Coordinate of Bounding Box and BBox-Coordinate is not 0
          if el[0] < bbox[1] or bbox[1] == 0:
    
            #Set BBox-Coordinate to new Element-Coordinate
            bbox[1] = el[0]
            
          #Check if South-Coordinate of Element is higher then the highest South-Coordinate of Bounding Box and BBox-Coordinate is not 0
          if el[0] > bbox[3] or bbox[3] == 0:
  
            #Set BBox-Coordinate to new Element-Coordinate
            bbox[3] = el[0]
          
          #Check if North-Coordinate of Element is lower then the lowest North-Coordinate of Bounding Box and BBox-Coordinate is not 0
          if el[1] < bbox[0] or bbox[0] == 0:
    
            #Set BBox-Coordinate to new Element-Coordinate
            bbox[0] = el[1]
          
          #Check if North-Coordinate of Element is higher then the highest North-Coordinate of Bounding Box and BBox-Coordinate is not 0
          if el[1] > bbox[2] or bbox[2] == 0:
  
            #Set BBox-Coordinate to new Element-Coordinate
            bbox[2] = el[1]
           
        #Do for every categories inside healthcare_poi_container
        for el in checkbox:
        
          #Check if categories-checkbox is checked
          if el.checked == True:
            
            #Loop through every Element in global Icon-Elements 
            for ele in Variables.icons[f'{el.text}']:
              
              #Get coordinates of current Icon
              ele_coords = dict(ele['_lngLat'])
              
              #Check if Icon is inside visible Bounding Box
              if bbox[0] > ele_coords['lat'] or ele_coords['lat'] > bbox[2] and bbox[1] > ele_coords['lng'] or ele_coords['lng'] < bbox[3]:
    
                #Remove Element from Map
                ele.remove()
  
      #Do if checkbox is unchecked
      else:  
        
          #Get visible Bounding Box of Map
          bbox = [(dict(self.mapbox.getBounds()['_sw']))['lat'], (dict(self.mapbox.getBounds()['_sw']))['lng'], (dict(self.mapbox.getBounds()['_ne']))['lat'], (dict(self.mapbox.getBounds()['_ne']))['lng']]
        
    #This method is called when the Check Box for POI 'bus' is checked or unchecked    
    def check_box_bus_change(self, **event_args):
      
      #Call create_icons-Function to set the Icons on Map and save last BBox of bus_stop
      Variables.last_bbox_bus = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, 'bus_stop', 'https://wiki.openstreetmap.org/w/images/5/5a/Amenity_bus_station.svg')
    
    #This method is called when the Check Box for POI 'tram' is checked or unchecked
    def check_box_tra_change(self, **event_args):
      
      #Call create_icons-Function to set the Icons on Map and save last BBox of tram_stop
      Variables.last_bbox_tra = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, 'tram_stop', 'https://upload.wikimedia.org/wikipedia/commons/a/a6/Tram-Logo.svg')

  ##### Check-Box Functions #####
  ###############################
  #####  Button Functions   #####

    #This method is called when the Button for toggling the Marker-Popups got clicked    
    def button_infos_click(self, **event_args):
    
      #Call JS-Function for Show or Hide Popup
      anvil.js.call('hide_show_Popup')   
      
    #This method is called when the Button for changing the Map-Style to "Satellite Map" got clicked    
    def radio_button_sm_clicked(self, **event_args):
    
      #Set new Mapstyle
      self.mapbox.setStyle('mapbox://styles/mapbox/satellite-streets-v11')
      
      #Call Function to reload Layers
      self.mapbox.on('styledata', self.place_layer)
  
    #This method is called when the Button for changing the Map-Style to "Outdoor Map" got clicked
    def radio_button_om_clicked(self, **event_args):
    
      #Set new Mapstyle
      self.mapbox.setStyle('mapbox://styles/mapbox/outdoors-v11')
      
      #Call Function to reload Layers
      self.mapbox.on('load', self.place_layer)
      
    #This method is called when the Button Icons is clicked
    def button_icons_click(self, **event_args):
      
      #Check if Checkbox-Panel is visible or not
      if self.icon_categories_all.visible == True:
      
        #Set Checkbox-Panel to invisible and change Arrow-Icon
        self.icon_change(self.icon_categories_all, False, self.button_icons, 'fa:angle-right')
        
      else:
        
        #Set Checkbox-Panel to visible and change Arrow-Icon
        self.icon_change(self.icon_categories_all, True, self.button_icons, 'fa:angle-down')

    #This method is called when the Button Icons is clicked
    def button_overlay_click(self, **event_args):
    
      #Check if Checkbox-Panel is visible or not
      if self.layer_categories.visible == True:
      
        #Set Checkbox-Panel to invisible and change Arrow-Icon
        self.icon_change(self.layer_categories, False, self.button_overlay, 'fa:angle-right')
        
      else:
        
        #Set Checkbox-Panel to visible and change Arrow-Icon
        self.icon_change(self.layer_categories, True, self.button_overlay, 'fa:angle-down')
        
    #This method is called when the User used the Admin-Button (!!!Just for Admin!!!)  
    def admin_button_click(self, **event_args):
    
      #Call a Server Function
      anvil.server.call('manipulate')
      
    #This method is called when the Healthcare-Button is clicked
    def button_healthcare_click(self, **event_args):
      
      #Check if Checkbox-Panel is visible or not
      if self.poi_categories_healthcare_container.visible == True:
      
        #Set Checkbox-Panel to invisible and change Arrow-Icon
        self.icon_change(self.poi_categories_healthcare_container, False, self.button_healthcare, 'fa:angle-right')
        
      else:
        
        #Set Checkbox-Panel to visible and change Arrow-Icon
        self.icon_change(self.poi_categories_healthcare_container, True, self.button_healthcare, 'fa:angle-down'),
        
    def hide_bar_button_click(self, **event_args):
      
      #Check if Checkbox-Panel is visible or not
      if self.Side_Bar.visible == True:
      
        #Set Checkbox-Panel to invisible and change Arrow-Icon
        self.icon_change(self.Side_Bar, False, self.hide_bar_button, 'fa:angle-left')
        
      else:
        
        #Set Checkbox-Panel to visible and change Arrow-Icon
        self.icon_change(self.Side_Bar, True, self.hide_bar_button, 'fa:angle-down'),

  #####  Button Functions   #####
  ###############################
  #####  Dropdown Functions #####

    #This method is called when the Time-Dropdown-Menu has changed  
    def time_dropdown_change(self, **event_args):
    
      #Set iso-Layer for new Time-Option
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
      
    #This method is called when the Profile-Dropdown-Menu has changed  
    def profile_dropdown_change(self, **event_args):
    
      #Set iso-Layer for new Profile-Option 
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

  #####  Dropdown Functions #####
  ###############################
  #####  Upload Functions   #####

    #This method is called when a new file is loaded into the FileLoader
    def file_loader_upload_change(self, file, **event_args):
      
      #Call Server-Function to safe the File  
      data = anvil.server.call('save_local_excel_file', file)
      
      #Initialise Variables
      markercount = 0
      cb_marker = []
      kk_marker = []
      h_marker = []
      kh_marker = []
      s_marker = []
      lg_marker = []
      
      #Add Marker while Markercount is under Amount of Adresses inside provided File
      while markercount < len(data):
        
        #Get Coordinates of provided Adress for Marker
        req_str = self.build_request_string(data[markercount])
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
        if data[markercount]['Icon'] == 'CapitalBay':
          
          #Set Markers based on Excel
          self.markerCB_static = None
          self.set_excel_markers(el, 'markerCB', Variables.imageCB, self.markerCB_static, coordinates, cb_marker, data[markercount]['Pinfarbe'])
        
        #Check which Icon the provided Adress has
        elif data[markercount]['Icon'] == 'Konkurrent':
          
          #Set Markers based on Excel
          self.markerKK_static = None
          self.set_excel_markers(el, 'markerKK', Variables.imageKK, self.markerKK_static, coordinates, kk_marker, data[markercount]['Pinfarbe'])  
          
        #Check which Icon the provided Adress has
        elif data[markercount]['Icon'] == 'Hotel':
          
          #Set Markers based on Excel
          self.markerH_static = None
          self.set_excel_markers(el, 'markerH', Variables.imageH, self.markerH_static, coordinates, h_marker, data[markercount]['Pinfarbe'])
         
        #Check which Icon the provided Adress has
        elif data[markercount]['Icon'] == 'Krankenhaus':     
          
          #Set Markers based on Excel
          self.markerKH_static = None
          self.set_excel_markers(el, 'markerKH', Variables.imageKH, self.markerKH_static, coordinates, kh_marker, data[markercount]['Pinfarbe'])
          
        #Check which Icon the provided Adress has
        elif data[markercount]['Icon'] == 'Laden':     
          
          #Set Markers based on Excel
          self.markerLG_static = None
          self.set_excel_markers(el, 'markerLG', Variables.imageLG, self.markerLG_static, coordinates, lg_marker, data[markercount]['Pinfarbe'])
          
        #Check which Icon the provided Adress has
        elif data[markercount]['Icon'] == 'Schule':       
          
          #Set Markers based on Excel
          self.markerS_static = None
          self.set_excel_markers(el, 'markerS', Variables.imageS, self.markerS_static, coordinates, s_marker, data[markercount]['Pinfarbe'])
          
        #Create Popup for Marker and add it to the Map
        popup = mapboxgl.Popup({'closeOnClick': False, 'offset': 25})
        popup.setHTML(data[markercount]['Informationen'])
        popup_static = mapboxgl.Popup({'closeOnClick': False, 'offset': 5, 'className': 'static-popup', 'closeButton': False, 'anchor': 'top'}).setText(data[markercount]['Informationen']).setLngLat(coords['features'][0]['geometry']['coordinates'])
        popup_static.addTo(self.mapbox)
        
        #Increase Markercount
        markercount += 1
      
      #Add Marker-Arrays to global Variable Marker
      Variables.marker.update({'cb_marker': cb_marker, 'kk_marker': kk_marker, 'h_marker': h_marker, 'kh_marker': kh_marker, 's_marker': s_marker, 'lg_marker': lg_marker})
      
  #####  Upload Functions   #####
  ###############################
  #####   Extra Functions   #####
    
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
    
      elif click.features[0].layer.source == 'gemeinden':
        print(click.features[0].properties)
        if hasattr(click.features[0].properties, 'GEN'):
          gm_name = click.features[0].properties.GEN
        else:
          gm_name = click.features[0].properties.name
        clicked_lngLat = dict(click.lngLat)
        popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<bGemeinde:</b> {gm_name}').addTo(self.mapbox)
        
      #Check which Layer is active
      elif click.features[0].layer.source == 'bezirke':
        
        #Create Popup and add it to the Map
        dt_name = click.features[0].properties.name
        dt_id = click.features[0].id
        clicked_lngLat = dict(click.lngLat)
        popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bezirk:</b> {dt_name}').addTo(self.mapbox)
  
    #This method is called when the User clicked on a Point of Interest on the Map   #Eventuell nicht mehr benötigt
    def poi(self, click):
    
      #Get and Set Variables
      info = dict(self.mapbox.style)
      
      #Check current Map-Style
      if (info['stylesheet']['metadata']['mapbox:origin'] == 'outdoors-v11'):
      
        #Get all Layers on the Map
        layers = self.mapbox.getStyle().layers
    
        #Get all Features (Point of Interest) of selected Layers on clicked Point
        features = self.mapbox.queryRenderedFeatures(click.point, {'layers': ['poi-label', 'transit-label', 'landuse', 'national-park']})
        
        #Check if no POI was clicked and no Layer is active
        if not features == [] and Variables.activeLayer == None and hasattr(features[0].properties, 'name') == True:
        
          #Create Popup on clicked Point with Information about the Point of Interest
          popup = mapboxgl.Popup().setLngLat(click.lngLat).setHTML('you clicked here: <br/>Name: ' + features[0].properties.name).addTo(self.mapbox)
      
      #Check current Map-Style
      elif Variables.activeLayer == None:
        
        #Send Notification to User
        Notification('Point of Interests are only available on the Outdoor-Map !', style='info').show()
    
    #This method is called when the Map is loading or changing his Style
    def place_layer(self, event):
      
      #Add 3D-Layer to the Map
      self.mapbox.addLayer({
        'id': 'add-3d-buildings',
        'source': 'composite',
        'source-layer': 'building',
        'filter': ['==', 'extrude', 'true'],
        'type': 'fill-extrusion',
        'minzoom': 15,
        'paint': {
          'fill-extrusion-color': '#aaa',
          'fill-extrusion-height': [
            'interpolate',
            ['linear'],
            ['zoom'],
            15,
            0,
            15.05,
            ['get', 'height']
          ],
          'fill-extrusion-base': [
            'interpolate',
            ['linear'],
            ['zoom'],
            15,
            0,
            15.05,
            ['get', 'min_height']
          ],
          'fill-extrusion-opacity': 0.6
        }
      })
      
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': 'bundeslaender',
        'type': 'fill',
        'source': {
            'type': 'geojson',
            'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json'
        },
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
      }) 
      
      #Add outlined Layer for Federal states
      self.mapbox.addLayer({
          'id': 'outlineBL',
          'type': 'line',
          'source': {
              'type': 'geojson',
              'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json'
          },
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 2
          }
      })
      
      #Add filled Layer for government districts
      self.mapbox.addLayer({
        'id': 'regierungsbezirke',
        'type': 'fill',
        'source': {
            'type': 'geojson',
            'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/3_regierungsbezirke/1_sehr_hoch.geo.json'
        },
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
      }) 
  
      #Add outlined Layer for government districts
      self.mapbox.addLayer({
          'id': 'outlineRB',
          'type': 'line',
          'source': {
              'type': 'geojson',
              'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/3_regierungsbezirke/1_sehr_hoch.geo.json'
          },
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 1
          }
      })
      
      #Add filled Layer for rural districts
      self.mapbox.addLayer({
        'id': 'landkreise',
        'type': 'fill',
        'source': {
            'type': 'geojson',
            'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/4_kreise/1_sehr_hoch.geo.json'
        },
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
      })
  
      #Add outlined Layer for rural districts
      self.mapbox.addLayer({
          'id': 'outlineLK',
          'type': 'line',
          'source': {
              'type': 'geojson',
              'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/4_kreise/1_sehr_hoch.geo.json'
          },
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      })
      
      #Add filled Layer for municipalities
      self.mapbox.addLayer({
        'id': 'gemeinden',
        'type': 'fill',
        'source': {
            'type': 'geojson',
            'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/gemeinden.geojson'
        },
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
      })
  
      #Add outlined Layer for municipalities
      self.mapbox.addLayer({
          'id': 'outlineGM',
          'type': 'line',
          'source': {
              'type': 'geojson',
              'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/gemeinden.geojson'
          },
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      })
      
      #Add filled Layer for berlin districts
      self.mapbox.addLayer({
        'id': 'bezirke',
        'type': 'fill',
        'source': {
            'type': 'geojson',
            'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/bln_hh_mun_dist.geojson'
        },
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
      })
  
      #Add outlined Layer for municipalities
      self.mapbox.addLayer({
          'id': 'outlineBK',
          'type': 'line',
          'source': {
              'type': 'geojson',
              'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/bln_hh_mun_dist.geojson'
          },
          'layout': {
              'visibility': 'none'
          },
          'paint': {
              'line-color': '#000',
              'line-width': 0.5
          }
      })
    
      #Check which Layer is active
      if Variables.activeLayer == 'bundeslaender':
    
        #Set Visibility to visible
        self.mapbox.setLayoutProperty('bundeslaender', 'visibility', 'visible')
        self.mapbox.setLayoutProperty('outlineBL', 'visibility', 'visible')
      
      #Check which Layer is active
      elif Variables.activeLayer == 'regierungsbezirke':
      
        #Set Visibility to visible
        self.mapbox.setLayoutProperty('regierungsbezirke', 'visibility', 'visible')
        self.mapbox.setLayoutProperty('outlineRB', 'visibility', 'visible')
      
      #Check which Layer is active
      elif Variables.activeLayer == 'landkreise':
        
        #Set Visibility to visible
        self.mapbox.setLayoutProperty('landkreise', 'visibility', 'visible')
        self.mapbox.setLayoutProperty('outlineLK', 'visibility', 'visible')
      
      #Check which Layer is active
      elif Variables.activeLayer == 'gemeinden':
        
        #Set Visibility to visible
        self.mapbox.setLayoutProperty('gemeinden', 'visibility', 'visible')
        self.mapbox.setLayoutProperty('outlineGM', 'visibility', 'visible')
        
      #Check which Layer is active
      elif Variables.activeLayer == 'ber_dist':
        
        #Set Visibility to visible
        self.mapbox.setLayoutProperty('ber_dist', 'visibility', 'visible')
        self.mapbox.setLayoutProperty('outlineBD', 'visibility', 'visible')
   
    #This method is called from the check_box_change-Functions to place Icons on Map  
    def create_icons(self, check_box, last_bbox, category, picture):

      # Check if Checkbox is checked
      if check_box == True:
      
          # Check if Checkbox for Iso-Layer' is checked
          if self.checkbox_poi_x_hfcig.checked == True:
      
              # Get Data of Iso-Layer
              iso = dict(self.mapbox.getSource('iso'))
      
              # Create empty Bounding Box
              bbox = [0, 0, 0, 0]
      
              # Check every element in Iso-Data
              for el in iso['_data']['features'][0]['geometry']['coordinates'][0]:
      
                  # Check if South-Coordinate of Element is lower then the lowest South-Coordinate of Bounding Box and BBox-Coordinate is not 0
                  if el[0] < bbox[1] or bbox[1] == 0:
            
                      # Set BBox-Coordinate to new Element-Coordinate
                      bbox[1] = el[0]
      
                  # Check if South-Coordinate of Element is higher then the highest South-Coordinate of Bounding Box and BBox-Coordinate is not 0
                  if el[0] > bbox[3] or bbox[3] == 0:
            
                      # Set BBox-Coordinate to new Element-Coordinate
                      bbox[3] = el[0]
      
                  # Check if North-Coordinate of Element is lower then the lowest North-Coordinate of Bounding Box and BBox-Coordinate is not 0
                  if el[1] < bbox[0] or bbox[0] == 0:
            
                      # Set BBox-Coordinate to new Element-Coordinate
                      bbox[0] = el[1]
      
                  # Check if North-Coordinate of Element is higher then the highest North-Coordinate of Bounding Box and BBox-Coordinate is not 0
                  if el[1] > bbox[2] or bbox[2] == 0:
            
                      # Set BBox-Coordinate to new Element-Coordinate
                      bbox[2] = el[1]
      
          # Do if Checkbox for Iso-Layer' is unchecked
          else:
      
              # Get visible Bounding Box of Map
              bbox = [(dict(self.mapbox.getBounds()['_sw']))['lat'], (dict(self.mapbox.getBounds()['_sw']))['lng'],
                      (dict(self.mapbox.getBounds()['_ne']))['lat'], (dict(self.mapbox.getBounds()['_ne']))['lng']]
      
          # Check if Bounding Box is not the same as least Request
          if not bbox == last_bbox:
      
              # Check if new Bounding Box is overlapping old Bounding Box
              if bbox[0] < last_bbox[0] or bbox[1] < last_bbox[1] or bbox[2] > last_bbox[2] or bbox[3] > last_bbox[3]:
      
                  # Get geojson of POIs inside Bounding Box
                  geojson = anvil.server.call('poi_data', category, bbox)
      
                  # Check if Elements are over 3000 for performance Reasons
                  if len(geojson) > 3000:
      
                      # Tell the User about to many Elements
                      alert('Zu große Ergebnismenge ! Näher ranzoomen !')
      
                  # Do if Elements are under 3000
                  else:
      
                      #Create empty Icons Array to save Elements
                      icons = []
      
                      # Loop through every Element in geojson
                      for ele in geojson:
      
                          # Get coordinates of current Icon
                          el_coords = ele['geometry']['coordinates']
      
                          # Create HTML Element for Icon
                          el = document.createElement('div')
                          el.className = 'marker'
                          el.style.width = '25px'
                          el.style.height = '25px'
                          el.style.backgroundSize = '100%'
                          el.style.backgroundrepeat = 'no-repeat'
      
                          # Create Icon
                          el.className = 'icon_doc'
                          el.style.backgroundImage = f'url({picture})'
      
                          # Get different Informations from geojson
                          city = ele['properties']['city']
                          suburb = ele['properties']['suburb']
                          street = ele['properties']['street']
                          housenumber = ele['properties']['housenumber']
                          postcode = ele['properties']['postcode']
                          phone = ele['properties']['phone']
                          website = ele['properties']['website']
                          healthcare = ele['properties']['healthcare']
                          name = ele['properties']['name']
                          opening_hours = ele['properties']['opening_hours']
                          wheelchair = ele['properties']['wheelchair']
                          o_id = ele['properties']['id']
                          fax = ele['properties']['fax']
                          email = ele['properties']['email']
                          speciality = ele['properties']['healthcare:speciality']
                          operator = ele['properties']['operator']
      
                          # Check if Category is Bus or Tram
                          if category == 'bus_stop' or category == 'tram_stop':
          
                              # Create Popup for Element
                              popup = mapboxgl.Popup({'offset': 25}).setHTML(
                                  f'<b>Name:</b>'
                                  f'<br>'
                                  f'&nbsp;&nbsp;{name}'
                              )
                             
                          # Check if Category is not Bus or Tram
                          else:
      
                              # Create Popup for Element
                              popup = mapboxgl.Popup({'offset': 25}).setHTML(
                                  f'<b>ID:</b> {o_id}'
                                  f'<br>'
                                  f'<b>Name:</b>'
                                  f'<br>'
                                  f'&nbsp;&nbsp;{name}'
                                  f'<br>'
                                  f'<b>Operator:</b>'
                                  f'<br>'
                                  f'&nbsp;&nbsp;{operator}'
                                  f'<br>'
                                  f'<b>Adresse:</b>'
                                  f'<br>'
                                  f'&nbsp;&nbsp;{street} {housenumber}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;{postcode}, {city} {suburb}'
                                  f'<br>'
                                  f'<b>Kontakt</b>'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Telefon: {phone}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Fax: {fax}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Email: {email}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Webseite:'
                                  f'<br>'
                                  f'&nbsp;&nbsp;&nbsp;&nbsp;{website}'
                                  f'<br>'
                                  f'<b>Infos</b>'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Kategorie: {healthcare}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Speciality: {speciality}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Öffnungszeiten:'
                                  f'<br>'
                                  f'&nbsp;&nbsp;&nbsp;&nbsp;{opening_hours}'
                                  f'<br>'
                                  f'&nbsp;&nbsp;Rollstuhlgerecht: {wheelchair}'
                              )
      
                          # Add Icon to the Map
                          newicon = mapboxgl.Marker(el).setLngLat(el_coords).setOffset([0, 0]).addTo(self.mapbox).setPopup(popup)
      
                          # Add current Element-Icon to Icon-Array
                          icons.append(newicon)
      
                  # Refresh global Variables
                  Variables.icons.update({f'{category}': icons})
                  last_bbox = bbox
                  Variables.last_cat = f'{category}'
      
              # Do if new Bounding Box is smaller or same than old Bounding Box
              else:
      
                  # Loop through every Element in global Icon-Elements
                  for el in Variables.icons[f'{category}']:
      
                      # Get coordinates of current Icon
                      el_coords = dict(el['_lngLat'])
      
                      # Check if Icon is inside visible Bounding Box
                      if bbox[0] < el_coords['lat'] < bbox[2] and bbox[1] < el_coords['lng'] < bbox[3]:
                          # Add Element to Map
                          el.addTo(self.mapbox)
      
                  # Change last Category
                  Variables.last_cat = f'{category}'
      
          # Do if Bounding Box is the same as least Request
          else:
      
              # Loop through every Element in global Icon-Elements
              for el in Variables.icons[f'{category}']:
                  # Add Element to Map
                  el.addTo(self.mapbox)
      
              # Change last Category
              Variables.last_cat = f'{category}'
      
      # Do if Checkbox is unchecked
      else:
      
          # Loop through every Element in global Icon-Elements
          for el in Variables.icons[f'{category}']:
              # Remove Element from Map
              el.remove()
      
      # Send Value back to origin Function
      return (last_bbox)
    
    #This method is called from different Marker-Checkboxes to hide/show there markers
    def show_hide_marker(self, check_box, marker_id):
        
      #Check if Check Box is checked and id exist 
      if check_box == True and marker_id in Variables.marker:
          
        #Show Marker and Icon
        for el in Variables.marker[marker_id]:
          
          #Add Marker to Map
          el.addTo(self.mapbox)
         
      #Check if Check Box is unchecked and id exist  
      elif check_box == False and marker_id in Variables.marker:
          
        #Hide Marker and Icon
        for el in Variables.marker[marker_id]:
          
          #Remove Marker from Map
          el.remove()
    
    #This method is called when the active Layer is changed
    def change_active_Layer(self, layer, inactive_layer, visibility, other_checkbox):
      
      # Check if Layer is visible or not
      for el in layer:
      
          # Hide active Layer
          self.mapbox.setLayoutProperty(el, 'visibility', visibility)
      
          #Do for every inactive Layer
          for el in inactive_layer:
      
              #Do for every Sub-Layer of inactive Layer
              for ele in el:
      
                  #Set visiblity to 'not visible'
                  self.mapbox.setLayoutProperty(ele, 'visibility', 'none')
      
      #Do for every Checkbox
      for el in other_checkbox:
      
          # Uncheck Check Box from other Layers
          el.checked = False
      
      #Check visibility
      if visibility == 'visible':
      
          # Set active Layer to Bundesländer
          Variables.activeLayer = layer[0]
          
      else:
        
          # Set active Layer to Bundesländer
          Variables.activeLayer = None
      
    #This method is called from different Menu-Collapsables
    def icon_change(self, container, container_state, icon, icon_icon):

      print(container)
      print(container.visible)
      
      #Change State of Button and Image of Icon
      container.visible = container_state
      icon.icon = icon_icon
    
    #This method is called from the file uploader to set Markers based on Excel-Data
    def set_excel_markers(self, el, el_className, el_image, marker_cat, coords, marker_list, color):
      
      # Create Icon
      el.className = el_className
      el.style.backgroundImage = el_image
      
      # Check wich Markercolor the provided Adress has and color the Marker
      if color == 'Rot':
          marker_cat = mapboxgl.Marker({'color': '#FF0000', 'draggable': False})
      elif color == 'Gelb':
          marker_cat = mapboxgl.Marker({'color': '#FFFF00', 'draggable': False})
      elif color == 'Grün':
          marker_cat = mapboxgl.Marker({'color': '#92D050', 'draggable': False})
      elif color == 'Blau':
          marker_cat = mapboxgl.Marker({'color': '#00B0F0', 'draggable': False})
      elif color == 'Lila':
          marker_cat = mapboxgl.Marker({'color': '#D427F1', 'draggable': False})
      elif color == 'Orange':
          marker_cat = mapboxgl.Marker({'color': '#FFC000', 'draggable': False})
      elif color == 'Dunkelgrün':
          marker_cat = mapboxgl.Marker({'color': '#00B050', 'draggable': False})
      
      # Add Marker to the Map
      newmarker = marker_cat.setLngLat(coords).addTo(self.mapbox)
      
      # Add Icon to the Map
      newicon = mapboxgl.Marker(el).setLngLat(coords).setOffset([0, -22]).addTo(self.mapbox)
      
      # Add Marker and Icon to Marker-Array
      marker_list.append(newmarker)
      marker_list.append(newicon)
      
    #This method is called when the Mouse is moved inside or out of an active Layer
    def change_hover_state(self, mouse):
      
      # Check if Layer is already hovered
      if Variables.hoveredStateId != None:
      
          # Check if active Layer is Bundesländer
          if Variables.activeLayer == 'bundeslaender':
      
              # Change hover-State to False and set global-variable 'hoveredStateId' to None
              self.mapbox.setFeatureState({'source': 'bundeslaender', 'id': Variables.hoveredStateId}, {'hover': False})
              Variables.hoveredStateId = None
      
          # Check if active Layer is Regierungsbezirke
          elif Variables.activeLayer == 'regierungsbezirke':
      
              # Change hover-State to False and set global-variable 'hoveredStateId' to None
              self.mapbox.setFeatureState({'source': 'regierungsbezirke', 'id': Variables.hoveredStateId}, {'hover': False})
              Variables.hoveredStateId = None
      
              # Check if active Layer is Landkreise
          elif Variables.activeLayer == 'landkreise':
      
              # Change hover-State to False and set global-variable 'hoveredStateId' to None
              self.mapbox.setFeatureState({'source': 'landkreise', 'id': Variables.hoveredStateId}, {'hover': False})
              Variables.hoveredStateId = None
      
          # Check if active Layer is Gemeinden
          elif Variables.activeLayer == 'gemeinden':
      
              # Change hover-State to False and set global-variable 'hoveredStateId' to None
              self.mapbox.setFeatureState({'source': 'gemeinden', 'id': Variables.hoveredStateId}, {'hover': False})
              Variables.hoveredStateId = None
            
          # Check if active Layer is Gemeinden
          elif Variables.activeLayer == 'bezirke':
      
              # Change hover-State to False and set global-variable 'hoveredStateId' to None
              self.mapbox.setFeatureState({'source': 'bezirke', 'id': Variables.hoveredStateId}, {'hover': False})
              Variables.hoveredStateId = None
      
      #Check if Mouse is moved inside Layer or out of Layer
      if hasattr(mouse, 'features'):
        
        # Check if Mouse was moved inside active Map-Layer
        if len(mouse.features) > 0:
        
            # Change global hoveredStateID to new active Layer-id
            Variables.hoveredStateId = mouse.features[0].id
        
            # Check if active Layer is Bundesländer
            if Variables.activeLayer == 'bundeslaender':
        
                # Change hover-State to True
                self.mapbox.setFeatureState({'source': 'bundeslaender', 'id': Variables.hoveredStateId}, {'hover': True})
        
            # Check if active Layer is Regierungsbezirke
            elif Variables.activeLayer == 'regierungsbezirke':
        
                # Change hover-State to True
                self.mapbox.setFeatureState({'source': 'regierungsbezirke', 'id': Variables.hoveredStateId}, {'hover': True})
        
            # Check if active Layer is Landkreise
            elif Variables.activeLayer == 'landkreise':
        
                # Change hover-State to True
                self.mapbox.setFeatureState({'source': 'landkreise', 'id': Variables.hoveredStateId}, {'hover': True})
        
            # Check if active Layer is Gemeinden
            elif Variables.activeLayer == 'gemeinden':
        
                # Change hover-State to True
                self.mapbox.setFeatureState({'source': 'gemeinden', 'id': Variables.hoveredStateId}, {'hover': True})
            
            # Check if active Layer is Gemeinden
            elif Variables.activeLayer == 'bezirke':
        
                # Change hover-State to True
                self.mapbox.setFeatureState({'source': 'bezirke', 'id': Variables.hoveredStateId}, {'hover': True})
    
    def build_request_string(self, marker):
      
      #Create basic request String
      request_string = f"https://api.mapbox.com/geocoding/v5/mapbox.places/"
      
      #Create and Send Request String based on given Marker
      request_string += str(marker['Straße']).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
      request_string += str(marker['Hausnummer']).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
      request_string += str(marker['Bezirk']).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
      request_string += str(marker['Stadt']).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
      request_string += str(marker['Postleitzahl'])
      
      return (request_string)
    
  #####   Extra Functions   #####