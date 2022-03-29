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
from .. import Variables, Layer, Images
import anvil.media
import math
import datetime

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
    #Initiate Map, Marker and Geocoder
    mapboxgl.accessToken = self.token
    self.mapbox = mapboxgl.Map({'container': self.dom,
                                'style': 'mapbox://styles/mapbox/outdoors-v11',
                                'center': [13.4092, 52.5167],
                                'zoom': 8})
    self.marker = mapboxgl.Marker({'color': '#0000FF', 'draggable': True})
    self.marker.setLngLat([13.4092, 52.5167]).addTo(self.mapbox)
    self.geocoder = MapboxGeocoder({'accessToken': mapboxgl.accessToken, 'marker': False})
    self.mapbox.addControl(self.geocoder)
    
    #Initiate Listeners for different Functions  
    self.geocoder.on('result', self.move_marker)
    self.marker.on('dragend', self.marker_dragged) 
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
    
  def pdb_data_al_change(self, **event_args):
  
    #Call create_icons-Function to set the Icons on Map and save last BBox of Assisted Living DB
    Variables.last_bbox_al = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, 'assistedLiving', Variables.icon_al)
          
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
    
#     #Call a Server Function
#     anvil.server.call('manipulate')

    sendData = anvil.server.call('separate_iso', Variables.activeIso)
    
    lk_Array = []
    value_Array = []
    
    for key in sendData['data']:
      
      lk_Array.append(key)
      
    counter = 2
    
    while not counter == len(sendData['data'][key][1]):
      
      value = 0
      
      for lk in lk_Array:
        
        value += sendData['data'][lk][1][counter]
        
      value = (round(value / 2 * 100) / 100)
      
      value_Array.append(value)
      
      counter += 1
  
    keyArray = ['Municipality']
    areaArray = ['Area']
    popArray = ['Population']
    km2Array = ['Population per km2']
  
    tableContentMun: str = f"""
        <tr>
          <th class='dataCell'>Municipality</th>
      """
  
    for key in sendData['areas']:
      
      if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
      
        tableContentMun += f"""<th class='dataCell width450'>{key}</th>"""
    
    tableContentMun += """<th></th><th></th><th></th><th class='dataCell'>Iso-Layer</th>"""
    
    for key in sendData['areas']:
      
      if 'Iso' in key:
        
        tableContentMun += f"""<th class='dataCell'>{key}</th>"""
    
    tableContentMun += """</tr><tr><td class='dataCell'>Area</td>"""
    
    for key in sendData['areas']:
      
      if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
        tableContentMun += f"""<td class='dataCell'>{round(sendData['data'][key][0][9], 2)} km2</td>"""
    
    tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Area</td>"""
    
    for key in sendData['areas']:
      
      if 'Iso' in key:
        
        tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['area_complete'], 2)} km2</td>"""
    
    tableContentMun += """</tr><tr><td class='dataCell'>Population</td>"""
    
    for key in sendData['areas']:
      
      if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
        tableContentMun += f"""<td class='dataCell'>{sendData['data'][key][0][10]}</td>"""
    
    tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Population</td>"""
    
    for key in sendData['areas']:
      
      if 'Iso' in key:
        
        tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'])}</td>"""
       
    tableContentMun += """</tr><tr><td class='dataCell'>Population per km2</td>"""
    
    for key in sendData['areas']:
      
      if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
        tableContentMun += f"""<td class='dataCell'>{sendData['data'][key][0][13]}</td>"""
  
    tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Population per km2</td>""" 
  
    for key in sendData['areas']:
        
      if 'Iso' in key:
          
        tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] / sendData['areas'][key]['area_complete'])}</td>"""
      
    tableContentMun += """</tr><tr class='emptyRow'></tr>"""
    
    for key in sendData['areas']:
      
      if 'Iso' in key:
    
        tableContentMun += f"""<tr>
                                <th class='dataCell'>{key}</th>
                              </tr>
                              <tr>
                                <th class='dataCell'>Gender</th>
                                <th class='dataCell'>Overall</th>
                                <th class='dataCell'>Under 3</th>
                                <th class='dataCell'>3 to Under 6</th>
                                <th class='dataCell'>6 to Under 10</th>
                                <th class='dataCell'>10 to Under 15</th>
                                <th class='dataCell'>15 to Under 18</th>
                                <th class='dataCell'>18 to Under 20</th>
                                <th class='dataCell'>20 to Under 25</th>
                                <th class='dataCell'>25 to Under 30</th>
                                <th class='dataCell'>30 to Under 35</th>
                                <th class='dataCell'>35 to Under 40</th>
                                <th class='dataCell'>40 to Under 45</th>
                                <th class='dataCell'>45 to Under 50</th>
                                <th class='dataCell'>50 to Under 55</th>
                                <th class='dataCell'>55 to Under 60</th>
                                <th class='dataCell'>60 to Under 65</th>
                                <th class='dataCell'>65 to Under 75</th>
                                <th class='dataCell'>75 and Older</th>
                              </tr>
                              <tr>
                                <td class='dataCell'>Overall</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[35] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[53] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[18] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[36] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[19] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[37] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[20] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[38] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[21] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[39] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[22] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[40] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[23] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[41] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[24] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[42] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[25] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[43] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[26] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[44] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[27] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[45] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[28] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[46] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[29] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[47] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[30] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[48] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[31] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[49] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[32] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[50] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[33] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[51] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[34] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[52] / 100))}</td>
                              </tr>
                              <tr>
                                <td class='dataCell'>Male</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[35] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[18] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[19] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[20] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[21] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[22] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[23] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[24] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[25] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[26] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[27] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[28] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[29] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[30] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[31] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[32] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[33] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[34] / 100))}</td>
                              </tr>
                              <tr>
                                <td class='dataCell'>Female</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[53] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[36] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[37] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[38] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[39] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[40] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[41] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[42] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[43] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[44] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[45] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[46] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[47] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[48] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[49] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[50] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[51] / 100))}</td>
                                <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[52] / 100))}</td>
                              </tr>
                              <tr class='emptyRow'></tr>
                            """
    html: str = f"""
      <html>
        <head>
          <title>Iso-Layer People Data</title>
          <style>
            table {{border-collapse: collapse; text-align: center; width: 99vw}}
            .dataCell {{border: 1px solid black}}
            .emptyRow {{height: 2vh}}
          </style>
          <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
        </head>
        <body>
          <table>
            {tableContentMun}
          </table>
        </body>
      </html>
    """
  
    anvil.js.call('open_tab', html)
    
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
      self.icon_change(self.poi_category, False, self.poi_categories, 'fa:angle-right')
      
    else:
    
      #Set Checkbox-Panel to visible and change Arrow-Icon
      self.icon_change(self.poi_category, True, self.poi_categories, 'fa:angle-down')
      
  def Summary_click(self, **event_args): 
    #Create Variables for multiple Uses in Function
    lng_lat_marker = {
                      "lng": (dict(self.marker['_lngLat'])['lng']),
                      "lat": (dict(self.marker['_lngLat'])['lat'])
                     }

    #Create Bounding Box based on Iso-Layer
    iso = dict(self.mapbox.getSource('iso'))
    bbox = [0, 0, 0, 0]
    for point in iso['_data']['features'][0]['geometry']['coordinates'][0]:
      if point[0] < bbox[1] or bbox[1] == 0:
        bbox[1] = point[0]
      if point[0] > bbox[3] or bbox[3] == 0:
        bbox[3] = point[0]
      if point[1] < bbox[0] or bbox[0] == 0:
        bbox[0] = point[1]
      if point[1] > bbox[2] or bbox[2] == 0:
        bbox[2] = point[1]

    #Get Data for Competitor Analysis
    index = 1
    counter = 0
    data_comp_analysis = []
    coords = []
    for entry_caredb in Variables.pflegeDBEntries:
      lng_entry = "%.6f" % float(entry_caredb[46])
      lat_entry = "%.6f" % float(entry_caredb[45])
      for icon in Variables.activeIcons['pflegeDB']:
        lng_icon = "%.6f" % icon['_lngLat']['lng']
        lat_icon = "%.6f" % icon['_lngLat']['lat']
        if lng_entry == lng_icon and lat_entry == lat_icon:
          coords.append([lng_icon, lat_icon])
          counter += 1
          if entry_caredb[27] == "-":
            anz_vers_pat = 0
          else:
            anz_vers_pat = int(entry_caredb[27])
          if entry_caredb[28] == "-":
            platz_voll_pfl = 0
          else:
            platz_voll_pfl = int(entry_caredb[28])
          if not anz_vers_pat == 0 and not platz_voll_pfl == 0:
            occupancy_raw = round((anz_vers_pat * 100) / platz_voll_pfl)
            occupancy = f"{occupancy_raw} %"
          else:
            occupancy = "-"
          if not entry_caredb[38] == "-":
            invest = f"{entry_caredb[38]}"
            if len(invest) == 4:
              invest += "0"
          else:
            invest = entry_caredb[38]
          data = {
                  "index": index,
                  "name": entry_caredb[5].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "platz_voll_pfl": entry_caredb[28],
                  "ez": entry_caredb[31],
                  "dz": entry_caredb[32],
                  "anz_vers_pat": entry_caredb[27],
                  "occupancy": occupancy,
                  "baujahr": entry_caredb[33],
                  "status": entry_caredb[4],
                  "betreiber": entry_caredb[6].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "invest": invest,
                  "mdk_note": entry_caredb[26]
                 }
          data_comp_analysis.append(data)
          index += 1          
          break

    #Sort Coordinates by Distance
    sorted_coords = anvil.server.call("get_distance", lng_lat_marker, coords)
    index_coords = len(sorted_coords)

    #Build Request-String for Mapbox Static-Map-API
    request_static_map = f"%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23FBA237%22%2C%22marker-size%22%3A%22large%22%2C%22marker-symbol%22%3A%22s%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{lng_lat_marker['lng']},{lng_lat_marker['lat']}%5D%7D%7D"
    for coordinate in reversed(sorted_coords):
      request_static_map += f"%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23000000%22%2C%22marker-size%22%3A%22large%22%2C%22marker-symbol%22%3A%22{index_coords}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0][0]},{coordinate[0][1]}%5D%7D%7D"
      index_coords -= 1
    request_static_map += "%5D%7D"

    #Get Place from Geocoder-API for Map-Marker
    string = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lng_lat_marker['lng']},{lng_lat_marker['lat']}.json?access_token={self.token}"
    response_data = anvil.http.request(string,json=True)
    marker_context = response_data['features'][0]['context']
    
    #Get Information about Zipcode, District, City and Federal-State of Map-Marker-Position
    zipcode = "n.a."
    district = "n.a."
    city = "n.a."
    federal_state = "n.a."
    for info in marker_context:
      if "postcode" in info['id'] :
        zipcode = info['text']
      elif "locality" in info['id']:
        district = info['text'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig")
      elif "place" in info['id']:
        city = info['text'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig")
        city_alt = info['text']
      elif "region" in info['id']:
        federal_state = info['text']
    if federal_state == "n.a.":
      federal_state = city
    if district == "n.a.":
      district = city

    #Get Value of choosen Time and Movement
    time = self.time_dropdown.selected_value
    if time == "-1":
      time = "20"
    movement = self.profile_dropdown.selected_value.lower()

    #Get Information from Database for County of Marker-Position
    countie_data = anvil.server.call("get_countie_data_from_db", city_alt, federal_state)
    countie = countie_data[0][1].split(',')

    #Get Entries from Care-Database based on Federal State
    care_data_federal = anvil.server.call("get_federalstate_data", federal_state, countie_data[0][0])
    
    #Sum up all Patients in County
    pat_rec_full_care = 0
    for entry_cd in care_data_federal:
        if not entry_cd[27] == '-':
            pat_rec_full_care += int(entry_cd[27])
    pat_rec_full_care_fc = round(pat_rec_full_care * float(countie_data[1][20]))

    #Get Data from Care-Database based on Iso-Layer
    care_data_iso = anvil.server.call("get_iso_data", bbox)

    #Create Variables for different Values for Summary
    inpatients = 0
    beds_active = 0
    beds_planned = 0
    beds_construct = 0
    nursing_homes_active = 0
    nursing_homes_planned = 0
    nursing_homes_construct = 0
    patients = 0
    invest_cost = []
    operator = []
    beds = []
    year = []
    operator_public = []
    operator_nonProfit = []
    operator_private = []
    pg3_cost = []
    copayment_cost = []
    board_cost = []
    
    #Get Values of Variables for every Entry in Care-Database inside Iso-Layer-Bounding-Box
    for care_entry in care_data_iso:
      beds_amount = 0
      if not care_entry[27] == '-':
        inpatients += int(care_entry[27])
      if care_entry[4] == "aktiv":
        nursing_homes_active += 1
        if not care_entry[28] == "-":
          beds_active += int(care_entry[28])
          beds_amount += int(care_entry[28])
        if not care_entry[29] == "-":
          beds_active += int(care_entry[29])
          beds_amount += int(care_entry[29])
        if not care_entry[30] == "-":
          beds_active += int(care_entry[30])
          beds_amount += int(care_entry[30])
        beds.append(beds_amount)
      elif care_entry[4] == "in Planung":
        nursing_homes_planned += 1
        if not care_entry[31] == "-":
          beds_planned += int(care_entry[31])
        if not care_entry[32] == "-":
          beds_planned += (int(care_entry[32]) * 2)
      elif care_entry[4] == "im Bau":
        nursing_homes_construct += 1
        if not care_entry[31] == "-":
          beds_construct += int(care_entry[31])
        if not care_entry[32] == "-":
          beds_construct += (int(care_entry[32]) * 2)
      if not care_entry[38] == "-":
        invest_cost.append(float(care_entry[38]))
      if not care_entry[6] == "-":
        if care_entry[9] == "privat":
          if not care_entry[6] in operator_private:
            operator_private.append(care_entry[6])
        elif care_entry[9] == "gemeinnützig":
          if not care_entry[6] in operator_nonProfit:
            operator_nonProfit.append(care_entry[6])
        elif care_entry[9] == "kommunal":
          if not care_entry[6] in operator_public:
            operator_public.append(care_entry[6])
        if not care_entry[6] in operator:
          operator.append(care_entry[6])
      if not care_entry[33] == "-":
        year.append(int(care_entry[33]))
      if not care_entry[41] == "-":
        pg3_cost.append(float(care_entry[41]))
      if not care_entry[36] == "-":
        copayment_cost.append(float(care_entry[36]))
      if not care_entry[37] == "-":
        board_cost.append(float(care_entry[37]))

    #Get Data for Summary and Competitor-Analysis-Piechart
    inpatients_fc = round(pat_rec_full_care_fc * (round(((inpatients * 100) / pat_rec_full_care), 1) / 100))
    invest_median = "{:.2f}".format(anvil.server.call("get_median", invest_cost))
    beds_median = anvil.server.call("get_median", beds)
    year_median = round(anvil.server.call("get_median", year))
    pg3_median = "{:.2f}".format(anvil.server.call("get_median", pg3_cost))
    copayment_median = "{:.2f}".format(anvil.server.call("get_median", copayment_cost))
    board_median = "{:.2f}".format(anvil.server.call("get_median", board_cost))
    if not operator_private == 0:
      op_private_percent = round((len(operator_private) * 100) / len(operator))
    else:
      op_private_percent = 0
    if not operator_nonProfit == 0:
      op_nonProfit_percent = round((len(operator_nonProfit) * 100) / len(operator))
    else:
      op_nonProfit_percent = 0
    if not operator_public == 0:
      op_public_percent = round((len(operator_public) * 100) / len(operator))
    else:
      op_public_percent = 0
    occupancy_raw = round((inpatients * 100) / beds_active)
    beds_adjusted = beds_active + beds_construct + beds_planned
    beds_surplus = beds_adjusted - inpatients_fc

    #Create Variables for different Values for Assisted Living Analysis
    mapRequestData = [lng_lat_marker['lng'], lng_lat_marker['lat'], self.token]
    apartments = 0
    facilities_active = 0
    facilities_planning = 0
    facilities_building = 0
    facilities_overall = 0
    apartments_planning = 0
    apartments_building = 0
    without_apartment = 0
    without_apartment_building = 0
    without_apartment_planning = 0

    #Get Assisted Living Facilities in Countie and inside 10km Radius of Marker
    al_entries = anvil.server.call("get_al_for_countie", countie[0])
    al_list = anvil.server.call("get_all_al_in_10km", lng_lat_marker, al_entries)

    #Get Data from Assisted Living Facilities
    for el in al_entries:
      facilities_overall += 1
      if el[3] == "aktiv":
        facilities_active += 1
        if not el[19] == "nan":
          apartments += int(float(el[19]))
        else:
          without_apartment += 1
      elif el[3] == "in Planung":
        facilities_planning += 1
        if not el[19] == "nan":
          apartments_planning += int(float(el[19]))
        else:
          without_apartment_planning += 1
      elif el[3] == "im Bau":
        facilities_building += 1
        if not el[19] == "nan":
          apartments_building += int(float(el[19]))
        else:
          without_apartment_building += 1
    if facilities_building > 0:
      build_apartments_average = round(apartments_building / facilities_building)
      build_apartments_adjusted = apartments_building + (build_apartments_average * without_apartment_building)
    else:
      build_apartments_average = 0
      build_apartments_adjusted = 0
    if facilities_active > 0:
      apartments_average = round(apartments / facilities_active)
      apartments_adjusted = apartments + (apartments_average * without_apartment)
    else:
      apartments_average = 0
      apartments_adjusted = 0
    if facilities_planning > 0:
      planning_apartments_average = round(apartments_planning / facilities_planning)
      planning_apartments_adjusted = apartments_planning + (planning_apartments_average * without_apartment_planning)
    else:
      planning_apartments_average = 0
      planning_apartments_adjusted = 0
    facilities_plan_build = facilities_planning + facilities_building
    apartments_plan_build = apartments_planning + apartments_building
    apartments_per_10k = apartments_adjusted // round(countie_data[0][19] // 10000)
      
    #Get Data for apartments in 10km Radius
    apartments_10km = 0
    for el in al_list:
      if not el[19] == "nan":
        apartments_10km += int(float(el[19]))

    #Create Charts and Static Map for Analysis
    values_pie_ca = [{"topic": "Median Nursing charge (PG 3) in €", "value": pg3_median}, {"topic": "Median Specific co-payment in €", "value": copayment_median}, {"topic": "Median Invest Cost in €", "value": invest_median}, {"topic": "Median Board and lodging in €", "value": board_median}]
    anvil.server.call("create_pie_chart", values_pie_ca, "donut_ca")
    values_pie_sum = [{"topic": "% Public operators", "value": len(operator_public)}, {"topic": "% Non-profit operators", "value": len(operator_nonProfit)}, {"topic": "% Private operators", "value": len(operator_private)}]
    anvil.server.call("create_pie_chart", values_pie_sum, "donut_sum")
    values_bar_sum = [{"topic": "Number of inpatients", "value": inpatients}, {"topic": "Beds", "value": beds_active}, {"topic": "Number of inpatients forecast 2030", "value": inpatients_fc}, {"topic": "Adjusted number of beds<br>(incl. beds in planning and under construction)", "value": beds_adjusted}]
    anvil.server.call("create_bar_chart", values_bar_sum, "bar")
    anvil.server.call("create_static_map", bbox, self.token, data_comp_analysis, request_static_map, "CA")
    
    #Create Data-Objects for Summary
    sendData_Summary = {"zipcode": zipcode,
                        "city": city,
                        "district": district,
                        "federal_state": federal_state,
                        "time": time,
                        "movement": movement,
                        "countie": countie[0],
                        "population": countie_data[0][19],
                        "people_u75": int((float(countie_data[0][19]) * float(countie_data[0][17])) / 100),
                        "people_o75": int((float(countie_data[0][19]) * float(countie_data[0][18])) / 100),
                        "pat_rec_full_care": pat_rec_full_care,
                        "inpatients": inpatients,
                        "beds_active": beds_active,
                        "nursing_homes_active": nursing_homes_active,
                        "nursing_homes_planned": nursing_homes_planned,
                        "nursing_homes_construct": nursing_homes_construct,
                        "beds_planned": beds_planned,
                        "beds_construct": beds_construct,
                        "beds_adjusted": beds_adjusted,
                        "occupancy_raw": occupancy_raw,
                        "invest_median": invest_median,
                        "operator": len(operator),
                        "beds_median": beds_median,
                        "year_median": year_median,
                        "op_public_percent": op_public_percent,
                        "op_nonProfit_percent": op_nonProfit_percent,
                        "op_private_percent": op_private_percent,
                        "people_u75_fc": round((int((float(countie_data[0][19]) * float(countie_data[0][17])) / 100)) * float(countie_data[1][20])),
                        "forecast_change": countie_data[1][19],
                        "people_o75_fc": round((int((float(countie_data[0][19]) * float(countie_data[0][18])) / 100)) * float(countie_data[1][20])),
                        "pat_rec_full_care_fc": pat_rec_full_care_fc,
                        "inpatients_fc": inpatients_fc,
                        "beds_surplus": beds_surplus,
                        "without_apartment": without_apartment} 
    sendData_ALAnalysis = {"countie": countie[0],
                           "population": countie_data[0][19],
                           "people_u75": int((float(countie_data[0][19]) * float(countie_data[0][17])) / 100),
                           "people_o75": int((float(countie_data[0][19]) * float(countie_data[0][18])) / 100),
                           "apartments": apartments,
                           "apartments_per_10k": apartments_per_10k,
                           "people_u75_fc": round((int((float(countie_data[0][19]) * float(countie_data[0][17])) / 100)) * float(countie_data[1][20])),
                           "people_o75_fc": round((int((float(countie_data[0][19]) * float(countie_data[0][18])) / 100)) * float(countie_data[1][20])),
                           "forecast_change": countie_data[1][19],
                           "facilities_active": facilities_active,
                           "facilities_plan_build": facilities_plan_build,
                           "apartments_plan_build": apartments_plan_build,
                           "facilities_10km": len(al_list),
                           "apartments_10km": apartments_10km,
                           "with_apartment": (facilities_active - without_apartment),
                           "without_apartment": without_apartment,
                           "apartments_adjusted": apartments_adjusted,
                           "facilities_building": facilities_building,
                           "with_apartment_building": (facilities_building - without_apartment_building),
                           "without_apartment_building": without_apartment_building,
                           "apartments_building": apartments_building,
                           "build_apartments_average": build_apartments_average,
                           "build_apartments_adjusted": build_apartments_adjusted,
                           "apartments_planning": apartments_planning,
                           "without_apartment_planning": without_apartment_planning,
                           "facilities_planning": facilities_planning,
                           "planning_apartments_average": planning_apartments_average,
                           "planning_apartments_adjusted": planning_apartments_adjusted}
    
    #Create Summary-PDF
    anvil.server.call("write_pdf_file", sendData_Summary, mapRequestData, sendData_ALAnalysis)
    
    #Get PDF from Table and start Download
    mapPDF = app_tables.pictures.search()[0]    
    anvil.media.download(mapPDF['pic'])
    
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
    Variables.activeIso = anvil.http.request(request_string,json=True)
    
    #Attach Data to iso-source
    self.mapbox.getSource('iso').setData(Variables.activeIso)
      
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
      bl_name = click.features[0].properties.lan_name
      lk_name = click.features[0].properties.krs_name
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}<br><b>Landkreis:</b> {lk_name}').addTo(self.mapbox)
  
    elif click.features[0].layer.source == 'gemeinden':
      
      if hasattr(click.features[0].properties, 'GEN'):
        
        gm_name = click.features[0].properties.GEN
        
      else:
        
        gm_name = click.features[0].properties.name
      
      key = click.features[0].properties.AGS
      data = anvil.server.call('get_data_from_database', key)
    
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
    
    layers = [{'id_fill': 'bundeslaender',
               'id_outline': 'outlineBL', 
               'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json',
               'line_width': 2}, 
              {'id_fill': 'regierungsbezirke',
               'id_outline': 'outlineRB', 
               'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/3_regierungsbezirke/1_sehr_hoch.geo.json',
               'line_width': 1},
             {'id_fill': 'landkreise',
               'id_outline': 'outlineLK', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/landkreise.geojson',
               'line_width': 0.5},
             {'id_fill': 'gemeinden',
               'id_outline': 'outlineGM', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/municipalities.geojson',
               'line_width': 0.5},
             {'id_fill': 'bezirke',
               'id_outline': 'outlineBK', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/bln_hh_mun_dist.geojson',
               'line_width': 0.5},
             {'id_fill': 'netherlands',
               'id_outline': 'outlineNL', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/netherlands.geojson',
               'line_width': 0.5}]
    
    for entry in layers:
      
      #Add filled Layer for Federal states
      self.mapbox.addLayer({
        'id': entry['id_fill'],
        'type': 'fill',
        'source': {
          'type': 'geojson',
          'data': entry['data']
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
          'id': entry['id_outline'],
          'type': 'line',
          'source': {
            'type': 'geojson',
            'data': entry['data']
          },
          'layout': {
            'visibility': 'none'
          },
          'paint': {
            'line-color': '#000',
            'line-width': entry['line_width']
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
    
            geojson = anvil.server.call('get_care_db_data', bbox, 'CareDB_Pflegeheime')
            Variables.pflegeDBEntries = geojson
        
          elif category == 'assistedLiving':
    
            geojson = anvil.server.call('get_care_db_data', bbox, 'CareDB_Betreutes_Wohnen')
            Variables.assistedLivingEntries = geojson
    
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
          
                if not category == 'assistedLiving':
    
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
    
              elif category == 'assistedLiving':
        
                el_coords = [ele[27], ele[26]]
    
                if not ele[19] == 'nan':
        
                  wohnungen = int(float(ele[19]))
          
                else:
              
                  wohnungen = ele[19]
                
                if not ele[20] == 'nan':
        
                  ezAL = int(float(ele[20]))
          
                else:
              
                  ezAL = ele[20]
                
                if not ele[21] == 'nan':
        
                  dzAL = int(float(ele[21]))
          
                else:
              
                  dzAL = ele[21]
                
                if not ele[21] == 'nan':
        
                  mieteAb = str(int(float(ele[21]))) + ' €'
          
                else:
              
                  mieteAb = ele[21]
                
                if not ele[22] == 'nan':
        
                  mieteBis = str(int(float(ele[22]))) + ' €'
          
                else:
              
                  mieteBis = ele[22]
    
                # Create Popup for Element
                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f'<b>PM ID: </b> {ele[0]}'
                  '<br>'
                  f'<b>Träger ID: </b> {ele[1]}'
                  '<br>'
                  '<br>'
                  f'<b>Sektor: </b> {ele[2]}'
                  '<br>'
                  f'<b>Art: </b> {ele[9]}'
                  '<br>'
                  f'<b>Spezialisierung: </b> {ele[25]}'
                  '<br>'
                  f'<b>Status: </b> {ele[3]}'
                  '<br>'
                  f'<b>Baujahr: </b> {ele[24]}'
                  '<br>'
                  '<br>'
                  f'<b>Name: </b> {ele[4]}'
                  '<br>'
                  '<br>'
                  f'<b>Betreiber: </b> {ele[5]}'
                  '<br>'
                  f'<b>Tochterfirma 1: </b> {ele[6]}'
                  '<br>'
                  f'<b>Tochterfirma 2: </b> {ele[7]}'
                  '<br>'
                  '<br>'
                  f'<b>Straße: </b> {ele[9]}'
                  '<br>'
                  f'<b>Postleitzahl: </b> {ele[10]}'
                  '<br>'
                  f'<b>Ort: </b> {ele[11]}'
                  '<br>'
                  f'<b>Bundesland: </b> {ele[12]}'
                  '<br>'
                  f'<b>Gemeindeschlüssel: </b> {ele[13]}'
                  '<br>'
                  '<br>'
                  f'<b>Telefon: </b> {ele[14]}'
                  '<br>'
                  f'<b>Fax: </b> {ele[15]}'
                  '<br>'
                  f'<b>E-Mail: </b> {ele[16]}'
                  '<br>'
                  f'<b>Webseite: </b> {ele[17]}'
                  '<br>'
                  f'<b>Domain: </b> {ele[18]}'
                  '<br>'
                  '<br>'
                  f'<b>Anzahl Wohnungen: </b> {wohnungen}'
                  '<br>'
                  f'<b>Einzelzimmer: </b> {ezAL}'
                  '<br>'
                  f'<b>Doppelzimmer: </b> {dzAL}'
                  '<br>'
                  f'<b>Miete ab: </b> {mieteAb}'
                  '<br>'
                  f'<b>Miete bis: </b> {mieteBis}'
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