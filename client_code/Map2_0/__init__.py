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
import anvil.media
import plotly.graph_objects as go

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
#     self.token = "pk.eyJ1IjoiYnJvb2tlbXllcnMiLCJhIjoiY2tsamtiZ3l0MW55YjJvb2lsbmNxaWo0dCJ9.9iOO0aFkAy0TAP_qjtSE-A"
    self.token = 'pk.eyJ1Ijoic2hpbnlrYW1wZmtldWxlIiwiYSI6ImNreWluYm5jMTBrYXcydnFvbmt3a3RiMG8ifQ.UEt90g8gVzPhsJof0znguA'

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
    self.mapbox.on('mousemove', 'netherlands', self.change_hover_state)
    self.mapbox.on('mouseleave', 'netherlands', self.change_hover_state)
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
      self.change_active_Layer(['bundeslaender', 'outlineBL'], [['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'visible', [self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_dt, self.check_box_nl])
    
    #Check state of visibility
    elif visibility == 'visible':
      
      #Change Active Layer to hide
      self.change_active_Layer(['bundeslaender', 'outlineBL'], [['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'none', [self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_dt, self.check_box_nl])
  
  #This method is called when the Check Box for Regierungsbezirke-Layer is checked or unchecked
  def check_box_rb_change(self, **event_args):
      
    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('regierungsbezirke', 'visibility')
      
    #Check state of visibility
    if visibility == 'none':
      
      #Change Active Layer to show
      self.change_active_Layer(['regierungsbezirke', 'outlineRB'], [['bundeslaender', 'outlineBL'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'visible', [self.check_box_bl, self.check_box_lk, self.check_box_gm, self.check_box_dt, self.check_box_nl])
    
    #Check state of visibility
    elif visibility == 'visible':
      
      #Change Active Layer to hide
      self.change_active_Layer(['regierungsbezirke', 'outlineRB'], [['bundeslaender', 'outlineBL'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'none', [self.check_box_bl, self.check_box_lk, self.check_box_gm, self.check_box_dt, self.check_box_nl])
  
  #This method is called when the Check Box for Landkreise-Layer is checked or unchecked
  def check_box_lk_change(self, **event_args):

    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('landkreise', 'visibility')
      
    #Check state of visibility
    if visibility == 'none':
      
      #Change Active Layer to show
      self.change_active_Layer(['landkreise', 'outlineLK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_gm, self.check_box_dt, self.check_box_nl])
    
    #Check state of visibility
    elif visibility == 'visible':
    
      #Change Active Layer to hide
      self.change_active_Layer(['landkreise', 'outlineLK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_gm, self.check_box_dt, self.check_box_nl])

  #This method is called when the Check Box for Gemeinden-Layer is checked or unchecked
  def check_box_gm_change(self, **event_args):
      
    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('gemeinden', 'visibility')
      
    #Check state of visibility
    if visibility == 'none':
      
      #Change Active Layer to show
      self.change_active_Layer(['gemeinden', 'outlineGM'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_dt, self.check_box_nl])
      
    #Check state of visibility
    elif visibility == 'visible':
      
      #Change Active Layer to hide
      self.change_active_Layer(['gemeinden', 'outlineGM'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['bezirke', 'outlineBK'], ['netherlands', 'outlineNL']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_dt, self.check_box_nl])
    
  #This method is called when the Check Box for Gemeinden-Layer is checked or unchecked
  def check_box_dt_change(self, **event_args):

    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('bezirke', 'visibility')
    
    #Check state of visibility
    if visibility == 'none':
    
      #Change Active Layer to show
      self.change_active_Layer(['bezirke', 'outlineBK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['netherlands', 'outlineNL']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_nl])
    
    #Check state of visibility
    elif visibility == 'visible':
    
      #Change Active Layer to hide
      self.change_active_Layer(['bezirke', 'outlineBK'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['netherlands', 'outlineNL']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_nl])
    
  #This method is called when the Check Box for Niederlande-Layer is checked or unchecked  
  def check_box_nl_change(self, **event_args):

    #Get Visibility of Layer
    visibility = self.mapbox.getLayoutProperty('netherlands', 'visibility')
    
    #Check state of visibility
    if visibility == 'none':
    
      #Change Active Layer to show
      self.change_active_Layer(['netherlands', 'outlineNL'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'visible', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_dt])
    
    #Check state of visibility
    elif visibility == 'visible':
    
      #Change Active Layer to hide
      self.change_active_Layer(['netherlands', 'outlineNL'], [['bundeslaender', 'outlineBL'], ['regierungsbezirke', 'outlineRB'], ['landkreise', 'outlineLK'], ['gemeinden', 'outlineGM'], ['bezirke', 'outlineBK']], 'none', [self.check_box_bl, self.check_box_rb, self.check_box_lk, self.check_box_gm, self.check_box_dt])
    
  #This method is called when the Check Box for POI 'doctors' is checked or unchecked
  def check_box_doc_change(self, **event_args):
  
    #Call create_icons-Function to set the Icons on Map and save last BBox of doctors
    Variables.last_bbox_doc = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, 'doctors', Variables.icon_doctors)
  
  #This method is called when the Check Box for POI 'dentist' is checked or unchecked
  def check_box_den_change(self, **event_args):
  
    #Call create_icons-Function to set the Icons on Map and save last BBox of dentist
    Variables.last_bbox_den = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, 'dentist', Variables.icon_dentist)
  
  #This method is called when the Check Box for POI 'clinic' is checked or unchecked
  def check_box_cli_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of clinics
    Variables.last_bbox_cli = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, 'clinic', Variables.icon_clinics)

  #This method is called when the Check Box for POI 'hospital' is checked or unchecked
  def check_box_hos_change(self, **event_args):
  
    #Call create_icons-Function to set the Icons on Map and save last BBox of hospital
    Variables.last_bbox_hos = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, 'hospital', Variables.icon_hospital)

  #This method is called when the Check Box for POI 'nursing_home' is checked or unchecked
  def check_box_nur_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of nursing_home
    Variables.last_bbox_nur = self.create_icons(self.check_box_nur.checked, Variables.last_bbox_nur, 'nursing_home', Variables.icon_nursing)
  
  #This method is called when the Check Box for POI 'pharmacy' is checked or unchecked
  def check_box_pha_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of pharmacy
    Variables.last_bbox_pha = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, 'pharmacy', Variables.icon_pharmacy)

  #This method is called when the Check Box for POI 'social_facility' is checked or unchecked
  def check_box_soc_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of social_facility
    Variables.last_bbox_soc = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, 'social_facility', Variables.icon_social)

  #This method is called when the Check Box for POI 'doctors' is checked or unchecked
  def check_box_vet_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of veterinary
    Variables.last_bbox_vet = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, 'veterinary', Variables.icon_veterinary)
      
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
    Variables.last_bbox_bus = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, 'bus_stop', Variables.icon_bus)
  
  #This method is called when the Check Box for POI 'tram' is checked or unchecked
  def check_box_tra_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of tram_stop
    Variables.last_bbox_tra = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, 'tram_stop', Variables.icon_tram)
   
  #This method is called when the Check Box for POI 'supermarket' is checked or unchecked
  def check_box_sma_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of supermarket
    Variables.last_bbox_sma = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, 'supermarket', Variables.icon_supermarket)

  #This method is called when the Check Box for POI 'restaurant' is checked or unchecked
  def check_box_res_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of restaurant
    Variables.last_bbox_res = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, 'restaurant', Variables.icon_restaurant)

  #This method is called when the Check Box for POI 'cafe' is checked or unchecked  
  def check_box_cafe_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of cafe
    Variables.last_bbox_caf = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, 'cafe', Variables.icon_cafe)

  #This method is called when the Check Box for POI 'university' is checked or unchecked  
  def check_box_uni_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of university
    Variables.last_bbox_uni = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, 'university', Variables.icon_university)
   
  #This method is called when the Check Box for POI 'Pflege DB' is checked or unchecked
  def pdb_data_cb_change(self, **event_args):
    
    #Call create_icons-Function to set the Icons on Map and save last BBox of Pflege DB
    Variables.last_bbox_pdb = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_pdb, 'pflegeDB', Variables.icon_pflegeDB)
          
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
      self.icon_change(self.poi_categories_healthcare_container, True, self.button_healthcare, 'fa:angle-down')
  
  #This method is called when the Miscelanious-Button is clicked
  def misc_button_click(self, **event_args):
    
    #Check if Checkbox-Panel is visible or not
    if self.Misc_Container.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.icon_change(self.Misc_Container, False, self.misc_button, 'fa:angle-right')
      
    else:
    
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.icon_change(self.Misc_Container, True, self.misc_button, 'fa:angle-down')

  #This method is called when the ÖPNV-Button is clicked
  def opnv_button_click(self, **event_args):
    
    #Check if Checkbox-Panel is visible or not
    if self.opnv_container.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.icon_change(self.opnv_container, False, self.opnv_button, 'fa:angle-right')
      
    else:
    
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.icon_change(self.opnv_container, True, self.opnv_button, 'fa:angle-down')
      
  def dist_layer_click(self, **event_args):

    #Check if Checkbox-Panel is visible or not
    if self.dist_container.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.icon_change(self.dist_container, False, self.dist_layer, 'fa:angle-right')
      
    else:
    
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.icon_change(self.dist_container, True, self.dist_layer, 'fa:angle-down')
      
  def map_styles_click(self, **event_args):
    
    #Check if Checkbox-Panel is visible or not
    if self.checkbox_map_style.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.icon_change(self.checkbox_map_style, False, self.map_styles, 'fa:angle-right')
      
    else:
    
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.icon_change(self.checkbox_map_style, True, self.map_styles, 'fa:angle-down')

  def poi_categories_click(self, **event_args):
    
    #Check if Checkbox-Panel is visible or not
    if self.poi_category.visible == True:
    
      #Set Checkbox-Panel to invisible and change Arrow-Icon
      self.icon_change(self.poi_category, False, self.poi_category, 'fa:angle-right')
      
    else:
    
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.icon_change(self.poi_category, True, self.poi_category, 'fa:angle-down')
      
  def exp_care_db_click(self, **event_args):
    
    index = 1
    counter = 0
    
    popup_text = '<html><head><title>Competitor Analysis</title><style>table {border-collapse: collapse; width: 100%} td {border-bottom: 1px solid black; text-align: center; min-width: 80px} th {background-color: #BFAD75; text-align: center; min-width: 80px; height: 30px}</style></head><body>'
    popup_text += f'<table><tr><th>No.</th><th>Name</th><th>No. of beds</th><th>single rooms</th><th>double rooms</th><th>Patients</th><th>occupancy</th><th>year of construction</th><th>Status</th><th>Operator</th><th>Invest costs per day</th><th>MDK grade</th></tr>'
    
    for el in Variables.pflegeDBEntries:
      
      lng1 = '%.6f' % float(el[46])
      lat1 = '%.6f' % float(el[45])
      
      for ele in Variables.activeIcons['pflegeDB']:
        
        lng = '%.6f' % ele['_lngLat']['lng']
        lat = '%.6f' % ele['_lngLat']['lat']
        
        if lng1 == lng and lat1 == lat:
          
          counter += 1
      
          if el[27] == '-':
            
            x = 0
            
          else:
            
            x = int(el[27])
            
          if el[28] == '-':
            
            y = 0
            
          else:
            
            y = int(el[28])
          
          if not x == 0 and not y == 0:
            
            occupancy_raw = round((x * 100) / y)
            occupancy = f'{occupancy_raw} %'
            
          else:
            
            occupancy = '-'
            
          if not el[38] == '-':
            
            invest = f'{el[38]} €'
            
          else:
            
            invest = el[38]
          
          popup_text += f'<tr><td>{index}</td><td>{el[5]}</td><td>{el[28]}</td><td>{el[31]}</td><td>{el[32]}</td><td>{el[27]}</td><td>{occupancy}</td><td>{el[33]}</td><td>{el[4]}</td><td>{el[6]}</td><td>{invest}</td><td>{el[26]}</td></tr>'
          index += 1
          
          break
          
    popup_text += '</table></body></html>'
  
    anvil.js.call('open_tab', popup_text)
    
  def Summary_click(self, **event_args):
    
    lngLat = [(dict(self.marker['_lngLat'])['lng']), (dict(self.marker['_lngLat'])['lat'])]
    
    string = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{lngLat[0]},{lngLat[1]}.json?access_token={self.token}'
    
    #Get Data from request
    response_data = anvil.http.request(string,json=True)
    
    marker_context = response_data['features'][0]['context']
    
    zipcode = 'n.a.'
    district = 'n.a.'
    city = 'n.a.'
    federal_state = 'n.a.'
    
    for el in marker_context:
      
      if 'postcode' in el['id'] :
        
        zipcode = el['text']
        
      elif 'locality' in el['id']:
        
        district = el['text']
        
      elif 'place' in el['id']:
        
        city = el['text']
        
      elif 'region' in el['id']:
        
        federal_state = el['text']
        
    if federal_state == 'n.a.':
      
      federal_state = city
      
    if district == 'n.a.':
      
      district = city

    time = self.time_dropdown.selected_value
    
    if time == '-1':
      
      time = '20'
    
    movement = self.profile_dropdown.selected_value.lower()
    
    data = anvil.server.call('get_countie_data_from_DB', city, federal_state)
    population = 0
    
    countie = data[0][1].split(',')
    
    peopleu75 = int((float(data[0][19]) * float(data[0][17])) / 100)
    peopleo75 = int((float(data[0][19]) * float(data[0][18])) / 100)
    
    CareData = anvil.server.call('get_federalstate_data', federal_state, data[0][0])
    
    sum = 0
    
    for el in CareData:
    
        if not el[27] == '-':
    
            sum += int(el[27])
    
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
        
    dataDB = anvil.server.call('get_iso_data', bbox)
    
    inpatients = 0
    beds_active = 0
    beds_planned = 0
    beds_construct = 0
    nursingHomes_active = 0
    nursingHomes_planned = 0
    nursingHomes_construct = 0
    patients = 0
    investCost = []
    operator = []
    beds = []
    year = []
    operator_public = []
    operator_nonProfit = []
    operator_private = []
    
    for el in dataDB:
      
      bedsEL = 0
      
      if not el[27] == '-':
        
        inpatients += int(el[27])
      
      if el[4] == 'aktiv':
      
        nursingHomes_active += 1
        
        if not el[28] == '-':
          
          beds_active += int(el[28])
          bedsEL += int(el[28])
          
        if not el[29] == '-':
          
          beds_active += int(el[29])
          bedsEL += int(el[29])
        
        if not el[30] == '-':
          
          beds_active += int(el[30])
          bedsEL += int(el[30])
          
        beds.append(bedsEL)
        
      elif el[4] == 'in Planung':
        
        nursingHomes_planned += 1
        
        if not el[31] == '-':
          
          beds_planned += int(el[31])
          
        if not el[32] == '-':
          
          beds_planned += (int(el[32]) * 2)
        
      elif el[4] == 'im Bau':
        
        nursingHomes_construct += 1
        
        if not el[31] == '-':
          
          beds_construct += int(el[31])
          
        if not el[32] == '-':
          
          beds_construct += (int(el[32]) * 2)
      
      if not el[38] == '-':
        
        investCost.append(float(el[38]))
        
      if not el[6] == '-':
        
        if el[9] == 'privat':
          
          if not el[6] in operator_private:
          
            operator_private.append(el[6])
          
        elif el[9] == 'gemeinnützig':
          
          if not el[6] in operator_nonProfit:
          
            operator_nonProfit.append(el[6])
          
        elif el[9] == 'kommunal':
          
          if not el[6] in operator_public:
          
            operator_public.append(el[6])
        
        if not el[6] in operator:
          
          operator.append(el[6])
          
      if not el[33] == '-':
        
        year.append(int(el[33]))
    
    investMedian = anvil.server.call('get_median', investCost)
    investMedian = "{:.2f}".format(investMedian)
    bedsMedian = anvil.server.call('get_median', beds)
    yearMedian = round(anvil.server.call('get_median', year))
    op_private_percent = round((len(operator_private) * 100) / len(operator))
    op_nonProfit_percent = round((len(operator_nonProfit) * 100) / len(operator))
    op_public_percent = round((len(operator_public) * 100) / len(operator))
    
    occupancy_raw = round((inpatients * 100) / beds_active)
        
    beds_adjusted = beds_active + beds_construct + beds_planned
    
    values = [{'topic': '% Public operators', 'value': len(operator_public)}, {'topic': '% Non-profit operators', 'value': len(operator_nonProfit)}, {'topic': '% Private operators', 'value': len(operator_private)}]
    
    anvil.server.call('create_pieChart', values)
    
    barValues = [{'topic': 'Number of inpatients', 'value': inpatients}, {'topic': 'Beds', 'value': beds_active}, {'topic': 'Number of inpatients forecast 2030', 'value': (inpatients + 300)}, {'topic': 'Adjusted number of beds (incl. beds in planning and under construction)', 'value': beds_adjusted}]
    
    anvil.server.call('create_barChart', barValues)
    
    donutPicture = app_tables.pictures.get(id=0)
    donutPic = donutPicture['pic']
    
    barPicture = app_tables.pictures.get(id=1)
    barPic = barPicture['pic']
    
    logoPicture = app_tables.pictures.get(id=2)
    logoPic = logoPicture['pic']
    
    lng = self.marker['_lngLat']['lng']
    lat = self.marker['_lngLat']['lat']
    
    mapRequest = f"""https://api.mapbox.com/styles/v1/shinykampfkeule/ckyimpqlg92o315qqw4ubxk6v/static/pin-s-c+BFB273({lng},{lat})%5D%7D)/[5.98865807458, 47.3024876979, 15.0169958839, 54.983104153]/800x800?access_token={self.token}"""
    
    mapImage = anvil.http.request(mapRequest,json=False)
    
    app_tables.pictures.add_row(id=3, pic=mapImage)
    
    mapPicture = app_tables.pictures.get(id=3)
    mapPic = mapPicture['pic']
    
    sendData = [mapRequest, zipcode, city, district, federal_state, time, movement, countie[0], data[0][19], peopleu75, peopleo75, sum, inpatients, beds_active, nursingHomes_active, nursingHomes_planned, nursingHomes_construct, beds_planned, beds_adjusted, occupancy_raw, investMedian, len(operator), bedsMedian, yearMedian, op_public_percent, op_nonProfit_percent, op_private_percent] 
    
    anvil.server.call('write_PDF_File', sendData)
    
    anvil.js.call('open_tab', response)
    
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
                                   })
      
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
      
      if hasattr(click.features[0].properties, 'GEN'):
        
        gm_name = click.features[0].properties.GEN
        
      else:
        
        gm_name = click.features[0].properties.name
      
      key = click.features[0].properties.AGS
      data = anvil.server.call('get_Data_from_Database', key)
    
      popup_text = f'<button type="button" onClick="hide_mun_info()">&#10006;</button><br><br><h3>Municipality: {gm_name}</h3><b>ID:</b> {key}<br><b>Area:</b> {"{:.2f}".format(data[0][9])}km&sup2;<br><br><b>Population:</b> {data[0][10]}<br><b>per km&sup2:</b> {data[0][13]}<br><br><table><tr><th class="firstCol">Gender</th><th>Overall</th><th>Under 3</th><th>3 to <br>Under 6</th><th>6 to <br>Under 10</th><th>10 to Under 15</th><th>15 to Under 18</th><th>18 to Under 20</th><th>20 to Under 25</th><th>25 to Under 30</th><th>30 to Under 35</th><th>35 to Under 40</th><th>40 to Under 45</th><th>45 to Under 50</th><th>50 to Under 55</th><th>55 to Under 60</th><th>60 to Under 65</th><th>65 to Under 75</th><th>75 and older</th></tr><tr><th class="firstCol">Overall</th><td>100%</td><td>{"{:.1f}".format(data[1][2])}%</td><td>{"{:.1f}".format(data[1][3])}%</td><td>{"{:.1f}".format(data[1][4])}%</td><td>{"{:.1f}".format(data[1][5])}%</td><td>{"{:.1f}".format(data[1][6])}%</td><td>{"{:.1f}".format(data[1][7])}%</td><td>{"{:.1f}".format(data[1][8])}%</td><td>{"{:.1f}".format(data[1][9])}%</td><td>{"{:.1f}".format(data[1][10])}%</td><td>{"{:.1f}".format(data[1][11])}%</td><td>{"{:.1f}".format(data[1][12])}%</td><td>{"{:.1f}".format(data[1][13])}%</td><td>{"{:.1f}".format(data[1][14])}%</td><td>{"{:.1f}".format(data[1][15])}%</td><td>{"{:.1f}".format(data[1][16])}%</td><td>{"{:.1f}".format(data[1][17])}%</td><td>{"{:.1f}".format(data[1][18])}%</td></tr><tr><th class="firstCol">Male</th><td>{"{:.1f}".format(data[1][37])}%</td><td>{"{:.1f}".format(data[1][20])}%</td><td>{"{:.1f}".format(data[1][21])}%</td><td>{"{:.1f}".format(data[1][22])}%</td><td>{"{:.1f}".format(data[1][23])}%</td><td>{data[1][24]}%</td><td>{"{:.1f}".format(data[1][25])}%</td><td>{"{:.1f}".format(data[1][26])}%</td><td>{"{:.1f}".format(data[1][27])}%</td><td>{"{:.1f}".format(data[1][28])}%</td><td>{"{:.1f}".format(data[1][29])}%</td><td>{"{:.1f}".format(data[1][30])}%</td><td>{"{:.1f}".format(data[1][31])}%</td><td>{"{:.1f}".format(data[1][32])}%</td><td>{"{:.1f}".format(data[1][33])}%</td><td>{"{:.1f}".format(data[1][34])}%</td><td>{"{:.1f}".format(data[1][35])}%</td><td>{"{:.1f}".format(data[1][36])}%</td></tr><tr><th class="firstCol">Female</th><td>{"{:.1f}".format(data[1][55])}%</td><td>{"{:.1f}".format(data[1][38])}%</td><td>{"{:.1f}".format(data[1][39])}%</td><td>{"{:.1f}".format(data[1][40])}%</td><td>{"{:.1f}".format(data[1][41])}%</td><td>{"{:.1f}".format(data[1][42])}%</td><td>{data[1][43]}%</td><td>{"{:.1f}".format(data[1][44])}%</td><td>{"{:.1f}".format(data[1][45])}%</td><td>{"{:.1f}".format(data[1][46])}%</td> <td>{"{:.1f}".format(data[1][47])}%</td><td>{"{:.1f}".format(data[1][48])}%</td><td>{"{:.1f}".format(data[1][49])}%</td><td>{"{:.1f}".format(data[1][50])}%</td><td>{"{:.1f}".format(data[1][51])}%</td><td>{"{:.1f}".format(data[1][52])}%</td><td>{"{:.1f}".format(data[1][53])}%</td><td>{"{:.1f}".format(data[1][54])}%</td></tr></table><br><br><br><b>Grad der Verstädterung:</b> {data[0][18]}'
      
      anvil.js.call('show_mun_info', popup_text)
      
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
        popup = mapboxgl.Popup().setLngLat(click.lngLat).setHTML('Name: ' + features[0].properties.name).addTo(self.mapbox)
    
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
        'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/municipalities.geojson'
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
          'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/municipalities.geojson'

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
    
    #Add filled Layer for Netherlands
    self.mapbox.addLayer({
      'id': 'netherlands',
      'type': 'fill',
      'source': {
        'type': 'geojson',
        'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/netherlands.geojson'
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

    #Add outlined Layer for Netherlands
    self.mapbox.addLayer({
        'id': 'outlineNL',
        'type': 'line',
        'source': {
          'type': 'geojson',
          'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/netherlands.geojson'
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
    
          # Check if Category is PflegeDB
          if category == 'pflegeDB':
    
            geojson = anvil.server.call('get_Care_DB_Data', bbox)
            Variables.pflegeDBEntries = geojson
    
          else:
    
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
    
              # Create HTML Element for Icon
              el = document.createElement('div')
              el.className = 'marker'
              el.style.width = '25px'
              el.style.height = '25px'
              el.style.backgroundSize = '100%'
              el.style.backgroundrepeat = 'no-repeat'
    
              # Create Icon
              el.style.backgroundImage = f'url({picture})'
    
              # Check if Category is not PflegeDB
              if not category == 'pflegeDB':
    
                # Get coordinates of current Icon
                el_coords = ele['geometry']['coordinates']
    
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
                
              # Check if Category is PflegeDB
              elif category == 'pflegeDB':
    
                el_coords = [ele[46], ele[45]]
    
                # Create Popup for Element
                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f'<b>PM ID: </b> {ele[0]}'
                  '<br>'
                  f'<b>Träger ID: </b> {ele[1]}'
                  '<br>'
                  f'<b>IK_Nummer: </b> {ele[2]}'
                  '<br>'
                  '<br>'
                  f'<b>Sektor: </b> {ele[3]}'
                  '<br>'
                  f'<b>Art: </b> {ele[9]}'
                  '<br>'
                  f'<b>Spezialisierung: </b> {ele[44]}'
                  '<br>'
                  f'<b>Status: </b> {ele[4]}'
                  '<br>'
                  f'<b>Baujahr: </b> {ele[33]}'
                  '<br>'
                  f'<b>Modernisierungsjahr: </b> {ele[34]}'
                  '<br>'
                  '<br>'
                  f'<b>Name: </b> {ele[5]}'
                  '<br>'
                  '<br>'
                  f'<b>Betreiber: </b> {ele[6]}'
                  '<br>'
                  f'<b>Tochterfirma 1: </b> {ele[7]}'
                  '<br>'
                  f'<b>Tochterfirma 2: </b> {ele[8]}'
                  '<br>'
                  '<br>'
                  f'<b>Straße: </b> {ele[10]}'
                  '<br>'
                  f'<b>Postleitzahl: </b> {ele[11]}'
                  '<br>'
                  f'<b>Ort: </b> {ele[12]}'
                  '<br>'
                  f'<b>Bundesland: </b> {ele[13]}'
                  '<br>'
                  f'<b>Gemeindeschlüssel: </b> {ele[14]}'
                  '<br>'
                  '<br>'
                  f'<b>Telefon: </b> {ele[15]}'
                  '<br>'
                  f'<b>Fax: </b> {ele[16]}'
                  '<br>'
                  f'<b>E-Mail: </b> {ele[17]}'
                  '<br>'
                  f'<b>Webseite: </b> {ele[18]}'
                  '<br>'
                  f'<b>Domain: </b> {ele[19]}'
                  '<br>'
                  '<br>'
                  f'<b>MDK Datum: </b> {ele[20]}'
                  '<br>'
                  f'<b>Pflege und medizinische Versorgung: </b> {ele[21]}'
                  '<br>'
                  f'<b>Umgang mit demenzkranken Bewohnern: </b> {ele[22]}'
                  '<br>'
                  f'<b>Soziale Betreuung und Alltagsgestaltung: </b> {ele[23]}'
                  '<br>'
                  f'<b>Wohnen, Verpflegung, Hauswirtschaft und Hygiene: </b> {ele[24]}'
                  '<br>'
                  f'<b>Befragung der Bewohner: </b> {ele[25]}'
                  '<br>'
                  f'<b>MDK Note: </b> {ele[26]}'
                  '<br>'
                  '<br>'
                  f'<b>Anzahl versorgte Patienten: </b> {ele[27]}'
                  '<br>'
                  f'<b>Platzzahl vollständige Pflege: </b> {ele[28]}'
                  '<br>'
                  f'<b>Platzzahl Kurzzeitpflege: </b> {ele[29]}'
                  '<br>'
                  f'<b>Platzzahl Nachtpflege: </b> {ele[30]}'
                  '<br>'
                  f'<b>Einzelzimmer: </b> {ele[31]}'
                  '<br>'
                  f'<b>Doppelzimmer: </b> {ele[32]}'
                  '<br>'
                  '<br>'
                  f'<b>Ausbildungsumlage: </b> {ele[35]}'
                  '<br>'
                  f'<b>EEE: </b> {ele[36]}'
                  '<br>'
                  f'<b>UuV: </b> {ele[37]}'
                  '<br>'
                  f'<b>Invest: </b> {ele[38]}'
                  '<br>'
                  f'<b>PG 1: </b> {ele[39]}'
                  '<br>'
                  f'<b>PG 2: </b> {ele[40]}'
                  '<br>'
                  f'<b>PG 3: </b> {ele[41]}'
                  '<br>'
                  f'<b>PG 4: </b> {ele[42]}'
                  '<br>'
                  f'<b>PG 5: </b> {ele[43]}'
                )
    
              # Check if Category is not Bus or Tram or PflegeDB
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
            Variables.activeIcons.pop(f'{category}', None)
            Variables.icons.update({f'{category}': icons})
            Variables.activeIcons.update({f'{category}': icons})
            last_bbox = bbox
            Variables.last_cat = f'{category}'
    
        # Do if new Bounding Box is smaller or same than old Bounding Box
        else:
          
          #Create empty Icons Array to save Elements
          icons = []
    
          # Loop through every Element in global Icon-Elements
          for el in Variables.icons[f'{category}']:
  
            # Get coordinates of current Icon
            el_coords = dict(el['_lngLat'])
  
            # Check if Icon is inside visible Bounding Box
            if bbox[0] < el_coords['lat'] < bbox[2] and bbox[1] < el_coords['lng'] < bbox[3]:
        
              # Add Element to Map and add to Icon-Array
              el.addTo(self.mapbox)
              icons.append(el)
  
          # Change last Category and add Icons to active Icon-Array
          Variables.activeIcons.pop(f'{category}', None)
          Variables.last_cat = f'{category}'
          Variables.activeIcons.update({f'{category}': icons})
  
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
      
    #Show Marker and Icon
    for el in Variables.marker[marker_id]:  
      
      #Check if Check Box is checked and id exist 
      if check_box == True and marker_id in Variables.marker:
          
        #Add Marker to Map
        el.addTo(self.mapbox)
          
      #Check if Check Box is unchecked and id exist  
      elif check_box == False and marker_id in Variables.marker:
    
        #Remove Marker from Map
        el.remove()
  
  #This method is called when the active Layer is changed
  def change_active_Layer(self, layer, inactive_layer, visibility, other_checkbox):
    
    #Check if Layer is visible or not
    for el in layer:
    
      #Hide active Layer
      self.mapbox.setLayoutProperty(el, 'visibility', visibility)
  
      #Do for every inactive Layer
      for el in inactive_layer:
  
        #Do for every Sub-Layer of inactive Layer
        for ele in el:
  
          #Set visiblity to 'not visible'
          self.mapbox.setLayoutProperty(ele, 'visibility', 'none')
    
    #Do for every Checkbox
    for el in other_checkbox:
    
      #Uncheck Check Box from other Layers
      el.checked = False
    
    #Check visibility
    if visibility == 'visible':
    
      #Set active Layer to Bundesländer
      Variables.activeLayer = layer[0]
        
    else:
      
      #Set active Layer to Bundesländer
      Variables.activeLayer = None
    
  #This method is called from different Menu-Collapsables
  def icon_change(self, container, container_state, icon, icon_icon):
    
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
    
      # Check if active Layer is Regierungsbezirke
      elif Variables.activeLayer == 'regierungsbezirke':
  
        # Change hover-State to False and set global-variable 'hoveredStateId' to None
        self.mapbox.setFeatureState({'source': 'regierungsbezirke', 'id': Variables.hoveredStateId}, {'hover': False})
  
          # Check if active Layer is Landkreise
      elif Variables.activeLayer == 'landkreise':
  
        # Change hover-State to False and set global-variable 'hoveredStateId' to None
        self.mapbox.setFeatureState({'source': 'landkreise', 'id': Variables.hoveredStateId}, {'hover': False})
  
      # Check if active Layer is Gemeinden
      elif Variables.activeLayer == 'gemeinden':
  
        # Change hover-State to False and set global-variable 'hoveredStateId' to None
        self.mapbox.setFeatureState({'source': 'gemeinden', 'id': Variables.hoveredStateId}, {'hover': False})
        
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
  
  #Builds request-String for geocoder
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