# Import of different Modules


from ._anvil_designer import Map2_0Template
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
from anvil.tables import app_tables
from anvil.js.window import mapboxgl, MapboxGeocoder, document
from .. import Variables, Layer, Images, ExcelFrames
from .Color_for_Cluster import Color_for_Cluster
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
import anvil.js
import anvil.http
import json
import Functions
import anvil.media
import math
import datetime
import time
import copy

global Variables, Layer, Images, ExcelFrames

class Map2_0(Map2_0Template):
  # Definition of every base function inside Map2_0

  def __init__(self, **properties):
    # Set Form properties and Data Bindings
    maintenance = False

    if maintenance:
      from .Maintenance import Maintenance
      alert(content=Maintenance(), dismissible=False, buttons=[], large=True)
    else:
      self.init_components(**properties)
      self.dom = anvil.js.get_dom_node(self.spacer_1)
      self.time_dropdown.items = [("5 minutes", "5"), ("10 minutes", "10"), ("15 minutes", "15"), ("20 minutes", "20"), ("30 minutes", "30"), ("60 minutes", "60"), ("5 minutes layers", "-1")]
      self.token = anvil.server.call('get_token')
      self.app_url = anvil.server.call('get_app_url')

  
  def form_show(self, **event_args):
    # Initiate Map and set Listener on Page Load
    self.select_all_hc.tag.categorie = 'Healthcare'
    self.select_all_misc.tag.categorie = 'Miscelaneous'
    self.select_all_opnv.tag.categorie = 'ÖPNV'
    
    mapboxgl.accessToken = self.token
    self.mapbox = mapboxgl.Map({'container': self.dom,
                                'style': "mapbox://styles/mapbox/outdoors-v11",
                                'center': [13.4092, 52.5167],
                                'zoom': 8})
    # Create HTML Element for Icon
    el = document.createElement('div')
    el.className = 'marker'
    el.style.width = '40px'
    el.style.height = '40px'
    el.style.backgroundSize = '100%'
    el.style.backgroundrepeat = 'no-repeat'
    el.style.zIndex = '9001'
    el.style.backgroundImage = f'url({self.app_url}/_/theme/Pins/CB_MapPin_Location.png)'
    
    self.marker = mapboxgl.Marker({'draggable': True, 'element': el, 'anchor': 'bottom'})
    self.marker.setLngLat([13.4092, 52.5167]).addTo(self.mapbox)
    self.geocoder = MapboxGeocoder({'accessToken': mapboxgl.accessToken, 'marker': False})
    self.mapbox.addControl(self.geocoder)
    
    self.geocoder.on("result", self.move_marker)
    self.marker.on("dragend", self.marker_dragged) 
    self.mapbox.on("mousemove", "federal_states", self.change_hover_state)
    self.mapbox.on("mouseleave", "federal_states", self.change_hover_state)
    self.mapbox.on("mousemove", "administrative_districts", self.change_hover_state)
    self.mapbox.on("mouseleave", "administrative_districts", self.change_hover_state)
    self.mapbox.on("mousemove", "counties", self.change_hover_state)
    self.mapbox.on("mouseleave", "counties", self.change_hover_state)
    self.mapbox.on("mousemove", "municipalities", self.change_hover_state)
    self.mapbox.on("mouseleave", "municipalities", self.change_hover_state)
    self.mapbox.on("mousemove", "districts", self.change_hover_state)
    self.mapbox.on("mouseleave", "districts", self.change_hover_state)
    self.mapbox.on("mousemove", 'netherlands', self.change_hover_state)
    self.mapbox.on("mouseleave", 'netherlands', self.change_hover_state)
    self.mapbox.on("click", "federal_states", self.popup)
    self.mapbox.on("click", "administrative_districts", self.popup)
    self.mapbox.on("click", "counties", self.popup)
    self.mapbox.on("click", "municipalities", self.popup)
    self.mapbox.on("click", "districts", self.popup)
    self.mapbox.on("styledata", self.place_layer)
    self.mapbox.on("load", self.loadHash)


  def loadHash(self, event):
    hash = get_url_hash()
    if not len(hash) == 0:
      data = anvil.server.call('get_map_settings', hash['name'])
      for component in self.checkbox_map_style.get_components():
        if component.text == data['map_style']:
          component.selected = True
          break
      component.raise_event('clicked')
      time.sleep(.5)
      self.marker.setLngLat([data['marker_lng'], data['marker_lat']])
      self.mapbox.flyTo({"center": [data['marker_lng'], data['marker_lat']], "zoom": data['zoom']})
      self.time_dropdown.selected_value = data['distance_time']
      self.profile_dropdown.selected_value = data['distance_movement']
      self.profile_dropdown.raise_event('change')
      self.checkbox_poi_x_hfcig.checked = data['iso_layer']
      self.pdb_data_al.checked = data['assisted_living']
      self.pdb_data_cb.checked = data['nursing_homes']
      if data['assisted_living']:
        self.pdb_data_al.raise_event('change')
      if data['nursing_homes']:
        self.pdb_data_cb.raise_event('change')
      healthcare_components = self.poi_categories_healthcare_container.get_components()
      if data['poi_healthcare'][0] == '1':
        healthcare_components[0].checked = True
        healthcare_components[0].raise_event('change')
      else:
        for index, state in enumerate(data['poi_healthcare']):
          if index > 0 and state == '1':
            healthcare_components[index].checked = True
            healthcare_components[index].raise_event('change')
      miscelaneous_components = self.misc_container.get_components()
      if data['poi_misc'][0] == '1':
        miscelaneous_components[0].checked = True
        miscelaneous_components[0].raise_event('change')
      else:
        for index, state in enumerate(data['poi_misc']):
          if index > 0 and state == '1':
            miscelaneous_components[index].checked = True
            miscelaneous_components[index].raise_event('change')
      opnv_components = self.opnv_container.get_components()
      if data['poi_opnv'][0] == '1':
        opnv_components[0].checked = True
        opnv_components[0].raise_event('change')
      else:
        for index, state in enumerate(data['poi_opnv']):
          if index > 0 and state == '1':
            opnv_components[index].checked = True
            opnv_components[index].raise_event('change')
      for component in self.layer_categories.get_components():
        if component.text == data['overlay']:
          component.checked = True
          component.raise_event('change')
      self.hide_ms_marker.checked = data['study_pin']
      if data['study_pin']:
        self.hide_ms_marker.raise_event('change')
      if not len(data['cluster']) == 0:
        self.create_cluster_marker(data['cluster'])
            

  def check_box_marker_icons_change(self, **event_args):
    # Show or Hide Marker-Icon-Types
    Functions.show_hide_marker(self, event_args['sender'].checked, event_args['sender'].text)

  def button_marker_icons_change(self, **event_args):
    # Show or Hide all Marker Icons
    
    all_marker = self.icon_grid.get_components()
    
    if dict(event_args)['sender'].text == "Show All": 
      marker_state = True
      self.show_marker.enabled = False
      self.hide_marker.enabled = True
    elif dict(event_args)['sender'].text == "Hide All":
      marker_state = False
      self.show_marker.enabled = True
      self.hide_marker.enabled = False
      
    for marker in all_marker:
      if not type(marker) is Label:
        Functions.show_hide_marker(self, marker_state, marker.text)
        marker.checked = marker_state
   
  
  def check_box_overlays_change(self, **event_args):
    #Change Overlays based on checked Checkbox
    
    layer_name = dict(event_args)['sender'].text.replace(" ", "_")
    outline_name = "outline_" + layer_name
    visibility = self.mapbox.getLayoutProperty(layer_name, "visibility")
    inactive_layers = []
    inactive_checkboxes = []
    
    all_layers = [
      {
        'name': "federal_states",
        'checkbox': self.check_box_fs
      }, 
      {
        'name': "administrative_districts",
        'checkbox': self.check_box_ad
      }, 
      {
        'name': "counties",
        'checkbox': self.check_box_c
      }, 
      {
        'name': "municipalities",
        'checkbox': self.check_box_m
      }, 
      {
        'name': "districts",
        'checkbox': self.check_box_d
      }, 
      {
        'name': "netherlands",
        'checkbox': self.check_box_nl
      }
    ]
    
    if visibility == "none":
      new_visibility = "visible"
    else:
      new_visibility = "none"
    
    for layer in all_layers:
      if not layer['name'] == layer_name:
        inactive_layers.append([layer['name'], "outline_" + layer['name']])
        inactive_checkboxes.append(layer['checkbox'])
    
    Functions.change_active_Layer(self, [layer_name, outline_name], inactive_layers, new_visibility, inactive_checkboxes)


  def check_box_poi_change(self, **event_args):
    # Check or uncheck various Check Boxes for different POI Categories
    if dict(event_args)['sender'].text == "veterinary":
      Variables.last_bbox_vet = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
    elif dict(event_args)['sender'].text == "social facility":
      Variables.last_bbox_soc = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
    elif dict(event_args)['sender'].text == "pharmacy":
      Variables.last_bbox_pha = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
    elif dict(event_args)['sender'].text == "nursing-home":
      Variables.last_bbox_nur = self.create_icons(self.check_box_nur.checked, Variables.last_bbox_nur, "nursing_home", Variables.icon_nursing)
    elif dict(event_args)['sender'].text == "hospital":
      Variables.last_bbox_hos = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
    elif dict(event_args)['sender'].text == "clinic":
      Variables.last_bbox_cli = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
    elif dict(event_args)['sender'].text == "dentist":
      Variables.last_bbox_den = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
    elif dict(event_args)['sender'].text == "doctors":
      Variables.last_bbox_doc = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)      
    elif dict(event_args)['sender'].text == "nursing-schools":
      Variables.last_bbox_nsc = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools) 
    elif dict(event_args)['sender'].text == "supermarket":
      Variables.last_bbox_sma = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
    elif dict(event_args)['sender'].text == "restaurant":
      Variables.last_bbox_res = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
    elif dict(event_args)['sender'].text == "cafe":
      Variables.last_bbox_caf = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
    elif dict(event_args)['sender'].text == "university":
      Variables.last_bbox_uni = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
    elif dict(event_args)['sender'].text == "bus stop":
      Variables.last_bbox_bus = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
    elif dict(event_args)['sender'].text == "tram stop":
      Variables.last_bbox_tra = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
    elif dict(event_args)['sender'].text == "Nursing Homes DB":
      Variables.last_bbox_nh = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
    elif dict(event_args)['sender'].text == "Assisted Living DB":
      Variables.last_bbox_al = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
    elif dict(event_args)['sender'].text == "podiatrist":
      Variables.last_bbox_pdt = self.create_icons(self.check_box_pdt.checked, Variables.last_bbox_pdt, "podiatrist", Variables.icon_podiatrist)
    elif dict(event_args)['sender'].text == "hairdresser":
      Variables.last_bbox_hd = self.create_icons(self.check_box_hd.checked, Variables.last_bbox_hd, "hairdresser", Variables.icon_hairdresser)


  #This method is called when the Check Box for POI based on HFCIG is checked or unchecked
  def checkbox_poi_x_hfcig_change(self, **event_args):
      
    if self.checkbox_poi_x_hfcig.checked == True:
      bbox = Functions.create_bounding_box(self)
    else:  
      bbox = [(dict(self.mapbox.getBounds()['_sw']))['lat'], (dict(self.mapbox.getBounds()['_sw']))['lng'], (dict(self.mapbox.getBounds()['_ne']))['lat'], (dict(self.mapbox.getBounds()['_ne']))['lng']]
    
    Functions.refresh_icons(self)
        
##### Check-Box Functions #####
###############################
#####  Button Functions   #####

  #This method is called when the Button for toggling the Marker-Popups got clicked    
  def button_infos_click(self, **event_args):
    anvil.js.call('hide_show_Popup')   

    
  #This method is called when one of the Buttons for changing the Map-Style got clicked    
  def radio_button_map_change_clicked(self, **event_args):
    if dict(event_args)['sender'].text == "Satellite Map":
      self.mapbox.setStyle('mapbox://styles/mapbox/satellite-streets-v11')
    elif dict(event_args)['sender'].text == "Outdoor-Map":
      self.mapbox.setStyle('mapbox://styles/mapbox/outdoors-v11')
    elif dict(event_args)['sender'].text == "IM-Map":
      self.mapbox.setStyle('mapbox://styles/mapbox/light-v11')
    self.mapbox.on('load', self.place_layer)
    #shinykampfkeule/clcylq1kd000c14p5w6tgrpyz
    #mapbox://styles/shinykampfkeule/clcqbbo8b00ug14s17s6621rf
    #mapbox://styles/mapbox/light-v11
    #mapbox://styles/shinykampfkeule/clcylq1kd000c14p5w6tgrpyz
    
  
  #This method is called when one of the Submenus should be opened or closed
  def button_toggle_menu_parts(self, **event_args):

    toggler = {
      'Distance-Layer': {
        'container': self.dist_container,
        'icon_container': self.dist_layer
      },
      'Import & Cluster': {
        'container': self.icon_categories_all,
        'icon_container': self.button_icons
      },
      'Overlays': {
        'container': self.layer_categories,
        'icon_container': self.button_overlay
      },
      'Map-Styles': {
        'container': self.checkbox_map_style,
        'icon_container': self.map_styles
      },
      'Point of Interests': {
        'container': self.poi_category,
        'icon_container': self.poi_categories
      },
      'Healthcare': {
        'container': self.poi_categories_healthcare_container,
        'icon_container': self.button_healthcare
      },
      'Miscelaneous': {
        'container': self.misc_container,
        'icon_container': self.misc_button
      },
      'ÖPNV': {
        'container': self.opnv_container,
        'icon_container': self.opnv_button
      }
    }
    
    sender = dict(event_args)['sender'].text
    container = toggler[sender]['container']
    container.visible = not container.visible
    icon_container = toggler[sender]['icon_container']
    
    if container.visible:
      icon_container.icon = "fa:angle-down"
    else:
      icon_container.icon = "fa:angle-right"
   
  #######Noch bearbeiten#######
  #This method is called when the User used the Admin-Button (!!!Just for Admin!!!)  
  def admin_button_click(self, **event_args): 

    date = datetime.datetime.now()
    # anvil.server.call('test_i_love_pdf')
    # anvil.server.call('micmaccircle')
    # anvil.server.call('read_regularien')
    # anvil.server.call('get_db_stations')

    url = anvil.server.call('get_app_url') + f'#?name=Test'
    poi_healthcare = ""
    poi_miscelaneous = ""
    poi_opnv = ""
    overlay = ""
    for category in self.poi_categories_healthcare_container.get_components():
      if category.checked:
        poi_healthcare += '1'
      else:
        poi_healthcare += '0'
    for category in self.misc_container.get_components():
      if category.checked:
        poi_miscelaneous += '1'
      else:
        poi_miscelaneous += '0'
    for category in self.opnv_container.get_components():
      if category.checked:
        poi_opnv += '1'
      else:
        poi_opnv += '0'
    for component in self.layer_categories.get_components():
      if component.checked:
        overlay = component.text
        break
    for component in self.checkbox_map_style.get_components():
      print(component.selected)
      if component.selected:
        map_style = component.text
        break
    study_pin = self.hide_ms_marker.checked

    settings = Variables.marker
    for setting in settings:
      settings[setting].pop('marker')
    cluster = {
      'data': self.cluster_data,
      'settings': Variables.marker
    }
    
    dataset = {
      'marker_lng': self.marker['_lngLat']['lng'],
      'marker_lat': self.marker['_lngLat']['lat'],
      'cluster': cluster,
      'distance_movement': self.profile_dropdown.selected_value,
      'distance_time': self.time_dropdown.selected_value,
      'overlay': overlay,
      'map_style': map_style,
      'poi_healthcare': poi_healthcare,
      'poi_misc': poi_miscelaneous,
      'poi_opnv': poi_opnv,
      'nursing_homes': self.pdb_data_cb.checked,
      'assisted_living': self.pdb_data_al.checked,
      'iso_layer': self.checkbox_poi_x_hfcig.checked,
      'name': 'Test', #Need to be added
      'url': url,
      'study_pin': study_pin,
      'zoom': self.mapbox.getZoom()
    }

    anvil.server.call('save_map_settings', dataset)
    
    alert(url)
    print(date)
    
#     #Call a Server Function
#     anvil.server.call('manipulate')

#     sendData = anvil.server.call('separate_iso', Variables.activeIso)
    
#     lk_Array = []
#     value_Array = []
    
#     for key in sendData['data']:
      
#       lk_Array.append(key)
      
#     counter = 2
    
#     while not counter == len(sendData['data'][key][1]):
      
#       value = 0
      
#       for lk in lk_Array:
        
#         value += sendData['data'][lk][1][counter]
        
#       value = (round(value / 2 * 100) / 100)
      
#       value_Array.append(value)
      
#       counter += 1
  
#     keyArray = ['Municipality']
#     areaArray = ['Area']
#     popArray = ['Population']
#     km2Array = ['Population per km2']
  
#     tableContentMun: str = f"""
#         <tr>
#           <th class='dataCell'>Municipality</th>
#       """
  
#     for key in sendData['areas']:
      
#       if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
      
#         tableContentMun += f"""<th class='dataCell width450'>{key}</th>"""
    
#     tableContentMun += """<th></th><th></th><th></th><th class='dataCell'>Iso-Layer</th>"""
    
#     for key in sendData['areas']:
      
#       if 'Iso' in key:
        
#         tableContentMun += f"""<th class='dataCell'>{key}</th>"""
    
#     tableContentMun += """</tr><tr><td class='dataCell'>Area</td>"""
    
#     for key in sendData['areas']:
      
#       if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
#         tableContentMun += f"""<td class='dataCell'>{round(sendData['data'][key][0][9], 2)} km2</td>"""
    
#     tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Area</td>"""
    
#     for key in sendData['areas']:
      
#       if 'Iso' in key:
        
#         tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['area_complete'], 2)} km2</td>"""
    
#     tableContentMun += """</tr><tr><td class='dataCell'>Population</td>"""
    
#     for key in sendData['areas']:
      
#       if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
#         tableContentMun += f"""<td class='dataCell'>{sendData['data'][key][0][10]}</td>"""
    
#     tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Population</td>"""
    
#     for key in sendData['areas']:
      
#       if 'Iso' in key:
        
#         tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'])}</td>"""
       
#     tableContentMun += """</tr><tr><td class='dataCell'>Population per km2</td>"""
    
#     for key in sendData['areas']:
      
#       if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
#         tableContentMun += f"""<td class='dataCell'>{sendData['data'][key][0][13]}</td>"""
  
#     tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Population per km2</td>""" 
  
#     for key in sendData['areas']:
        
#       if 'Iso' in key:
          
#         tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] / sendData['areas'][key]['area_complete'])}</td>"""
      
#     tableContentMun += """</tr><tr class='emptyRow'></tr>"""
    
#     for key in sendData['areas']:
      
#       if 'Iso' in key:
    
#         tableContentMun += f"""<tr>
#                                 <th class='dataCell'>{key}</th>
#                               </tr>
#                               <tr>
#                                 <th class='dataCell'>Gender</th>
#                                 <th class='dataCell'>Overall</th>
#                                 <th class='dataCell'>Under 3</th>
#                                 <th class='dataCell'>3 to Under 6</th>
#                                 <th class='dataCell'>6 to Under 10</th>
#                                 <th class='dataCell'>10 to Under 15</th>
#                                 <th class='dataCell'>15 to Under 18</th>
#                                 <th class='dataCell'>18 to Under 20</th>
#                                 <th class='dataCell'>20 to Under 25</th>
#                                 <th class='dataCell'>25 to Under 30</th>
#                                 <th class='dataCell'>30 to Under 35</th>
#                                 <th class='dataCell'>35 to Under 40</th>
#                                 <th class='dataCell'>40 to Under 45</th>
#                                 <th class='dataCell'>45 to Under 50</th>
#                                 <th class='dataCell'>50 to Under 55</th>
#                                 <th class='dataCell'>55 to Under 60</th>
#                                 <th class='dataCell'>60 to Under 65</th>
#                                 <th class='dataCell'>65 to Under 75</th>
#                                 <th class='dataCell'>75 and Older</th>
#                               </tr>
#                               <tr>
#                                 <td class='dataCell'>Overall</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[35] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[53] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[18] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[36] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[19] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[37] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[20] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[38] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[21] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[39] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[22] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[40] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[23] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[41] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[24] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[42] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[25] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[43] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[26] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[44] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[27] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[45] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[28] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[46] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[29] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[47] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[30] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[48] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[31] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[49] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[32] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[50] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[33] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[51] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[34] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[52] / 100))}</td>
#                               </tr>
#                               <tr>
#                                 <td class='dataCell'>Male</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[35] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[18] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[19] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[20] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[21] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[22] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[23] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[24] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[25] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[26] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[27] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[28] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[29] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[30] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[31] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[32] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[33] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[34] / 100))}</td>
#                               </tr>
#                               <tr>
#                                 <td class='dataCell'>Female</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[53] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[36] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[37] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[38] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[39] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[40] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[41] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[42] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[43] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[44] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[45] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[46] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[47] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[48] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[49] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[50] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[51] / 100))}</td>
#                                 <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[52] / 100))}</td>
#                               </tr>
#                               <tr class='emptyRow'></tr>
#                             """
#     html: str = f"""
#       <html>
#         <head>
#           <title>Iso-Layer People Data</title>
#           <style>
#             table {{border-collapse: collapse; text-align: center; width: 99vw}}
#             .dataCell {{border: 1px solid black}}
#             .emptyRow {{height: 2vh}}
#           </style>
#           <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
#         </head>
#         <body>
#           <table>
#             {tableContentMun}
#           </table>
#         </body>
#       </html>
#     """
  
#     anvil.js.call('open_tab', html)

    print('Done')

  #######Noch bearbeiten#######
  def tm_mode_change(self, **event_args):
    if event_args['sender'].checked:
      t = TextBox(placeholder="Password")
      alert(content=t, title="Pleaser enter an Password")
      if t.text == Variables.tm_password:
        Variables.tm_mode = True
      else:
        alert("Password was incorrect ! Please try again")
        event_args['sender'].checked = False
    else:
      Variables.tm_mode = False
    
  #This methos is called when the User want's to generate a Market Summary
  def Summary_click(self, **event_args):
    
    nh_checked = self.pdb_data_cb.checked
    al_checked = self.pdb_data_al.checked

    unique_code = anvil.server.call("get_unique_code")
    searched_address = anvil.js.call('getSearchedAddress')

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

    #Get Place from Geocoder-API for Map-Marker
    string = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{lng_lat_marker['lng']},{lng_lat_marker['lat']}.json?access_token={self.token}"
    response_data = anvil.http.request(string,json=True)
    string_test = f"https://nominatim.openstreetmap.org/reverse?format=geojson&addressdetails=1&lat={lng_lat_marker['lat']}&lon={lng_lat_marker['lng']}"
    response_data_test = anvil.http.request(string_test,json=True)
    marker_context = response_data['features'][0]['context']

    #Get Information about Zipcode, District, City and Federal-State of Map-Marker-Position
    zipcode = "n.a."
    district = "n.a."
    city = "n.a."
    city_alt = "n.a."
    federal_state = "n.a."
    for info in marker_context:
      if "postcode" in info['id'] :
        zipcode = info['text']
      elif "locality" in info['id']:
        district = info['text']
      elif "place" in info['id']:
        city = info['text']
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

    marker_coords = dict(self.marker.getLngLat())

    #Get Information from Database for County of Marker-Position
    countie_data = anvil.server.call("get_demographic_district_data", marker_coords)
    countie = countie_data['ex_dem_lk']['name'].split(',')

    #Get Entries from Care-Database based on District
    care_data_district = anvil.server.call("get_care_district_data", countie_data['ex_dem_lk']['key'])

    #Get different Values for Assisted Living Analysis and/or Executive Summary
    people_u80 = int(countie_data['dem_fc_lk']['g_65tou70_2020_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2020_abs'])
    people_o80 = int(countie_data['dem_fc_lk']['g_80plus_2020_abs'])
    people_u80_fc = int(countie_data['dem_fc_lk']['g_65tou70_2030_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2030_abs'])
    people_o80_fc = int(countie_data['dem_fc_lk']['g_80plus_2030_abs'])
    people_u80_fc_35 = int(countie_data['dem_fc_lk']['g_65tou70_2035_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2035_abs'])
    people_o80_fc_35 = int(countie_data['dem_fc_lk']['g_80plus_2035_abs'])
    change_u80 = float("{:.2f}".format(((people_u80_fc * 100) / people_u80) - 100))
    change_u80_raw = change_u80 / 100
    change_o80 = float("{:.2f}".format(((people_o80_fc * 100) / people_o80) - 100))
    change_o80_raw = change_o80 / 100
    
    #Get organized Coords for Nursing Homes
    coords_nh = self.organize_ca_data(Variables.nursing_homes_entries, 'nursing_homes', lng_lat_marker)

    #Get Data for both Nursing Homes
    data_comp_analysis_nh = self.build_req_string(coords_nh, 'nursing_homes')

    inpatients_lk = 0
    beds_lk = 0
    for el in care_data_district:
      if not el['anz_vers_pat'] == '-':
        inpatients_lk += int(el['anz_vers_pat'])
      if not el['platz_voll_pfl'] == '-':
        beds_lk += int(el['platz_voll_pfl'])
      if not el['platz_kurzpfl'] == '-':
        beds_lk += int(el['platz_kurzpfl'])
      if not el['platz_nachtpfl'] == '-':
        beds_lk += int(el['platz_nachtpfl'])
    occupancy_lk = float("{:.2f}".format((inpatients_lk * 100) / beds_lk))
    occupancy_lk_raw = occupancy_lk / 100
    free_beds_lk = beds_lk - inpatients_lk

    population_fc = int(countie_data['dem_fc_lk']['g_u6_2030_abs']) + int(countie_data['dem_fc_lk']['g_6tou10_2030_abs']) + int(countie_data['dem_fc_lk']['g_10tou16_2030_abs']) + int(countie_data['dem_fc_lk']['g_16tou20_2030_abs']) + int(countie_data['dem_fc_lk']['g_20tou30_2030_abs']) + int(countie_data['dem_fc_lk']['g_30tou50_2030_abs']) + int(countie_data['dem_fc_lk']['g_50tou65_2030_abs']) + int(countie_data['dem_fc_lk']['g_65tou70_2030_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2030_abs']) + int(countie_data['dem_fc_lk']['g_80plus_2030_abs'])
    population_fc_35 = int(countie_data['dem_fc_lk']['g_u6_2035_abs']) + int(countie_data['dem_fc_lk']['g_6tou10_2035_abs']) + int(countie_data['dem_fc_lk']['g_10tou16_2035_abs']) + int(countie_data['dem_fc_lk']['g_16tou20_2035_abs']) + int(countie_data['dem_fc_lk']['g_20tou30_2035_abs']) + int(countie_data['dem_fc_lk']['g_30tou50_2035_abs']) + int(countie_data['dem_fc_lk']['g_50tou65_2035_abs']) + int(countie_data['dem_fc_lk']['g_65tou70_2035_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2035_abs']) + int(countie_data['dem_fc_lk']['g_80plus_2035_abs'])
    
    #Get organized Coords for both Assisted Living
    coords_al = self.organize_ca_data(Variables.assisted_living_entries, 'assisted_living', lng_lat_marker)
        
    #Get Data for both Assisted Living
    data_comp_analysis_al = self.build_req_string(coords_al, 'assisted_living')   
    
    nursing_home_rate = float(countie_data['pfleg_stat_lk']['heimquote2019'])
    nursing_home_rate_perc = "{:.1f}".format(nursing_home_rate * 100)
    new_r_care_rate_raw = float("{:.3f}".format(inpatients_lk / (people_u80 + people_o80)))
    new_r_care_rate_perc = "{:.1f}".format(new_r_care_rate_raw * 100)
    new_care_rate_raw = float("{:.3f}".format(inpatients_lk / round((nursing_home_rate * countie_data['ex_dem_lk']['all_compl']) + 1)))
    new_care_rate_perc = "{:.1f}".format(new_care_rate_raw * 100)
    pat_rec_full_care_fc_30_v1 = round(new_r_care_rate_raw * (people_u80_fc + people_o80_fc))
    care_rate_30_v1_raw = float("{:.3f}".format(pat_rec_full_care_fc_30_v1 / (population_fc * nursing_home_rate)))
    care_rate_30_v1_perc = "{:.1f}".format(care_rate_30_v1_raw * 100)   
    pat_rec_full_care_fc_30_v2 = round((new_r_care_rate_raw + 0.003) * (people_u80_fc + people_o80_fc))
    care_rate_30_v2_raw = float("{:.3f}".format(pat_rec_full_care_fc_30_v2 / (population_fc * nursing_home_rate)))
    care_rate_30_v2_perc = "{:.1f}".format(care_rate_30_v2_raw * 100)
    pat_rec_full_care_fc_35_v1 = round(new_r_care_rate_raw * (people_u80_fc_35 + people_o80_fc_35))
    care_rate_35_v1_raw = float("{:.3f}".format(pat_rec_full_care_fc_35_v1 / (population_fc_35 * nursing_home_rate)))
    care_rate_35_v1_perc = "{:.1f}".format(care_rate_35_v1_raw * 100)
    pat_rec_full_care_fc_35_v2 = round((new_r_care_rate_raw + 0.003) * (people_u80_fc_35 + people_o80_fc_35))
    care_rate_35_v2_raw = float("{:.3f}".format(pat_rec_full_care_fc_35_v2 / (population_fc_35 * nursing_home_rate)))
    care_rate_35_v2_perc = "{:.1f}".format(care_rate_35_v2_raw * 100)
    change_pat_rec_raw = pat_rec_full_care_fc_30_v1 / inpatients_lk - 1
    change_pat_rec = float("{:.2f}".format(change_pat_rec_raw * 100))
  
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
      if not care_entry['anz_vers_pat'] == '-':
        inpatients += int(care_entry['anz_vers_pat'])
      if care_entry['status'] == "aktiv":
        nursing_homes_active += 1
        if not care_entry['platz_voll_pfl'] == "-":
          beds_active += int(care_entry['platz_voll_pfl'])
          beds_amount += int(care_entry['platz_voll_pfl'])
        if not care_entry['platz_kurzpfl'] == "-":
          beds_active += int(care_entry['platz_kurzpfl'])
          beds_amount += int(care_entry['platz_kurzpfl'])
        if not care_entry['platz_nachtpfl'] == "-":
          beds_active += int(care_entry['platz_nachtpfl'])
          beds_amount += int(care_entry['platz_nachtpfl'])
        beds.append(beds_amount)
      elif care_entry['status'] == "in Planung":
        nursing_homes_planned += 1
        if not care_entry['platz_voll_pfl'] == "-":
          beds_planned += int(care_entry['platz_voll_pfl'])
        if not care_entry['platz_kurzpfl'] == "-":
          beds_planned += int(care_entry['platz_kurzpfl'])
        if not care_entry['platz_nachtpfl'] == "-":
          beds_planned += int(care_entry['platz_nachtpfl'])
      elif care_entry['status'] == "im Bau":
        nursing_homes_construct += 1
        if not care_entry['platz_voll_pfl'] == "-":
          beds_construct += int(care_entry['platz_voll_pfl'])
        if not care_entry['platz_kurzpfl'] == "-":
          beds_construct += int(care_entry['platz_kurzpfl'])
        if not care_entry['platz_nachtpfl'] == "-":
          beds_construct += int(care_entry['platz_nachtpfl'])
      if not care_entry['invest'] == "-":
        invest_cost.append(float(care_entry['invest']))
      if not care_entry['betreiber'] == "-":
        if care_entry['art'] == "privat":
          if not care_entry['betreiber'] in operator_private:
            operator_private.append(care_entry['betreiber'])
        elif care_entry['art'] == "gemeinnützig":
          if not care_entry['betreiber'] in operator_nonProfit:
            operator_nonProfit.append(care_entry['betreiber'])
        elif care_entry['art'] == "kommunal":
          if not care_entry['betreiber'] in operator_public:
            operator_public.append(care_entry['betreiber'])
        if not care_entry['betreiber'] in operator:
          operator.append(care_entry['betreiber'])
      if not care_entry['baujahr'] == "-":
        year.append(int(care_entry['baujahr']))
      if not care_entry['pg_3'] == "-":
        pg3_cost.append(float(care_entry['pg_3']))
      if not care_entry['eee'] == "-":
        copayment_cost.append(float(care_entry['eee']))
      if not care_entry['uuv'] == "-":
        board_cost.append(float(care_entry['uuv']))

    #Get Data for Summary and Competitor-Analysis-Piechart
    inpatients_fc = round(pat_rec_full_care_fc_30_v1 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
    inpatients_fc_v2 = round(pat_rec_full_care_fc_30_v2 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
    inpatients_fc_35 = round(pat_rec_full_care_fc_35_v1 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
    inpatients_fc_35_v2 = round(pat_rec_full_care_fc_35_v2 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
    inpatents_fc_30_avg = round((inpatients_fc + inpatients_fc_v2) / 2)
    inpatents_fc_35_avg = round((inpatients_fc_35 + inpatients_fc_35_v2) / 2)
    invest_med = anvil.server.call("get_median", invest_cost)
    invest_median = "{:.2f}".format(invest_med)
    beds_median = anvil.server.call("get_median", beds)
    year_median = round(anvil.server.call("get_median", year))
    pg3_median_raw = anvil.server.call("get_median", pg3_cost)
    pg3_median = "{:.2f}".format(pg3_median_raw)
    copayment_median_raw = anvil.server.call("get_median", copayment_cost)
    copayment_median = "{:.2f}".format(copayment_median_raw)
    board_median_raw = anvil.server.call("get_median", board_cost)
    board_median = "{:.2f}".format(board_median_raw)
    if not len(operator_private) == 0:
      if not len(operator) == 0:
        op_private_percent = round((len(operator_private) * 100) / len(operator))
        op_private_raw = op_private_percent / 100
    else:
      op_private_percent = 0
      op_private_raw = 0
    if not len(operator_nonProfit) == 0:
      if not len(operator) == 0:
        op_nonProfit_percent = round((len(operator_nonProfit) * 100) / len(operator))
        op_nonProfit_raw = op_nonProfit_percent / 100
    else:
      op_nonProfit_percent = 0
      op_nonProfit_raw = 0
    if not len(operator_public) == 0:
      if not len(operator) == 0:
        op_public_percent = round((len(operator_public) * 100) / len(operator))
        op_public_raw = op_public_percent / 100
    else:
      op_public_percent = 0
      op_public_raw = 0
    if not inpatients == 0 and not beds_active == 0:
      occupancy_percent = round((inpatients * 100) / beds_active)
      occupancy_raw = occupancy_percent / 100
    else:
      occupancy_percent = 0
      occupancy_raw = 0
    beds_adjusted = beds_active + beds_construct + beds_planned
    beds_surplus = beds_adjusted - inpatients_fc
    beds_surplus_35 = beds_adjusted - inpatients_fc_35
    beds_surplus_v2 = beds_adjusted - inpatients_fc_v2
    beds_surplus_35_v2 = beds_adjusted - inpatients_fc_35_v2
    beds_in_reserve_20 = round(beds_active * (1 - occupancy_raw))
    beds_in_reserve_fc = round(beds_adjusted * 0.05)
    beds_surplus_30_avg = round((beds_surplus + beds_surplus_v2) / 2)
    beds_surplus_35_avg = round((beds_surplus_35 + beds_surplus_35_v2) / 2)
    
################################################Neue Berechnungen################################################

    care_rate_break_even_raw = float("{:.3f}".format((beds_adjusted * 0.95) / (countie_data['ex_dem_lk']['all_compl'] * nursing_home_rate)))
    care_rate_break_even_perc = "{:.1f}".format(care_rate_break_even_raw * 100)
    care_rate_break_even_30_raw = float("{:.3f}".format((beds_adjusted * 0.95) / (population_fc * nursing_home_rate)))
    care_rate_break_even_30_perc = "{:.1f}".format(care_rate_break_even_30_raw * 100)
    care_rate_break_even_35_raw = float("{:.3f}".format((beds_adjusted * 0.95) / (population_fc_35 * nursing_home_rate)))
    care_rate_break_even_35_perc = "{:.1f}".format(care_rate_break_even_35_raw * 100)
    beds_30_v1 = round((pat_rec_full_care_fc_30_v1 / 0.95))
    beds_30_v2 = round((pat_rec_full_care_fc_30_v2 / 0.95))
    beds_35_v1 = round((pat_rec_full_care_fc_35_v1 / 0.95))
    beds_35_v2 = round((pat_rec_full_care_fc_35_v2 / 0.95))
    free_beds_30_v1 =  beds_30_v1 - pat_rec_full_care_fc_30_v1
    free_beds_30_v2 =  beds_30_v2 - pat_rec_full_care_fc_30_v2
    free_beds_35_v1 =  beds_35_v1 - pat_rec_full_care_fc_35_v1
    free_beds_35_v2 =  beds_35_v2 - pat_rec_full_care_fc_35_v2
    

################################################Neue Berechnungen################################################
    
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
    al_entries = anvil.server.call("get_al_for_district", countie_data['ex_dem_lk']['key'])
    al_list = anvil.server.call("get_all_al_in_10km", lng_lat_marker, al_entries)

    #Get Data from Assisted Living Facilities
    for el in al_entries:
      facilities_overall += 1
      if el['status'] == "aktiv":
        facilities_active += 1
        if not el['anz_wohnungen'] == "-":
          apartments += int(float(el['anz_wohnungen']))
        else:
          without_apartment += 1
      elif el['status'] == "in Planung":
        facilities_planning += 1
        if not el['anz_wohnungen'] == "-":
          apartments_planning += int(float(el['anz_wohnungen']))
        else:
          without_apartment_planning += 1
      elif el['status'] == "im Bau":
        facilities_building += 1
        if not el['anz_wohnungen'] == "-":
          apartments_building += int(float(el['anz_wohnungen']))
        else:
          without_apartment_building += 1
    if facilities_building > 0 and apartments_building > 0 and without_apartment_building > 0:
      build_apartments_average = round(apartments_building / (facilities_building - without_apartment_building))
      build_apartments_adjusted = apartments_building + (build_apartments_average * without_apartment_building)
    else:
      build_apartments_average = 0
      build_apartments_adjusted = 0
    if facilities_active > 0 and apartments > 0:
      apartments_average = round(apartments / facilities_active)
      apartments_adjusted = apartments + (apartments_average * without_apartment)
    else:
      apartments_average = 0
      apartments_adjusted = 0
    if facilities_planning > 0 and apartments_planning > 0:
      planning_apartments_average = round(apartments_planning / (facilities_planning - without_apartment_planning))
      planning_apartments_adjusted = apartments_planning + (planning_apartments_average * without_apartment_planning)
    else:
      planning_apartments_average = 0
      planning_apartments_adjusted = 0
    facilities_plan_build = facilities_planning + facilities_building
    apartments_plan_build = apartments_planning + apartments_building
    apartments_per_10k = apartments_adjusted // round(countie_data['ex_dem_lk']['all_compl'] // 10000)
      
    #Get Data for apartments in 10km Radius
    apartments_10km = 0
    for el in al_list:
      if not el['anz_wohnungen'] == "-":
        apartments_10km += int(float(el['anz_wohnungen']))
        
    apartments_plan_build_adjusted = build_apartments_adjusted + planning_apartments_adjusted
        
    #Get level, multiplier, surplus, demand and potential for Assisted Living Analysis
    if countie_data['dem_city']['bevoelkerung_ges'] < 30001:
      level = "national level"
      multiplier = 0.03
    elif countie_data['dem_city']['bevoelkerung_ges'] < 260000:
      level = "small city"
      multiplier = 0.05
    else:
      level = "top 30 city"
      multiplier = 0.07
    surplus2022 = round(apartments_adjusted - (((people_u80 + people_o80) * multiplier) / 1.5))
    if surplus2022 > 0:
      demand2022 = -abs(surplus2022)
    else:
      demand2022 = abs(surplus2022)
    surplus2040 = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (((people_u80_fc + people_o80_fc) * multiplier) / 1.5))
    if surplus2040 > 0:
      demand2040 = -abs(surplus2040)
    else:
      demand2040 = abs(surplus2040)
    if demand2040 <= -200:
      demand_potential = "very low"
    elif demand2040 <= 0:
      demand_potential = "low"
    elif demand2040 <= 200:
      demand_potential = "average"
    elif demand2040 <= 500:
      demand_potential = "strong"
    else:
      demand_potential = "very strong"

    purchase_power = anvil.server.call('get_purchasing_power', location={'lat': lng_lat_marker['lat'], 'lon': lng_lat_marker['lng']})
      
    # Copy and Fill Dataframe for Excel-Cover
    cover_frame = copy.deepcopy(ExcelFrames.cover_data)
    cover_frame['data'][1]['content'] = zipcode
    cover_frame['data'][2]['content'] = city.upper()

    # Copy and Fill Dataframe for Excel-Summary
    summary_frame = copy.deepcopy(ExcelFrames.summary_data)
    summary_frame['data'][9]['content'] = f"Population {city}"
    summary_frame['data'][10]['content'] = f"{countie[0]}, LK"
    summary_frame['data'][37]['content'] = f"In 2030 the number of inpatients will based on our scenarios be between {inpatients_fc} and {inpatients_fc_v2} (in average about {inpatents_fc_30_avg})."
    summary_frame['data'][38]['content'] = f"In 2035 the number of inpatients will based on our scenarios be between {inpatients_fc_35} and {inpatients_fc_35_v2} (in average about {inpatents_fc_35_avg})."
    summary_frame['data'][59]['content'] = f"In 2030 the surplus/deficit on beds based on our scenarios is between {beds_surplus} and {beds_surplus_v2} (in average {beds_surplus_30_avg})."
    summary_frame['data'][60]['content'] = f"In 2035 the surplus/deficit on beds based on our scenarios is between {beds_surplus_35} and {beds_surplus_35_v2} (in average {beds_surplus_35_avg})."
    summary_frame['data'][70]['content'] = countie_data['dem_city']['bevoelkerung_ges']
    summary_frame['data'][72]['content'] = countie_data['ex_dem_lk']['all_compl']
    summary_frame['data'][73]['content'] = people_u80
    summary_frame['data'][74]['content'] = people_o80
    summary_frame['data'][76]['content'] = care_rate_break_even_raw
    summary_frame['data'][77]['content'] = new_care_rate_raw
    summary_frame['data'][78]['content'] = nursing_home_rate
    summary_frame['data'][79]['content'] = inpatients_lk
    summary_frame['data'][80]['content'] = occupancy_lk_raw
    summary_frame['data'][81]['content'] = beds_lk
    summary_frame['data'][82]['content'] = free_beds_lk
    summary_frame['data'][83]['content'] = new_care_rate_raw
    summary_frame['data'][84]['content'] = nursing_home_rate
    summary_frame['data'][85]['content'] = inpatients_lk
    summary_frame['data'][86]['content'] = occupancy_lk_raw
    summary_frame['data'][87]['content'] = beds_lk
    summary_frame['data'][88]['content'] = free_beds_lk
    summary_frame['data'][90]['content'] = inpatients
    summary_frame['data'][92]['content'] = beds_active
    summary_frame['data'][93]['content'] = nursing_homes_active
    summary_frame['data'][94]['content'] = nursing_homes_planned
    summary_frame['data'][95]['content'] = nursing_homes_construct
    summary_frame['data'][96]['content'] = beds_planned
    summary_frame['data'][97]['content'] = beds_construct
    summary_frame['data'][98]['content'] = beds_active
    summary_frame['data'][99]['content'] = occupancy_raw
    summary_frame['data'][100]['content'] = beds_in_reserve_20
    summary_frame['data'][101]['content'] = f"{invest_median}€"
    summary_frame['data'][103]['content'] = beds_adjusted
    summary_frame['data'][104]['content'] = inpatients
    summary_frame['data'][105]['content'] = beds_adjusted
    summary_frame['data'][106]['content'] = inpatients
    summary_frame['data'][108]['content'] = len(operator)
    summary_frame['data'][109]['content'] = beds_median
    summary_frame['data'][110]['content'] = year_median
    summary_frame['data'][111]['content'] = op_public_raw
    summary_frame['data'][112]['content'] = op_nonProfit_raw
    summary_frame['data'][113]['content'] = op_private_raw
    summary_frame['data'][117]['content'] = population_fc
    summary_frame['data'][118]['content'] = people_u80_fc
    summary_frame['data'][119]['content'] = people_o80_fc
    summary_frame['data'][121]['content'] = care_rate_break_even_30_raw
    summary_frame['data'][122]['content'] = care_rate_30_v1_raw
    summary_frame['data'][123]['content'] = nursing_home_rate
    summary_frame['data'][124]['content'] = pat_rec_full_care_fc_30_v1
    summary_frame['data'][125]['content'] = 0.95
    summary_frame['data'][126]['content'] = beds_30_v1
    summary_frame['data'][127]['content'] = free_beds_30_v1
    summary_frame['data'][128]['content'] = care_rate_30_v2_raw
    summary_frame['data'][129]['content'] = nursing_home_rate
    summary_frame['data'][130]['content'] = pat_rec_full_care_fc_30_v2
    summary_frame['data'][131]['content'] = 0.95
    summary_frame['data'][132]['content'] = beds_30_v2
    summary_frame['data'][133]['content'] = free_beds_30_v2
    summary_frame['data'][134]['content'] = f"{time} minutes of {movement}"
    summary_frame['data'][135]['content'] = inpatients_fc
    summary_frame['data'][136]['content'] = inpatients_fc_v2
    summary_frame['data'][137]['content'] = f"{time} minutes of {movement}"
    summary_frame['data'][138]['content'] = beds_adjusted
    summary_frame['data'][139]['content'] = 0.95
    summary_frame['data'][140]['content'] = beds_in_reserve_fc
    summary_frame['data'][141]['content'] = f"{time} minutes of {movement}"
    summary_frame['data'][142]['content'] = beds_adjusted
    summary_frame['data'][143]['content'] = inpatients_fc
    summary_frame['data'][144]['content'] = beds_surplus
    summary_frame['data'][145]['content'] = beds_adjusted
    summary_frame['data'][146]['content'] = inpatients_fc_v2
    summary_frame['data'][147]['content'] = beds_surplus_v2
    summary_frame['data'][148]['content'] = f"{time} minutes of {movement}"
    summary_frame['data'][150]['content'] = zipcode
    summary_frame['data'][151]['content'] = city
    summary_frame['data'][152]['content'] = countie[0]
    summary_frame['data'][153]['content'] = federal_state
    summary_frame['data'][154]['content'] = f"{time} minutes of {movement}"
    summary_frame['data'][155]['content'] = searched_address
    summary_frame['data'][158]['content'] = population_fc_35
    summary_frame['data'][159]['content'] = people_u80_fc_35
    summary_frame['data'][160]['content'] = people_o80_fc_35
    summary_frame['data'][162]['content'] = care_rate_break_even_35_raw
    summary_frame['data'][163]['content'] = care_rate_35_v1_raw
    summary_frame['data'][164]['content'] = nursing_home_rate
    summary_frame['data'][165]['content'] = pat_rec_full_care_fc_35_v1
    summary_frame['data'][166]['content'] = 0.95
    summary_frame['data'][167]['content'] = beds_35_v1
    summary_frame['data'][168]['content'] = free_beds_35_v1
    summary_frame['data'][169]['content'] = care_rate_35_v2_raw
    summary_frame['data'][170]['content'] = nursing_home_rate
    summary_frame['data'][171]['content'] = pat_rec_full_care_fc_35_v2
    summary_frame['data'][172]['content'] = 0.95
    summary_frame['data'][173]['content'] = beds_35_v2
    summary_frame['data'][174]['content'] = free_beds_35_v2
    summary_frame['data'][176]['content'] = inpatients_fc_35
    summary_frame['data'][177]['content'] = inpatients_fc_35_v2
    summary_frame['data'][179]['content'] = beds_adjusted
    summary_frame['data'][180]['content'] = 0.95
    summary_frame['data'][181]['content'] = beds_in_reserve_fc
    summary_frame['data'][183]['content'] = beds_adjusted
    summary_frame['data'][184]['content'] = inpatients_fc_35
    summary_frame['data'][185]['content'] = beds_surplus_35
    summary_frame['data'][186]['content'] = beds_adjusted
    summary_frame['data'][187]['content'] = inpatients_fc_35_v2
    summary_frame['data'][188]['content'] = beds_surplus_35_v2
    summary_frame['data'][189]['content'] = purchase_power
    summary_frame['data'][190]['content'] = 100 - purchase_power
    summary_frame['data'][191]['content'] = purchase_power
    summary_frame['data'][194]['file'] = f"tmp/summaryMap_{unique_code}.png"


    # Copy and Fill Dataframe for Nursing Home Competitor Analysis
    nurscomp_frame = copy.deepcopy(ExcelFrames.nca_data)
    nurscomp_frame['data'][7]['content'] = pg3_median_raw
    nurscomp_frame['data'][8]['content'] = copayment_median_raw
    nurscomp_frame['data'][9]['content'] = invest_med
    nurscomp_frame['data'][10]['content'] = board_median_raw
    nurscomp_frame['row_count'] = len(data_comp_analysis_nh['data']) + 1
    
    start_row = 33
    index = 0
    subindex = 1
    last_coords_dist = 0
    home_entries = 0
    
    for competitor in data_comp_analysis_nh['data']:
      if 'home' in competitor:
        if len(competitor[0]['name']) > 35:
          name_size = 8
        else:
          name_size = 11
        if len(competitor[0]['betreiber']) > 35:
          op_size = 8
        else:
          op_size = 11
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'A{start_row}',
          'content': 'S',
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'B{start_row}',
          'content': competitor[0]['name'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': name_size,
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'C{start_row}',
          'content': competitor[0]['platz_voll_pfl'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'D{start_row}',
          'content': competitor[0]['ez'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'E{start_row}',
          'content': competitor[0]['dz'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'F{start_row}',
          'content': competitor[0]['anz_vers_pat'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'G{start_row}',
          'content': competitor[0]['occupancy'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'H{start_row}',
          'content': competitor[0]['baujahr'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036',
            'num_format': '0'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'I{start_row}',
          'content': competitor[0]['status'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'J{start_row}',
          'content': competitor[0]['betreiber'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': op_size,
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        if not competitor[0]['invest'] == 'N/A':
          print(competitor[0]['invest'])
          invest = f"{competitor[0]['invest']}€"
        else:
          invest = competitor[0]['invest']
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'K{start_row}',
          'content': invest,
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036',
            'num_format': '#,##0.00€'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'L{start_row}',
          'content': competitor[0]['mdk_note'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        home_entries += 1
      else:
        if not last_coords_dist == competitor[1]:
          index += 1
          subindex = 1
          shown_index = f'{index}'
          if len(data_comp_analysis_nh['data']) > data_comp_analysis_nh['data'].index(competitor) + 1:
            if competitor[0]['coords'] == data_comp_analysis_nh['data'][data_comp_analysis_nh['data'].index(competitor) + 1][0]['coords']:
              shown_index = f'{index}.{subindex}'
        else:
          shown_index = f'{index}'
          if not data_comp_analysis_nh['data'].index(competitor) == home_entries:
              subindex += 1
              shown_index = f'{index}.{subindex}'
        last_coords_dist = competitor[1]
        if len(competitor[0]['name']) > 35:
          name_size = 8
        else:
          name_size = 11
        if len(competitor[0]['betreiber']) > 35:
          op_size = 8
        else:
          op_size = 11
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'A{start_row}',
          'content': f'{shown_index}',
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'B{start_row}',
          'content': competitor[0]['name'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': name_size,
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'C{start_row}',
          'content': competitor[0]['platz_voll_pfl'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'D{start_row}',
          'content': competitor[0]['ez'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'E{start_row}',
          'content': competitor[0]['dz'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'F{start_row}',
          'content': competitor[0]['anz_vers_pat'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'G{start_row}',
          'content': competitor[0]['occupancy'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'H{start_row}',
          'content': competitor[0]['baujahr'],
          'format': {
            'align': 'center',
            'bottom': True,
            'num_format': '0'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'I{start_row}',
          'content': competitor[0]['status'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'J{start_row}',
          'content': competitor[0]['betreiber'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': op_size,
            'bottom': True
          }
        })
        if not competitor[0]['invest'] == 'N/A':
          invest = f"{competitor[0]['invest']}€"
        else:
          invest = competitor[0]['invest']
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'K{start_row}',
          'content': invest,
          'format': {
            'align': 'center',
            'bottom': True,
            'num_format': '#,##0.00€'
          }
        })
        nurscomp_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'L{start_row}',
          'content': competitor[0]['mdk_note'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
      start_row += 1

    # Copy and Fill Dataframe for Assisted Living Analysis
    assliv_frame = copy.deepcopy(ExcelFrames.ala_data)
    assliv_frame['data'][3]['content'] = f'Population {countie[0]}'
    assliv_frame['data'][40]['content'] = f'Population {countie[0]}'
    assliv_frame['data'][41]['content'] = f'Population {countie[0]}, LK 2022'
    assliv_frame['data'][42]['content'] = f'Population {countie[0]}, LK 2030'
    assliv_frame['data'][45]['content'] = countie_data['ex_dem_lk']['all_compl']
    assliv_frame['data'][46]['content'] = people_u80
    assliv_frame['data'][47]['content'] = people_o80
    assliv_frame['data'][48]['content'] = people_u80_fc
    assliv_frame['data'][49]['content'] = people_o80_fc
    assliv_frame['data'][50]['content'] = change_pat_rec_raw
    assliv_frame['data'][51]['content'] = apartments_adjusted
    assliv_frame['data'][52]['content'] = apartments_per_10k
    assliv_frame['data'][53]['content'] = facilities_active
    assliv_frame['data'][54]['content'] = facilities_plan_build
    assliv_frame['data'][55]['content'] = apartments_plan_build_adjusted
    assliv_frame['data'][56]['content'] = len(al_list)
    assliv_frame['data'][57]['content'] = apartments_10km
    assliv_frame['data'][58]['content'] = f'{countie[0]}, LK'
    assliv_frame['data'][61]['content'] = facilities_active - without_apartment
    assliv_frame['data'][62]['content'] = without_apartment
    assliv_frame['data'][63]['content'] = facilities_active
    assliv_frame['data'][64]['content'] = facilities_building - without_apartment_building
    assliv_frame['data'][65]['content'] = without_apartment_building
    assliv_frame['data'][66]['content'] = facilities_building
    assliv_frame['data'][67]['content'] = facilities_planning - without_apartment_planning
    assliv_frame['data'][68]['content'] = without_apartment_planning
    assliv_frame['data'][69]['content'] = facilities_planning
    assliv_frame['data'][70]['content'] = facilities_active + facilities_building + facilities_planning
    assliv_frame['data'][73]['content'] = round(((people_u80 + people_o80) * 0.01) / 1.5)
    assliv_frame['data'][74]['content'] = round(((people_u80 + people_o80) * 0.02) / 1.5)
    assliv_frame['data'][75]['content'] = round(((people_u80 + people_o80) * 0.03) / 1.5)
    assliv_frame['data'][76]['content'] = round(((people_u80 + people_o80) * 0.04) / 1.5)
    assliv_frame['data'][77]['content'] = round(((people_u80 + people_o80) * 0.05) / 1.5)
    assliv_frame['data'][78]['content'] = round(((people_u80 + people_o80) * 0.07) / 1.5)
    assliv_frame['data'][79]['content'] = round(((people_u80 + people_o80) * 0.09) / 1.5)
    assliv_frame['data'][80]['content'] = level
    assliv_frame['data'][81]['content'] = demand2022
    assliv_frame['data'][82]['content'] = demand2040
    assliv_frame['data'][83]['content'] = demand_potential
    assliv_frame['data'][88]['content'] = change_u80_raw
    assliv_frame['data'][89]['content'] = change_o80_raw
    assliv_frame['data'][100]['content'] = apartments
    assliv_frame['data'][102]['content'] = apartments
    assliv_frame['data'][103]['content'] = apartments_building
    assliv_frame['data'][105]['content'] = apartments_building
    assliv_frame['data'][106]['content'] = apartments_planning
    assliv_frame['data'][108]['content'] = apartments_planning
    assliv_frame['data'][109]['content'] = apartments + (facilities_building - without_apartment_building) + apartments_planning
    assliv_frame['data'][112]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.01) / 1.5)
    assliv_frame['data'][113]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.02) / 1.5)
    assliv_frame['data'][114]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.03) / 1.5)
    assliv_frame['data'][115]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.04) / 1.5)
    assliv_frame['data'][116]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.05) / 1.5)
    assliv_frame['data'][117]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.07) / 1.5)
    assliv_frame['data'][118]['content'] = apartments_adjusted - round(((people_u80 + people_o80) * 0.09) / 1.5)
    assliv_frame['data'][121]['content'] = apartments_average
    assliv_frame['data'][123]['content'] = apartments_adjusted
    assliv_frame['data'][124]['content'] = build_apartments_average
    assliv_frame['data'][126]['content'] = build_apartments_adjusted
    assliv_frame['data'][127]['content'] = planning_apartments_average
    assliv_frame['data'][129]['content'] = planning_apartments_adjusted
    assliv_frame['data'][130]['content'] = apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted
    assliv_frame['data'][133]['content'] = round(((people_u80_fc + people_o80_fc) * 0.01) / 1.5)
    assliv_frame['data'][134]['content'] = round(((people_u80_fc + people_o80_fc) * 0.02) / 1.5)
    assliv_frame['data'][135]['content'] = round(((people_u80_fc + people_o80_fc) * 0.03) / 1.5)
    assliv_frame['data'][136]['content'] = round(((people_u80_fc + people_o80_fc) * 0.04) / 1.5)
    assliv_frame['data'][137]['content'] = round(((people_u80_fc + people_o80_fc) * 0.05) / 1.5)
    assliv_frame['data'][138]['content'] = round(((people_u80_fc + people_o80_fc) * 0.07) / 1.5)
    assliv_frame['data'][139]['content'] = round(((people_u80_fc + people_o80_fc) * 0.09) / 1.5)
    assliv_frame['data'][144]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.01) / 1.5)))
    assliv_frame['data'][145]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.02) / 1.5)))
    assliv_frame['data'][146]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.03) / 1.5)))
    assliv_frame['data'][147]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.04) / 1.5)))
    assliv_frame['data'][148]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.05) / 1.5)))
    assliv_frame['data'][149]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.07) / 1.5)))
    assliv_frame['data'][150]['content'] = round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.09) / 1.5)))
    assliv_frame['data'][154]['series'][0]['name'] = f'{countie[0]}, LK 2022'
    assliv_frame['data'][154]['series'][1]['name'] = f'{countie[0]}, LK 2030'
    
    # Copy and Fill Dataframe for Assisted Living Competitor Analysis
    alca_frame = copy.deepcopy(ExcelFrames.alca_data)
    alca_frame['row_count'] = len(data_comp_analysis_al['data']) + 1
    
    start_row = 30
    index = 0
    subindex = 1
    last_coords_dist = 0
    home_entries = 0
    
    for competitor in data_comp_analysis_al['data']:
      if 'home' in competitor:
        if len(competitor[0]['name']) > 35:
          name_size = 8
        else:
          name_size = 11
        if len(competitor[0]['operator']) > 35:
          op_size = 8
        else:
          op_size = 11
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'A{start_row}',
          'content': 'S',
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'B{start_row}',
          'content': competitor[0]['name'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': name_size,
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'C{start_row}',
          'content': competitor[0]['operator'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': op_size,
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'D{start_row}',
          'content': competitor[0]['type'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'E{start_row}',
          'content': competitor[0]['city'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'F{start_row}',
          'content': competitor[0]['status'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'G{start_row}',
          'content': competitor[0]['number_apts'],
          'format': {
            'align': 'center',
            'bottom': True,
            'bg_color': '#FEA036'
          }
        })
        home_entries += 1
      else:
        if not last_coords_dist == competitor[1]:
          index += 1
          subindex = 1
          shown_index = f'{index}'
          if len(data_comp_analysis_al['data']) > data_comp_analysis_al['data'].index(competitor) + 1:
            if competitor[0]['coords'] == data_comp_analysis_al['data'][data_comp_analysis_al['data'].index(competitor) + 1][0]['coords']:
              shown_index = f'{index}.{subindex}'
        else:
          shown_index = f'{index}'
          if not data_comp_analysis_al['data'].index(competitor) == home_entries:
              subindex += 1
              shown_index = f'{index}.{subindex}'
        last_coords_dist = competitor[1]
        if len(competitor[0]['name']) > 35:
          name_size = 8
        else:
          name_size = 11
        if len(competitor[0]['operator']) > 35:
          op_size = 8
        else:
          op_size = 11
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'A{start_row}',
          'content': f'{shown_index}',
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'B{start_row}',
          'content': competitor[0]['name'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’"),
          'format': {
            'align': 'center',
            'font_size': name_size,
            'bottom': True
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'C{start_row}',
          'content': competitor[0]['operator'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'font_size': op_size,
            'bottom': True
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'D{start_row}',
          'content': competitor[0]['type'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'E{start_row}',
          'content': competitor[0]['city'].replace("&auml;", "ä").replace("&ouml;", "ö").replace("&uuml", "ü").replace("&Auml;", "Ä").replace("&Ouml;", "Ö").replace("&Uuml", "Ü").replace("&szlig", "ß").replace("&prime;", "’").replace("&ndash;", "-"),
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'F{start_row}',
          'content': competitor[0]['status'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
        alca_frame['data'].append({
          'type': 'text', 
          'insert': 'write', 
          'cell': f'G{start_row}',
          'content': competitor[0]['number_apts'],
          'format': {
            'align': 'center',
            'bottom': True
          }
        })
      start_row += 1
    
    t = ColumnPanel()
    t.add_component(CheckBox(text="Executive Summary", checked=True))
    t.add_component(CheckBox(text="Nursing Home Competitor Analysis", checked=True))
    t.add_component(CheckBox(text="Assisted Living Analysis", checked=True))
    t.add_component(CheckBox(text="Assisted Living Competitor Analysis", checked=True))
    alert(content=t, title="Choose Pages to create")
    checkboxes = {}
    for checkbox in t.get_components():
      checkboxes[f'{checkbox.text.replace(" ", "_")}'] = checkbox.checked

    ##### Analysis Addition to Market Study #####

    home_facilities = []
    
    ez_rate_asset = 0
    i_cost_asset = 0
    occupancy_asset = 0
    year_of_construction_asset = 0
    ez_total_comp = 0
    room_total_comp = 0
    ez_weight_avg_comp = 0
    
    for entry in data_comp_analysis_nh['data']:
      if entry[len(entry) - 1] == 'home':
        home_facilities.append(entry)
        if entry[0]['ez'] == 'N/A':
          ez_rate_asset = 0
        elif entry[0]['dz'] == 'N/A':
          ez_rate_asset = 100
        else:
          ez_rate_asset = round((int(entry[0]['ez']) * 100) / (int(entry[0]['ez']) + int(entry[0]['dz'])))
        if not entry[0]['invest'] == 'N/A':
          i_cost_asset = float(entry[0]['invest'])
        else:
          i_cost_asset = 0
        if not entry[0]['occupancy'].split(" ")[0] == 'N/A':
          occupancy_asset = int(entry[0]['occupancy'].split(" ")[0])
        else:
          occupancy_asset = 0
        year_of_construction_asset = entry[0]['baujahr']
      else:
        if entry[0]['dz'] == 'N/A':
          if not entry[0]['ez'] == 'N/A':
            ez_total_comp += int(entry[0]['ez'])
            room_total_comp += int(entry[0]['ez'])
        elif not entry[0]['ez'] == 'N/A':
          ez_total_comp += int(entry[0]['ez'])
          room_total_comp += (int(entry[0]['ez']) + int(entry[0]['dz']))
        # if not entry[0]['invest'] == 'N/A':
        #   i_cost_comp += float(entry[0]['invest'])
        #   i_cost_comp_amount += 1
        # if not entry[0]['occupancy'] == 'N/A':
        #   occupancy_comp += float(entry[0]['occupancy'].split(" ")[0])
        #   occupancy_comp_amount += 1
        # if not entry[0]['baujahr'] == 'N/A':
        #   year_of_construction_comp += entry[0]['baujahr']
        #   year_of_construction_comp_amount += 1

    ez_weight_avg_comp = round(100 + (((ez_total_comp / room_total_comp) - 1) * 100))
    print(ez_weight_avg_comp)
      
    ###Old###
    # ez_rate_asset = 0
    # ez_rate_comp = 0
    # ez_comp_amount = 0
    # ez_rate_state = 0
    # ez_state_amount = 0
    # i_cost_asset = 0
    # i_cost_comp = 0
    # i_cost_comp_amount = 0
    # i_cost_state = 0
    # i_cost_state_amount = 0
    # occupancy_asset = 0
    # occupancy_comp = 0
    # occupancy_comp_amount = 0
    # occupancy_state = 0
    # occupancy_state_amount = 0
    # year_of_construction_asset = 0
    # year_of_construction_comp = 0
    # year_of_construction_comp_amount = 0
    # year_of_construction_state = 0
    # year_of_construction_state_amount = 0

    # home_facilities = []
    
    # for entry in data_comp_analysis_nh['data']:
    #   if entry[len(entry) - 1] == 'home':
    #     home_facilities.append(entry)
    #     if entry[0]['ez'] == 'N/A':
    #       ez_rate_asset = 0
    #     elif entry[0]['dz'] == 'N/A':
    #       ez_rate_asset = 100
    #     else:
    #       ez_rate_asset = round((int(entry[0]['ez']) * 100) / (int(entry[0]['ez']) + int(entry[0]['dz'])))
    #     i_cost_asset = float(entry[0]['invest'])
    #     occupancy_asset = int(entry[0]['occupancy'].split(" ")[0])
    #     year_of_construction_asset = entry[0]['baujahr']
    #   else:
    #     if entry[0]['dz'] == 'N/A':
    #       if not entry[0]['ez'] == 'N/A':
    #         print(entry[0]['ez'])
    #         print('##############################')
    #         ez_rate_comp += 100
    #         ez_comp_amount += int(entry[0]['ez'])
    #     elif not entry[0]['ez'] == 'N/A':
    #       print(entry[0]['ez'])
    #       print(entry[0]['dz'])
    #       ez_rate_comp += round((int(entry[0]['ez']) * 100) / (int(entry[0]['ez']) + int(entry[0]['dz'])))
    #       ez_comp_amount += int(entry[0]['ez'])
    #       print(round((int(entry[0]['ez']) * 100) / (int(entry[0]['ez']) + int(entry[0]['dz']))))
    #       print('##############################')
    #     if not entry[0]['invest'] == 'N/A':
    #       i_cost_comp += float(entry[0]['invest'])
    #       i_cost_comp_amount += 1
    #     if not entry[0]['occupancy'] == 'N/A':
    #       occupancy_comp += float(entry[0]['occupancy'].split(" ")[0])
    #       occupancy_comp_amount += 1
    #     if not entry[0]['baujahr'] == 'N/A':
    #       year_of_construction_comp += entry[0]['baujahr']
    #       year_of_construction_comp_amount += 1

    # if not ez_comp_amount == 0:
    #   ez_rate_comp = round(ez_rate_comp / ez_comp_amount)
    # else:
    #   ez_rate_comp = 0
    # if not i_cost_comp_amount == 0:
    #   i_cost_comp = round(i_cost_comp / i_cost_comp_amount, 2)
    # else:
    #   i_cost_comp = 0
    # if not occupancy_comp_amount == 0:
    #   occupancy_comp = round(occupancy_comp /occupancy_comp_amount)
    # else:
    #   occupancy_comp = 0
    # if not year_of_construction_comp_amount == 0:
    #   year_of_construction_comp = round(year_of_construction_comp / year_of_construction_comp_amount)
    # else:
    #   year_of_construction_comp = 0

    # nursing_homes_federal_state = anvil.server.call('get_nursing_homes_federal_states', federal_state)

    # home = False
    # for nursing_home in nursing_homes_federal_state:
    #   # print(nursing_home)
    #   for facility in home_facilities:
    #     if facility[0]['name'] == nursing_home['name']:
    #       home = True
    #   if not home:
    #     if not nursing_home['ez'] == '-':
    #       ez_rate_state += int(nursing_home['ez'])
    #       ez_state_amount += 1
    #     if not nursing_home['invest'] == '-':
    #       i_cost_state += float(nursing_home['invest'])
    #       i_cost_state_amount += 1
    #     if not nursing_home['anz_vers_pat'] == '-' and not nursing_home['platz_voll_pfl'] == '-':
    #       occupancy_state += float((int(nursing_home['anz_vers_pat']) * 100) / int(nursing_home['platz_voll_pfl']))
    #       occupancy_state_amount += 1
    #     if not nursing_home['baujahr'] == '-':
    #       year_of_construction_state += int(nursing_home['baujahr'])
    #       year_of_construction_state_amount += 1
    #   else:
    #     home = False

    # if not ez_state_amount == 0:
    #   ez_rate_state = round(ez_rate_state / ez_state_amount)
    # else:
    #   ez_rate_state = 0
    # if not i_cost_state_amount == 0:
    #   i_cost_state = round(i_cost_state / i_cost_state_amount, 2)
    # else:
    #   i_cost_state = 0
    # if not occupancy_state_amount == 0:
    #   occupancy_state = round(occupancy_state /occupancy_state_amount)
    # else:
    #   occupancy_state = 0
    # if not year_of_construction_state_amount == 0:
    #   year_of_construction_state = round(year_of_construction_state / year_of_construction_state_amount)
    # else:
    #   year_of_construction_state = 0
    
    # print('###### Asset ######')
    # print(f'ez_rate_asset: {ez_rate_asset}')
    # print(f'i_cost_asset: {i_cost_asset}')
    # print(f'occupancy_asset: {occupancy_asset}')
    # print(f'year_of_construction_asset: {year_of_construction_asset}')
    # print('###### Competitors ######')
    # print(f'ez_rate_comp: {ez_rate_comp}')
    # print(f'ez_comp_amount: {ez_comp_amount}')
    # print(f'i_cost_comp: {i_cost_comp}')
    # print(f'i_cost_comp_amount: {i_cost_comp_amount}')
    # print(f'occupancy_comp: {occupancy_comp}')
    # print(f'occupancy_comp_amount: {occupancy_comp_amount}')
    # print(f'year_of_construction_comp: {year_of_construction_comp}')
    # print(f'year_of_construction_comp_amount: {year_of_construction_comp_amount}')
    # print('###### Federal State ######')
    # print(f'ez_rate_state: {ez_rate_state}')
    # print(f'ez_state_amount: {ez_state_amount}')
    # print(f'i_cost_state: {i_cost_asset}')
    # print(f'i_cost_comp_amount: {i_cost_state_amount}')
    # print(f'occupancy_state: {occupancy_state}')
    # print(f'occupancy_state_amount: {occupancy_state_amount}')
    # print(f'year_of_construction_state: {year_of_construction_state}')
    # print(f'year_of_construction_state_amount: {year_of_construction_state_amount}')
      
  ##### Analysis Addition to Market Study #####
    
    anvil.server.call('create_iso_map', Variables.activeIso, Functions.create_bounding_box(self), unique_code)
    anvil.server.call('write_excel_file', mapRequestData, bbox, unique_code, data_comp_analysis_nh['request'] , data_comp_analysis_al['request'] ,cover_frame, summary_frame, nurscomp_frame, assliv_frame, alca_frame, nh_checked, al_checked, Variables.tm_mode, checkboxes)

    if not Variables.tm_mode:
      #Create Charts and Static Map for Analysis
      values_pie_ca = [{"topic": "Median Nursing charge (PG 3) in €", "value": pg3_median}, {"topic": "Median Specific co-payment in €", "value": copayment_median}, {"topic": "Median Invest Cost in €", "value": invest_median}, {"topic": "Median Board and lodging in €", "value": board_median}]
      anvil.server.call("create_pie_chart", values_pie_ca, f"donut_ca_{unique_code}", 'donut_ca')
      values_pie_sum = [{"topic": "% Public operators", "value": len(operator_public)}, {"topic": "% Non-profit operators", "value": len(operator_nonProfit)}, {"topic": "% Private operators", "value": len(operator_private)}]
      anvil.server.call("create_pie_chart", values_pie_sum, f"donut_sum_{unique_code}", 'other_donut')
      values_bar_sum = [{"topic": "Number of inpatients", "value": inpatients}, {"topic": "Beds", "value": beds_active}, {"topic": "Number of inpatients forecast 2030 Scenario 1", "value": inpatients_fc}, {"topic": "Adjusted number of beds<br>(incl. beds in planning and under construction) 2030", "value": beds_adjusted}, {"topic": "Number of inpatients forecast 2035 Scenario 1", "value": inpatients_fc_35}, {"topic": "Adjusted number of beds<br>(incl. beds in planning and under construction) 2035", "value": beds_adjusted}]
      anvil.server.call("create_bar_chart", values_bar_sum, f"bar_v1_{unique_code}")
      values_bar_sum = [{"topic": "Number of inpatients", "value": inpatients}, {"topic": "Beds", "value": beds_active}, {"topic": "Number of inpatients forecast 2030 Scenario 2", "value": inpatients_fc_v2}, {"topic": "Adjusted number of beds<br>(incl. beds in planning and under construction) 2030", "value": beds_adjusted}, {"topic": "Number of inpatients forecast 2035 Scenario 2", "value": inpatients_fc_35_v2}, {"topic": "Adjusted number of beds<br>(incl. beds in planning and under construction) 2035", "value": beds_adjusted}]
      anvil.server.call("create_bar_chart", values_bar_sum, f"bar_v2_{unique_code}")
      anvil.server.call("create_bar_chart", [{"topic": f"{countie[0]}, LK 2022", "value": demand2022}, {"topic": f"{countie[0]}, LK 2030", "value": demand2040}], f"bar_al_{unique_code}")
      
      #Create Data-Objects for Summary
      sendData_Summary = {"zipcode": zipcode,
                          "city": city,
                          "district": district,
                          "federal_state": federal_state,
                          "time": time,
                          "movement": movement,
                          "countie": countie[0],
                          "population": "{:,}".format(countie_data['ex_dem_lk']['all_compl']),
                          "people_u80": "{:,}".format(people_u80),
                          "people_o80": "{:,}".format(people_o80),
                          "pat_rec_full_care": "{:,}".format(inpatients_lk),
                          "inpatients": "{:,}".format(inpatients),
                          "beds_active": "{:,}".format(beds_active),
                          "nursing_homes_active": nursing_homes_active,
                          "nursing_homes_planned": nursing_homes_planned,
                          "nursing_homes_construct": nursing_homes_construct,
                          "beds_planned": "{:,}".format(beds_planned),
                          "beds_construct": "{:,}".format(beds_construct),
                          "beds_adjusted": "{:,}".format(beds_adjusted),
                          "occupancy_percent": occupancy_percent,
                          "invest_median": invest_median,
                          "operator": len(operator),
                          "beds_median": beds_median,
                          "year_median": year_median,
                          "op_public_percent": op_public_percent,
                          "op_nonProfit_percent": op_nonProfit_percent,
                          "op_private_percent": op_private_percent,
                          "people_u80_fc": "{:,}".format(people_u80_fc),
                          "change_u80": "{:,}".format(change_u80),
                          "change_o80": "{:,}".format(change_o80),
                          "people_o80_fc": "{:,}".format(people_o80_fc),
                          "pat_rec_full_care_fc": "{:,}".format(pat_rec_full_care_fc_30_v1),
                          "inpatients_fc": "{:,}".format(inpatients_fc),
                          "beds_surplus": "{:,}".format(beds_surplus),
                          "without_apartment": without_apartment,
                          "change_pat_rec": "{:,}".format(change_pat_rec),
                          "city_population": "{:,}".format(countie_data['dem_city']['bevoelkerung_ges']),
                          "occupancy_lk": "{:,}".format(occupancy_lk),
                          "people_u80_fc_35": "{:,}".format(people_u80_fc_35),
                          "people_o80_fc_35": "{:,}".format(people_o80_fc_35),
                          "pat_rec_full_care_fc_35": "{:,}".format(pat_rec_full_care_fc_35_v1),
                          "nursing_home_rate": nursing_home_rate_perc,
                          "care_rate": new_care_rate_perc,
                          "pat_rec_full_care_fc_s2": "{:,}".format(pat_rec_full_care_fc_30_v2),
                          "care_rate_v2": care_rate_30_v2_perc,
                          "nh_rate_30": care_rate_30_v1_perc,
                          "care_rate_v2_35": care_rate_35_v2_perc,
                          "population_30": "{:,}".format(population_fc),
                          "population_35": "{:,}".format(population_fc_35),
                          "nh_rate_35": care_rate_35_v1_perc,
                          "pat_rec_full_care_fc_35_s2": "{:,}".format(pat_rec_full_care_fc_35_v2),
                          "inpatients_fc_35": "{:,}".format(inpatients_fc_35),
                          "inpatients_fc_v2": "{:,}".format(inpatients_fc_v2),
                          "inpatients_fc_35_v2": "{:,}".format(inpatients_fc_35_v2),
                          "beds_surplus_35": "{:,}".format(beds_surplus_35),
                          "beds_surplus_v2": "{:,}".format(beds_surplus_v2),
                          "beds_surplus_35_v2": "{:,}".format(beds_surplus_35_v2),
                          "care_rate_break_even_perc": care_rate_break_even_perc,
                          "care_rate_break_even_30_perc": care_rate_break_even_30_perc,
                          "care_rate_break_even_35_perc": care_rate_break_even_35_perc,
                          "beds_surplus_v2": beds_surplus_v2,
                          "beds_surplus_35_v2": beds_surplus_35_v2,
                          "beds_lk": "{:,}".format(beds_lk),
                          "free_beds_lk" : "{:,}".format(free_beds_lk),
                          "beds_in_reserve_20": "{:,}".format(beds_in_reserve_20),
                          "beds_in_reserve_fc": "{:,}".format(beds_in_reserve_fc),
                          "free_beds_30_v1": "{:,}".format(free_beds_30_v1),
                          "free_beds_30_v2": "{:,}".format(free_beds_30_v2),
                          "free_beds_35_v1": "{:,}".format(free_beds_35_v1),
                          "free_beds_35_v2": "{:,}".format(free_beds_35_v2),
                          "beds_30_v1": "{:,}".format(beds_30_v1),
                          "beds_30_v2": "{:,}".format(beds_30_v2),
                          "beds_35_v1": "{:,}".format(beds_35_v1),
                          "beds_35_v2": "{:,}".format(beds_35_v2),
                          "inpatents_fc_30_avg": "{:,}".format(inpatents_fc_30_avg),
                          "inpatents_fc_35_avg": "{:,}".format(inpatents_fc_35_avg),
                          "beds_surplus_30_avg": "{:,}".format(beds_surplus_30_avg),
                          "beds_surplus_35_avg": "{:,}".format(beds_surplus_35_avg),
                          "searched_address": searched_address,
                          "nh_checked": nh_checked}
      sendData_ALAnalysis = {"countie": countie[0],
                            "population": "{:,}".format(countie_data['ex_dem_lk']['all_compl']),
                            "people_u80": "{:,}".format(people_u80),
                            "people_o80": "{:,}".format(people_o80),
                            "apartments": "{:,}".format(apartments),
                            "apartments_per_10k": "{:,}".format(apartments_per_10k),
                            "people_u80_fc": "{:,}".format(people_u80_fc),
                            "people_o80_fc": "{:,}".format(people_o80_fc),
                            "change_u80": change_u80,
                            "change_o80": change_o80,
                            "facilities_active": "{:,}".format(facilities_active),
                            "facilities_plan_build": "{:,}".format(facilities_plan_build),
                            "apartments_plan_build": "{:,}".format(apartments_plan_build),
                            "facilities_10km": "{:,}".format(len(al_list)),
                            "apartments_10km": "{:,}".format(apartments_10km),
                            "with_apartment": "{:,}".format(facilities_active - without_apartment),
                            "without_apartment": "{:,}".format(without_apartment),
                            "apartments_adjusted": "{:,}".format(apartments_adjusted),
                            "facilities_building": "{:,}".format(facilities_building),
                            "with_apartment_building": "{:,}".format(facilities_building - without_apartment_building),
                            "without_apartment_building": "{:,}".format(without_apartment_building),
                            "apartments_building": "{:,}".format(apartments_building),
                            "build_apartments_average": "{:,}".format(build_apartments_average),
                            "build_apartments_adjusted": "{:,}".format(build_apartments_adjusted),
                            "apartments_planning": "{:,}".format(apartments_planning),
                            "without_apartment_planning": "{:,}".format(without_apartment_planning),
                            "facilities_planning": "{:,}".format(facilities_planning),
                            "planning_apartments_average": "{:,}".format(planning_apartments_average),
                            "planning_apartments_adjusted": "{:,}".format(planning_apartments_adjusted),
                            "average_with_apartments": "{:,}".format(apartments_average),
                            "planned_with_apartments": "{:,}".format(facilities_planning - without_apartment_planning),
                            "total_facility": "{:,}".format(facilities_active + facilities_building + facilities_planning),
                            "total_apartments": "{:,}".format(apartments + (facilities_building - without_apartment_building) + apartments_planning),
                            "total_apartments_adjusted": "{:,}".format(apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted),
                            "demand_1_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.01) / 1.5)),
                            "demand_1_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.01) / 1.5)),
                            "demand_1_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.01) / 1.5)),
                            "demand_1_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.01) / 1.5)))),
                            "demand_2_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.02) / 1.5)),
                            "demand_2_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.02) / 1.5)),
                            "demand_2_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.02) / 1.5)),
                            "demand_2_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.02) / 1.5)))),
                            "demand_3_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.03) / 1.5)),
                            "demand_3_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.03) / 1.5)),
                            "demand_3_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.03) / 1.5)),
                            "demand_3_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.03) / 1.5)))),
                            "demand_4_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.04) / 1.5)),
                            "demand_4_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.04) / 1.5)),
                            "demand_4_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.04) / 1.5)),
                            "demand_4_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.04) / 1.5)))),
                            "demand_5_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.05) / 1.5)),
                            "demand_5_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.05) / 1.5)),
                            "demand_5_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.05) / 1.5)),
                            "demand_5_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.05) / 1.5)))),
                            "demand_7_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.07) / 1.5)),
                            "demand_7_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.07) / 1.5)),
                            "demand_7_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.07) / 1.5)),
                            "demand_7_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.07) / 1.5)))),
                            "demand_9_2022": "{:,}".format(round(((people_u80 + people_o80) * 0.09) / 1.5)),
                            "demand_9_2022_surplus": "{:,}".format(apartments_adjusted - round(((people_u80 + people_o80) * 0.09) / 1.5)),
                            "demand_9_2040": "{:,}".format(round(((people_u80_fc + people_o80_fc) * 0.09) / 1.5)),
                            "demand_9_2040_surplus": "{:,}".format(round((apartments_adjusted + build_apartments_adjusted + planning_apartments_adjusted) - (round(((people_u80_fc + people_o80_fc) * 0.09) / 1.5)))),
                            "level": level,
                            "surplus_2022": surplus2022,
                            "demand_2022": demand2022,
                            "surplus_2040": surplus2040,
                            "demand_2040": demand2040,
                            "demand_potential": demand_potential,
                            "apartments_plan_build_adjusted": apartments_plan_build_adjusted,
                            "change_pat_rec": change_pat_rec,
                            "city": city,
                            "al_checked": al_checked}
      
      #Create Summary-PDF
      anvil.server.call("write_pdf_file", sendData_Summary, mapRequestData, sendData_ALAnalysis, unique_code, bbox, data_comp_analysis_nh['data'], data_comp_analysis_nh['request'], data_comp_analysis_al['data'], data_comp_analysis_al['request'], checkboxes)
    
    #Get PDF from Table and start Download
    table = app_tables.pictures.search()
    mapPDF = app_tables.pictures.search()[1]
    mapExcel = app_tables.pictures.search()[0]
    anvil.media.download(mapPDF['pic'])
    anvil.media.download(mapExcel['pic'])
    Variables.unique_code = unique_code

  
  def upload_mspdf_change(self, file, **event_args):
    #This method is called when the Dropdown-Menu has changed
    folder = app_files.market_studies
    file = folder.create_file(f"market_study_{Variables.unique_code}", file)
    anvil.js.call('show_mun_info', f'<h1>Google Drive Share Link for Market Study PDF</h1><br><br><p id="toCopyText">{file._obj["alternateLink"]}</p><br><button type="button" onClick="copy_to_clipboard()">Copy Link</button><br><br><button type="button" onClick="hide_mun_info()">&#10006;</button>')
    self.upload_mspdf.clear()
    
#####  Button Functions   #####
###############################
#####  Dropdown Functions #####

  def distance_dropdown_change(self, **event_args):
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    
    Functions.refresh_icons(self)
  
  #####  Dropdown Functions #####
  ###############################
  #####  Upload Functions   #####

  #This method is called when a new file is loaded into the FileLoader
  def file_loader_upload_change(self, file, **event_args):  
    #Call Server-Function to safe the File  
    self.cluster_data = anvil.server.call('save_local_excel_file', file)
    
    if self.cluster_data == None:
      alert('Irgendwas ist schief gelaufen. Bitte Datei neu hochladen!')
    else:
      #Initialise Variables
      excel_markers = {}
      added_clusters = []
      colors = ['blue', 'green', 'grey', 'lightblue', 'orange', 'pink', 'red', 'white', 'yellow', 'gold']
  
      #Create Settings
      self.icon_grid.row_spacing = 0
      
      for asset in self.cluster_data:
  
        # Create HTML Element for Icon
        el = document.createElement('div')
        el.className = f'{asset["address"]}'
        el.style.width = '40px'
        el.style.height = '40px'
        el.style.backgroundSize = '100%'
        el.style.backgroundrepeat = 'no-repeat'
        el.style.zIndex = '9001'
  
        cluster_name = asset['cluster']
  
        if cluster_name not in added_clusters:
          color = alert(content=Color_for_Cluster(cluster=cluster_name, colors=colors), large=True, buttons=[], dismissible=False)
          colors.remove(color[0])
          checkbox = CheckBox(checked=True, text=cluster_name, spacing_above='none', spacing_below='none')
          checkbox.add_event_handler('change', self.check_box_marker_icons_change)
          icon = Label(icon='fa:circle', foreground=color[1], spacing_above='none', spacing_below='none')
          self.icon_grid.add_component(checkbox, row=cluster_name, col_xs=0, width_xs=8)
          self.icon_grid.add_component(icon, row=cluster_name, col_xs=8, width_xs=1)
          added_clusters.append(cluster_name)
  
        # #Get Coordinates of provided Adress for Marker
        req_str = self.build_request_string(asset)
        req_str += f'.json?access_token={self.token}'
        coords = anvil.http.request(req_str,json=True)
        coordinates = coords['features'][0]['geometry']['coordinates']
  
        if not cluster_name in excel_markers.keys():
          excel_markers[cluster_name] = {'color': color, 'static': 'none', 'marker': []}
        el.style.backgroundImage = f'url({excel_markers[cluster_name]["color"][2]})'
        new_list = self.set_excel_markers(excel_markers[cluster_name]['static'], coordinates, excel_markers[cluster_name]['marker'], el)
        excel_markers[cluster_name]['marker'] = new_list
        
        # Create Popup for Marker and add it to the Map
        # popup = mapboxgl.Popup({'closeOnClick': False, 'offset': 25})
        # popup.setHTML(data[0][markercount]['Informationen'])
        # popup_static = mapboxgl.Popup({'closeOnClick': False, 'offset': 5, 'className': 'static-popup', 'closeButton': False, 'anchor': 'top'}).setText(data[0][markercount]['Informationen']).setLngLat(coords['features'][0]['geometry']['coordinates'])
        # popup_static.addTo(self.mapbox)
        
        #Increase Markercount
        # markercount += 1
        
      # Add Marker-Arrays to global Variable Marker
      Variables.marker.update(excel_markers)
  
      self.hide_marker.enabled = True
      self.change_cluster_color.enabled = True
    
  #####  Upload Functions   #####
  ###############################
  #####   Extra Functions   #####
  
  #This method is called when the Geocoder was used 
  def move_marker(self, result):
  
    #Set iso-Layer for new coordinates
    lnglat = result['result']['geometry']['coordinates']
    self.marker.setLngLat(lnglat)
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    
    Functions.refresh_icons(self)
  
  #This method is called when the draggable Marker was moved
  def marker_dragged(self, drag):
  
    #Set iso-Layer for new Markerposition
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    
    Functions.refresh_icons(self)
    
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
                            'layout': {'visibility': 'visible'},
                            'paint': {
                            'fill-color': '#A6A18A',
                            'fill-opacity': 0.3,
                            'fill-outline-color': '#4D4A3F'
                            },
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
    if click.features[0].layer.source == 'federal_states':
      
      #Create Popup and add it to the Map
      bl_name = click.features[0].properties.name
      bl_id = click.features[0].id
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}').addTo(self.mapbox)
    
    #Check which Layer is active
    elif click.features[0].layer.source == 'administrative_districts':
      
      #Create Popup and add it to the Map
      bl_name = click.features[0].properties.NAME_1
      rb_name = click.features[0].properties.NAME_2
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}<br><b>Regierungsbezirk:</b> {rb_name}').addTo(self.mapbox)
    
    #Check which Layer is active
    elif click.features[0].layer.source == 'counties':
      
      #Create Popup and add it to the Map
      bl_name = click.features[0].properties.lan_name
      lk_name = click.features[0].properties.krs_name
      clicked_lngLat = dict(click.lngLat)
      popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bundesland:</b> {bl_name}<br><b>Landkreis:</b> {lk_name}').addTo(self.mapbox)
  
    elif click.features[0].layer.source == 'municipalities':
      
      if hasattr(click.features[0].properties, 'GEN'):
        
        gm_name = click.features[0].properties.GEN
        
      else:
        
        gm_name = click.features[0].properties.name
      
      key = click.features[0].properties.AGS
      demographic, exact_demographic = anvil.server.call('get_data_from_database', key)
      print(demographic)
      print(exact_demographic)
    
      popup_text = f'<button type="button" onClick="hide_mun_info()">&#10006;</button><br><br><h3>Municipality: {gm_name}</h3><b>ID:</b> {key}<br><b>Area:</b> {"{:.2f}".format(float(demographic["flaeche"]))}km&sup2;<br><br><b>Population:</b> {demographic["bevoelkerung_ges"]}<br><b>per km&sup2:</b> {demographic["bevoelkerung_jekm2"]}<br><br><table><tr><th class="firstCol">Gender</th><th>Overall</th><th>Under 3</th><th>3 to <br>Under 6</th><th>6 to <br>Under 10</th><th>10 to Under 15</th><th>15 to Under 18</th><th>18 to Under 20</th><th>20 to Under 25</th><th>25 to Under 30</th><th>30 to Under 35</th><th>35 to Under 40</th><th>40 to Under 45</th><th>45 to Under 50</th><th>50 to Under 55</th><th>55 to Under 60</th><th>60 to Under 65</th><th>65 to Under 75</th><th>75 and older</th></tr><tr><th class="firstCol">Overall</th><td>100%</td><td>{"{:.1f}".format(float(exact_demographic["all_u3"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_3tou6"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_6tou10"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_10tou15"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_15tou18"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_18tou20"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_20tou25"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_25tou30"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_30tou35"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_35tou40"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_40tou45"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_45tou50"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_50tou55"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_55tou60"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_60tou65"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_65tou75"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_75"]))}%</td></tr><tr><th class="firstCol">Male</th><td>{"{:.1f}".format(float(exact_demographic["man_compl"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_u3"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_3tou6"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_6tou10"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_10tou15"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_15tou18"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_18tou20"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_20tou25"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_25tou30"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_30tou35"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_35tou40"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_40tou45"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_45tou50"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_50tou55"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_55tou60"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_60tou65"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_65tou75"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_75"]))}%</td></tr><tr><th class="firstCol">Female</th><td>{"{:.1f}".format(float(exact_demographic["woman_compl"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_u3"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_3tou6"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_6tou10"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_10tou15"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_15tou18"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_18tou20"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_20tou25"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_25tou30"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_30tou35"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_35tou40"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_40tou45"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_45tou50"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_50tou55"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_55tou60"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_60tou65"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_65tou75"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_75"]))}%</td></tr></table><br><br><br><b>Grad der Verstädterung:</b> {demographic["verstaedterung_bez"]}'
      
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
    
    layers = [{'id_fill': 'federal_states',
               'id_outline': 'outline_federal_states', 
               'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json',
               'line_width': 2}, 
              {'id_fill': 'administrative_districts',
               'id_outline': 'outline_administrative_districts', 
               'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/3_regierungsbezirke/1_sehr_hoch.geo.json',
               'line_width': 1},
             {'id_fill': 'counties',
               'id_outline': 'outline_counties', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/landkreise.geojson',
               'line_width': 0.5},
             {'id_fill': 'municipalities',
               'id_outline': 'outline_municipalities', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/municipalities.geojson',
               'line_width': 0.5},
             {'id_fill': 'districts',
               'id_outline': 'outline_districts', 
               'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/bln_hh_mun_dist.geojson',
               'line_width': 0.5},
             {'id_fill': 'netherlands',
               'id_outline': 'outline_netherlands', 
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
  
    self.mapbox.setLayoutProperty(Variables.activeLayer, 'visibility', 'visible')
    self.mapbox.setLayoutProperty(f'outline_{Variables.activeLayer}', 'visibility', 'visible')
  
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
          if category == 'nursing_homes':
            geojson = anvil.server.call('get_care_db_data', bbox, 'Pflegeheime')
            Variables.nursing_homes_entries = geojson
        
          elif category == 'assisted_living':
    
            geojson = anvil.server.call('get_care_db_data', bbox, 'BetreutesWohnen')
            Variables.assisted_living_entries = geojson

          elif category == 'nursing-schools':

            geojson = anvil.server.call('get_einrichtungen', bbox)
    
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
              el.style.width = '40px'
              el.style.height = '40px'
              el.style.backgroundSize = '100%'
              el.style.backgroundrepeat = 'no-repeat'
    
              # Create Icon
              el.style.backgroundImage = f'url({picture})'
    
              # Check if Category is not PflegeDB
              if not category == 'nursing_homes':
          
                if not category == 'assisted_living':

                  if not category == 'nursing-schools':
                  
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

                  else:

                    name = ele['name']
                    street = ele['street']
                    postcode = ele['postcode']
                    city = ele['city']
                    telefon = ele['telefon']
                    email = ele['email']
                    web = ele['web']
                    degree = ele['degree']
                    parttime_education = ele['parttime-education']
                    certificate = ele['certificate']
                    district_code = ele['district-code']
                    inserted = ele['inserted']
                    updated = ele['updated']
                    el_coords = [ ele['longitude'], ele['lattitude'] ]
    
              # Check if Category is Bus or Tram
              if category == 'bus_stop' or category == 'tram_stop':
    
                # Create Popup for Element
                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f'<b>Name:</b>'
                  f'<br>'
                  f'&nbsp;&nbsp;{name}'
                )
                
              # Check if Category is PflegeDB
              elif category == 'nursing_homes':
    
                el_coords = [ele['coord_lon'], ele['coord_lat']]
    
                # Create Popup for Element
                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f"<b>PM ID: </b> {ele['pm_id']}"
                  "<br>"
                  f"<b>Träger ID: </b> {ele['traeger_id']}"
                  "<br>"
                  f"<b>IK_Nummer: </b> {ele['ik_nummer']}"
                  "<br>"
                  "<br>"
                  f"<b>Sektor: </b> {ele['sektor']}"
                  "<br>"
                  f"<b>Art: </b> {ele['art']}"
                  "<br>"
                  f"<b>Spezialisierung: </b> {ele['spezialisierung']}"
                  "<br>"
                  f"<b>Status: </b> {ele['status']}"
                  "<br>"
                  f"<b>Baujahr: </b> {ele['baujahr']}"
                  "<br>"
                  f"<b>Modernisierungsjahr: </b> {ele['modernisierung']}"
                  "<br>"
                  "<br>"
                  f"<b>Name: </b> {ele['name']}"
                  "<br>"
                  "<br>"
                  f"<b>Betreiber: </b> {ele['betreiber']}"
                  "<br>"
                  f"<b>Tochterfirma 1: </b> {ele['tochterfirma1']}"
                  "<br>"
                  f"<b>Tochterfirma 2: </b> {ele['tochterfirma2']}"
                  "<br>"
                  "<br>"
                  f"<b>Straße: </b> {ele['strasse']}"
                  "<br>"
                  f"<b>Postleitzahl: </b> {ele['plz']}"
                  "<br>"
                  f"<b>Ort: </b> {ele['ort']}"
                  "<br>"
                  f"<b>Bundesland: </b> {ele['bundesland']}"
                  "<br>"
                  f"<b>Gemeindeschlüssel: </b> {ele['gemeindeschluessel']}"
                  "<br>"
                  "<br>"
                  f"<b>Telefon: </b> {ele['telefon']}"
                  "<br>"
                  f"<b>Fax: </b> {ele['fax']}"
                  "<br>"
                  f"<b>E-Mail: </b> {ele['email']}"
                  "<br>"
                  f"<b>Webseite: </b> {ele['webseite']}"
                  "<br>"
                  f"<b>Domain: </b> {ele['domain']}"
                  "<br>"
                  "<br>"
                  f"<b>MDK Datum: </b> {ele['mdk_datum']}"
                  "<br>"
                  f"<b>Pflege und medizinische Versorgung: </b> {ele['pfl_u_med_vers']}"
                  "<br>"
                  f"<b>Umgang mit demenzkranken Bewohnern: </b> {ele['umg_mit_dem_bew']}"
                  "<br>"
                  f"<b>Soziale Betreuung und Alltagsgestaltung: </b> {ele['soz_betrualltag']}"
                  "<br>"
                  f"<b>Wohnen, Verpflegung, Hauswirtschaft und Hygiene: </b> {ele['wohn_verpfl_hausw_hyg']}"
                  "<br>"
                  f"<b>Befragung der Bewohner: </b> {ele['befr_bew']}"
                  "<br>"
                  f"<b>MDK Note: </b> {ele['mdk_note']}"
                  "<br>"
                  "<br>"
                  f"<b>Anzahl versorgte Patienten: </b> {ele['anz_vers_pat']}"
                  "<br>"
                  f"<b>Platzzahl vollständige Pflege: </b> {ele['platz_voll_pfl']}"
                  "<br>"
                  f"<b>Platzzahl Kurzzeitpflege: </b> {ele['platz_kurzpfl']}"
                  "<br>"
                  f"<b>Platzzahl Nachtpflege: </b> {ele['platz_nachtpfl']}"
                  "<br>"
                  f"<b>Einzelzimmer: </b> {ele['ez']}"
                  "<br>"
                  f"<b>Doppelzimmer: </b> {ele['dz']}"
                  "<br>"
                  "<br>"
                  f"<b>Ausbildungsumlage: </b> {ele['ausbildungsumlage']}"
                  "<br>"
                  f"<b>EEE: </b> {ele['eee']}"
                  "<br>"
                  f"<b>UuV: </b> {ele['uuv']}"
                  "<br>"
                  f"<b>Invest: </b> {ele['invest']}"
                  "<br>"
                  f"<b>PG 1: </b> {ele['pg_1']}"
                  "<br>"
                  f"<b>PG 2: </b> {ele['pg_2']}"
                  "<br>"
                  f"<b>PG 3: </b> {ele['pg_3']}"
                  "<br>"
                  f"<b>PG 4: </b> {ele['pg_4']}"
                  "<br>"
                  f"<b>PG 5: </b> {ele['pg_5']}"
                )
    
              elif category == 'assisted_living':

                el_coords = [ele['coord_lon'], ele['coord_lat']]
                wohnungen = "N.A." if ele['anz_wohnungen'] == "-" else ele['anz_wohnungen']
                ez = "N.A." if ele['ez'] == "-" else ele['ez']
                dz = "N.A." if ele['dz'] == "-" else ele['dz']
                miete_ab = "N.A." if ele['miete_ab'] == "-" else f"{ele['miete_ab']} €"
                miete_bis = "N.A." if ele['miete_bis'] == "-" else f"{ele['miete_bis']} €"
    
                # Create Popup for Element
                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f"<b>PM ID: </b> {ele['pm_id']}"
                  "<br>"
                  f"<b>Träger ID: </b> {ele['traeger_id']}"
                  "<br>"
                  "<br>"
                  f"<b>Sektor: </b> {ele['sektor']}"
                  "<br>"
                  f"<b>Art: </b> {ele['art']}"
                  "<br>"
                  f"<b>Spezialisierung: </b> {ele['spezialisierung']}"
                  "<br>"
                  f"<b>Status: </b> {ele['status']}"
                  "<br>"
                  f"<b>Baujahr: </b> {ele['baujahr']}"
                  "<br>"
                  "<br>"
                  f"<b>Name: </b> {ele['name']}"
                  "<br>"
                  "<br>"
                  f"<b>Betreiber: </b> {ele['betreiber']}"
                  "<br>"
                  f"<b>Tochterfirma 1: </b> {ele['tochterfirma1']}"
                  "<br>"
                  f"<b>Tochterfirma 2: </b> {ele['tochterfirma2']}"
                  "<br>"
                  "<br>"
                  f"<b>Straße: </b> {ele['strasse']}"
                  "<br>"
                  f"<b>Postleitzahl: </b> {ele['plz']}"
                  "<br>"
                  f"<b>Ort: </b> {ele['ort']}"
                  "<br>"
                  f"<b>Bundesland: </b> {ele['bundesland']}"
                  "<br>"
                  f"<b>Gemeindeschlüssel: </b> {ele['gemeindeschluessel']}"
                  "<br>"
                  "<br>"
                  f"<b>Telefon: </b> {ele['telefon']}"
                  "<br>"
                  f"<b>Fax: </b> {ele['fax']}"
                  "<br>"
                  f"<b>E-Mail: </b> {ele['email']}"
                  "<br>"
                  f"<b>Webseite: </b> {ele['webseite']}"
                  "<br>"
                  f"<b>Domain: </b> {ele['domain']}"
                  "<br>"
                  "<br>"
                  f"<b>Anzahl Wohnungen: </b> {wohnungen}"
                  "<br>"
                  f"<b>Einzelzimmer: </b> {ez}"
                  "<br>"
                  f"<b>Doppelzimmer: </b> {dz}"
                  "<br>"
                  f"<b>Miete ab: </b> {miete_ab}"
                  "<br>"
                  f"<b>Miete bis: </b> {miete_bis}"
                )

              elif category == 'nursing-schools':

                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f'<b>Name:</b>'
                  f'<br>'
                  f'&nbsp;&nbsp;{name}'
                  f'<b>Adresse:</b>'
                  f'<br>'
                  f'&nbsp;&nbsp;{street}'
                  f'<br>'
                  f'&nbsp;&nbsp;{postcode}, {city}'
                  f'<br>'
                  f'&nbsp;&nbsp;district code: {district_code}'
                  f'<br>'
                  f'<b>Kontakt</b>'
                  f'<br>'
                  f'&nbsp;&nbsp;Telefon: {telefon}'
                  f'<br>'
                  f'&nbsp;&nbsp;Email: {email}'
                  f'<br>'
                  f'&nbsp;&nbsp;Webseite:'
                  f'<br>'
                  f'&nbsp;&nbsp;&nbsp;&nbsp;{web}'
                  f'<br>'
                  f'<b>Infos</b>'
                  f'<br>'
                  f'&nbsp;&nbsp;Degree: {degree}'
                  f'<br>'
                  f'&nbsp;&nbsp;parttime education: {parttime_education}'
                  f'br'
                  f'&nbsp;&nbsp;certificate: {certificate}'
                  f'<br>'
                  f'&nbsp;&nbsp;inserted: {inserted}'
                  f'<br>'
                  f'&nbsp;&nbsp;updated: {updated}'
                )
                
              # Check if Category is not Bus or Tram or PflegeDB
              else:
                
                # Create Popup for Element
                popup = mapboxgl.Popup({'offset': 25}).setHTML(
                  f'{name}'
                  '<br>'
                  f'{el_coords[0]}, {el_coords[1]}'
                  # f'<b>ID:</b> {o_id}'
                  # f'<br>'
                  # f'<b>Name:</b>'
                  # f'<br>'
                  # f'&nbsp;&nbsp;{name}'
                  # f'<br>'
                  # f'<b>Operator:</b>'
                  # f'<br>'
                  # f'&nbsp;&nbsp;{operator}'
                  # f'<br>'
                  # f'<b>Adresse:</b>'
                  # f'<br>'
                  # f'&nbsp;&nbsp;{street} {housenumber}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;{postcode}, {city} {suburb}'
                  # f'<br>'
                  # f'<b>Kontakt</b>'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Telefon: {phone}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Fax: {fax}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Email: {email}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Webseite:'
                  # f'<br>'
                  # f'&nbsp;&nbsp;&nbsp;&nbsp;{website}'
                  # f'<br>'
                  # f'<b>Infos</b>'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Kategorie: {healthcare}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Speciality: {speciality}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Öffnungszeiten:'
                  # f'<br>'
                  # f'&nbsp;&nbsp;&nbsp;&nbsp;{opening_hours}'
                  # f'<br>'
                  # f'&nbsp;&nbsp;Rollstuhlgerecht: {wheelchair}'
                )
    
              # Add Icon to the Map
              newicon = mapboxgl.Marker(el, {'anchor': 'bottom'}).setLngLat(el_coords).setOffset([0, 0]).addTo(self.mapbox).setPopup(popup)
              newiconElement = newicon.getElement()

              context = mapboxgl.Popup({'anchor': 'top', 'offset': 10}).setHTML(
                  '<button>Remove Marker</button>'
                )

              newicon.setPopup(context)
              
              anvil.js.call('addHoverEffect', newiconElement, popup, self.mapbox, context, newicon)
    
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
  
      # Do if Bounding Box is the same as last Request
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

      
  #This method is called from the file uploader to set Markers based on Excel-Data
  def set_excel_markers(self, marker_cat, coords, marker_list, el):

    marker_cat = mapboxgl.Marker({'draggable': False, 'element': el, 'anchor': 'bottom'})
    
    # Add Marker to the Map
    newmarker = marker_cat.setLngLat(coords).addTo(self.mapbox)

    # Add Marker Marker-Array
    marker_list.append(newmarker)
    return(marker_list)
    
  #This method is called when the Mouse is moved inside or out of an active Layer
  def change_hover_state(self, mouse):
    
    # Check if Layer is already hovered
    if Variables.hoveredStateId != None:
  
      # Change hover-State to False and set global-variable 'hoveredStateId' to None
      self.mapbox.setFeatureState({'source': Variables.activeLayer, 'id': Variables.hoveredStateId}, {'hover': False})
      
      Variables.hoveredStateId = None
    
    #Check if Mouse is moved inside Layer or out of Layer
    if hasattr(mouse, 'features'):
      
      # Check if Mouse was moved inside active Map-Layer
      if len(mouse.features) > 0:
      
        # Change global hoveredStateID to new active Layer-id
        Variables.hoveredStateId = mouse.features[0].id
    
        # Change hover-State to True
        self.mapbox.setFeatureState({'source': Variables.activeLayer, 'id': Variables.hoveredStateId}, {'hover': True})
  
  #Builds request-String for geocoder
  def build_request_string(self, asset):
    
    #Create basic request String
    request_string = f"https://api.mapbox.com/geocoding/v5/mapbox.places/"

    split_address = asset['map_address'].split(' ')
    street = split_address[0]
    housenumber = split_address[1]
    
    #Create and Send Request String based on given Marker
    request_string += str(street).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
    request_string += str(housenumber).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
    request_string += str(asset['city']).replace(" ", "%20").replace("ß", "%C3%9F").replace("/", "-").replace("nan", "").replace('ä', '%C3%A4').replace('ö', '%C3%B6').replace('ü', '%C3%BC').replace('Ä', '%C3%A4').replace('Ö', '%C3%B6').replace('Ü', '%C3%BC') + "%20"
    request_string += str(asset['zip'])
    
    return (request_string)
  
  #Organize Data for Compettior Analysis
  def organize_ca_data(self, entries, topic, marker_coords):
    
    # Create Variables
    counter = 0
    data_comp_analysis = []
    coords = []

    if topic == 'nursing_homes':
      Variables.home_address_nh = []
    else:
      Variables.home_address_al = []
    
    for entry in entries:
      print(entry)
      if topic == "nursing_homes":
        lat_entry = "%.6f" % float(entry['coord_lat'])
        lng_entry = "%.6f" % float(entry['coord_lon'])
      else:
        lat_entry = "%.6f" % float(entry['coord_lat'])
        lng_entry = "%.6f" % float(entry['coord_lon'])
      for icon in Variables.activeIcons[topic]:
          lng_icon = "%.6f" % icon['_lngLat']['lng']
          lat_icon = "%.6f" % icon['_lngLat']['lat']
          if lng_entry == lng_icon and lat_entry == lat_icon:
            coords.append([lng_icon, lat_icon])
            counter += 1
            if topic == "nursing_homes":
              if entry['anz_vers_pat'] == "-":
                anz_vers_pat = "N/A"
              else:
                anz_vers_pat = int(entry['anz_vers_pat'])
              if entry['platz_voll_pfl'] == "-":
                platz_voll_pfl = "N/A"
              else:
                platz_voll_pfl = int(entry['platz_voll_pfl'])
              if not anz_vers_pat == "N/A" and not platz_voll_pfl == "N/A":
                occupancy_raw = round((anz_vers_pat * 100) / platz_voll_pfl)
                if occupancy_raw > 100:
                  occupancy_raw = 100
                occupancy = f"{occupancy_raw} %"
              else:
                occupancy = "N/A"
              if not entry['invest'] == "-":
                if len(entry['invest']) == 4:
                  if entry['invest'].index(".") == 2:
                    invest = entry['invest'] + "0"
                  else:
                    invest = entry['invest']
                else:
                  invest = entry['invest']
              else:
                invest = "N/A"
              if entry['ez'] == "-":
                ez = "N/A"
              else:
                ez = int(entry['ez'])
              if entry['dz'] == "-":
                dz = "N/A"
              else:
                dz = int(entry['dz'])
              if entry['baujahr'] == "-":
                year = "N/A"
              else:
                year = int(entry['baujahr'])
              if entry['betreiber'] == "-":
                operator = "N/A"
              else:
                operator = entry['betreiber']
              if entry['mdk_note'] == "-":
                mdk = "N/A"
              else:
                mdk = entry['mdk_note']
              data = {
                "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "platz_voll_pfl": platz_voll_pfl,
                "ez": ez,
                "dz": dz,
                "anz_vers_pat": anz_vers_pat,
                "occupancy": occupancy,
                "baujahr": year,
                "status": entry['status'],
                "betreiber": operator.replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "invest": invest,
                "mdk_note": mdk,
                "coords": [lng_icon, lat_icon]
              }
              data_comp_analysis.append(data)
              break
            elif topic == "assisted_living":
              if entry['anz_wohnungen'] == '-':
                number_apts = 'N/A'
              else:
                number_apts = int(float(entry['anz_wohnungen']))
              if entry['betreiber'] == '-':
                operator = 'N/A'
              else:
                operator = entry['betreiber']
              data = {
                "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "operator": operator.replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "type": entry['art'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "city": entry['ort'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "status": entry['status'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                "number_apts": number_apts,
                "coords": [lng_icon, lat_icon]
              }
              data_comp_analysis.append(data)
              break
              
    # Sort Coordinates by Distance
    sorted_coords = anvil.server.call("get_distance", marker_coords, data_comp_analysis)
    for entry in sorted_coords:
      if entry[1] <= 0.01:
        anvil.js.call('addHomeAddress', entry, topic)
        res = 'none'
        while res == 'none':
          res = anvil.js.call('getResponse')
          time.sleep(.5)
        if res == 'yes':
          if topic == 'nursing_homes':
            Variables.home_address_nh.append(entry)
          else:
            Variables.home_address_al.append(entry)
      anvil.js.call('resetResponse')
      
    if topic == 'nursing_homes':
      if Variables.home_address_nh == []:
        anvil.js.call('addData', 'nursing_homes', marker_coords)
    else:
      if Variables.home_address_al == []:
        anvil.js.call('addData', 'assisted_living', marker_coords)
    
    preventLoop = True
    if topic == 'nursing_homes':
      if not Variables.home_address_nh == []:
        home_address = Variables.home_address_nh
      else:
        preventLoop = False
    elif topic == 'assisted_living':
      if not Variables.home_address_al == []:
        home_address = Variables.home_address_al
      else:
        preventLoop = False
    
    if preventLoop == False:
      gres = 'none'
      while gres == 'none':
        res = anvil.js.call('getResponse')
        time.sleep(.5)
        if not res == 'none':
          gres = 'true'
      if not res == 'dismiss':
        home_address = res
      else:
        home_address = []
      anvil.js.call('resetResponse', topic)
      
      if not home_address == []:
        sorted_coords.insert(0, home_address)
    
    res_data = {'sorted_coords': sorted_coords, 'marker_coords': marker_coords}
    
    return res_data
    
  def build_req_string(self, res_data, topic):
    
    if topic == 'nursing_homes':
      home_address = Variables.home_address_nh
    else:
      home_address = Variables.home_address_al
      
    for entry in home_address:
      if entry in res_data['sorted_coords']:
        ha_index = res_data['sorted_coords'].index(entry)
        res_data['sorted_coords'][ha_index].append('home')
    
    #Build Request-String for Mapbox Static-Map-API
    counter = 0
    request = []
    request_static_map_raw = f"%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B"
    request_static_map = request_static_map_raw
    
    index_coords = len(res_data['sorted_coords'])
    for entry in res_data['sorted_coords']:
      if 'home' in entry:
        index_coords -= 1
    last_coords = []
    complete_counter = 0

    test_counter = 0
    last_coord_dist = 0 
    for coordinate in res_data['sorted_coords']:
      if not last_coord_dist == coordinate[1]:
        if not 'home' in coordinate:
          for second_coordinate in res_data['sorted_coords']:
            if not coordinate == second_coordinate and coordinate[1] == second_coordinate[1]:
              test_counter += 1
      last_coord_dist = coordinate[1]
    index_coords -= test_counter

    last_coord_dist = 0
    
    for coordinate in reversed(res_data['sorted_coords']):
      if not last_coord_dist == coordinate[1]:
        counter += 1
        if complete_counter == len(res_data['sorted_coords']) - 1:
          if not coordinate[0]['coords'] == last_coords and not 'home' in coordinate:
            if not counter == 1:
              request_static_map += f"%2C"
            request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23000000%22%2C%22marker-size%22%3A%22medium%22%2C%22marker-symbol%22%3A%22{index_coords}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D"
          counter = 0
          if not request_static_map == request_static_map_raw:
            request_static_map += f"%2C"
          request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23FBA237%22%2C%22marker-size%22%3A%22medium%22%2C%22marker-symbol%22%3A%22s%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
          request.append(request_static_map)
          request_static_map = request_static_map_raw
          index_coords -= 1
        elif counter == 10:
          if not 'home' in coordinate:
            if not coordinate[0]['coords'] == last_coords:
              request_static_map += f"%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23000000%22%2C%22marker-size%22%3A%22medium%22%2C%22marker-symbol%22%3A%22{index_coords}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D%5D%7D"
              counter = 0
              request.append(request_static_map)
              request_static_map = request_static_map_raw
            else:
              dupe_coord = True
          index_coords -= 1
        elif not 'home' in coordinate:
          if not coordinate[0]['coords'] == last_coords:
            if not counter == 1:
              request_static_map += f"%2C"
            request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23000000%22%2C%22marker-size%22%3A%22medium%22%2C%22marker-symbol%22%3A%22{index_coords}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D"
          else:
            dupe_coord = True
          index_coords -= 1
        else:
          request_static_map += f"%5D%7D"
          counter = 0
          request.append(request_static_map)
          request_static_map = request_static_map_raw
          break
      last_coord_dist = coordinate[1]
        
      complete_counter += 1
      last_coords = coordinate[0]['coords']
    
    if request == []:
      request_static_map = request_static_map_raw + f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker-color%22%3A%22%23FBA237%22%2C%22marker-size%22%3A%22medium%22%2C%22marker-symbol%22%3A%22s%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
      request.append(request_static_map)
      request_static_map = request_static_map_raw
    
    return({"data": res_data['sorted_coords'], "request": request, "request2": Variables.activeIso})

  
  def change_icons(self, checkbox):
    
    if checkbox == "veterinary" and self.check_box_vet.checked == True:
      Variables.last_bbox_vet = self.create_icons(False, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
      Variables.last_bbox_vet = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
    elif checkbox == "social facility" and self.check_box_soc.checked == True:
      Variables.last_bbox_soc = self.create_icons(False, Variables.last_bbox_soc, "social_facility", Variables.icon_social)  
      Variables.last_bbox_soc = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
    elif checkbox == "pharmacy" and self.check_box_pha.checked == True:
      Variables.last_bbox_pha = self.create_icons(False, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
      Variables.last_bbox_pha = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
    elif checkbox == "nursing-home" and self.check_box_nur.checked == True:
      Variables.last_bbox_nur = self.create_icons(False, Variables.last_bbox_nur, "nursing_home", Variables.icon_nursing)
      Variables.last_bbox_nur = self.create_icons(self.check_box_nur.checked, Variables.last_bbox_nur, "nursing_home", Variables.icon_nursing)
    elif checkbox == "hospital" and self.check_box_hos.checked == True:
      Variables.last_bbox_hos = self.create_icons(False, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
      Variables.last_bbox_hos = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
    elif checkbox == "clinic" and self.check_box_cli.checked == True:
      Variables.last_bbox_cli = self.create_icons(False, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
      Variables.last_bbox_cli = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
    elif checkbox == "dentist" and self.check_box_den.checked == True:
      Variables.last_bbox_den = self.create_icons(False, Variables.last_bbox_den, "dentist", Variables.icon_dentist) 
      Variables.last_bbox_den = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
    elif checkbox == "doctors" and self.check_box_doc.checked == True:
      Variables.last_bbox_doc = self.create_icons(False, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)
      Variables.last_bbox_doc = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)
    elif checkbox == "nursing-schools" and self.check_box_nsc.checked == True:
      Variables.last_bbox_nsc = self.create_icons(False, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools)
      Variables.last_bbox_nsc = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools)    
    elif checkbox == "supermarket" and self.check_box_sma.checked == True:
      Variables.last_bbox_sma = self.create_icons(False, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
      Variables.last_bbox_sma = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
    elif checkbox == "restaurant" and self.check_box_res.checked == True:
      Variables.last_bbox_res = self.create_icons(False, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant) 
      Variables.last_bbox_res = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
    elif checkbox == "cafe" and self.check_box_cafe.checked == True:
      Variables.last_bbox_caf = self.create_icons(False, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
      Variables.last_bbox_caf = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
    elif checkbox == "university" and self.check_box_uni.checked == True:
      Variables.last_bbox_uni = self.create_icons(False, Variables.last_bbox_uni, "university", Variables.icon_university) 
      Variables.last_bbox_uni = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
    elif checkbox == "bus stop" and self.check_box_bus.checked == True:
      Variables.last_bbox_bus = self.create_icons(False, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)
      Variables.last_bbox_bus = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
    elif checkbox == "tram stop" and self.check_box_tra.checked == True:
      Variables.last_bbox_tra = self.create_icons(False, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
      Variables.last_bbox_tra = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
    elif checkbox == "Nursing Homes DB" and self.pdb_data_cb.checked == True:
      Variables.last_bbox_nh = self.create_icons(False, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
      Variables.last_bbox_nh = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
    elif checkbox == "Assisted Living DB" and self.pdb_data_al.checked == True:
      Variables.last_bbox_al = self.create_icons(False, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
      Variables.last_bbox_al = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)

  def select_all_change(self, **event_args):
    if event_args['sender'].tag.categorie == 'Healthcare':
        self.check_box_vet.checked = event_args['sender'].checked
        self.check_box_soc.checked = event_args['sender'].checked
        self.check_box_pha.checked = event_args['sender'].checked
        self.check_box_hos.checked = event_args['sender'].checked
        self.check_box_cli.checked = event_args['sender'].checked
        self.check_box_den.checked = event_args['sender'].checked
        self.check_box_doc.checked = event_args['sender'].checked
        self.check_box_nsc.checked = event_args['sender'].checked
        self.check_box_pdt.checked = event_args['sender'].checked
        self.check_box_hd.checked = event_args['sender'].checked
        self.check_box_vet.raise_event('change')
        self.check_box_soc.raise_event('change')
        self.check_box_pha.raise_event('change')
        self.check_box_hos.raise_event('change')
        self.check_box_cli.raise_event('change')
        self.check_box_den.raise_event('change')
        self.check_box_doc.raise_event('change')
        self.check_box_nsc.raise_event('change')
        self.check_box_pdt.raise_event('change')
        self.check_box_hd.raise_event('change')
    elif event_args['sender'].tag.categorie == 'Miscelaneous':
      self.check_box_sma.checked = event_args['sender'].checked
      self.check_box_res.checked = event_args['sender'].checked
      self.check_box_cafe.checked = event_args['sender'].checked
      self.check_box_uni.checked = event_args['sender'].checked
      self.check_box_sma.raise_event('change')
      self.check_box_res.raise_event('change')
      self.check_box_cafe.raise_event('change')
      self.check_box_uni.raise_event('change')
    elif event_args['sender'].tag.categorie == 'ÖPNV':
      self.check_box_bus.checked = event_args['sender'].checked
      self.check_box_tra.checked = event_args['sender'].checked
      self.check_box_bus.raise_event('change')
      self.check_box_tra.raise_event('change')
    pass

  def iso_layer_active_change(self, **event_args):
    if event_args['sender'].checked:
      self.mapbox.setLayoutProperty('isoLayer', 'visibility', 'visible')
    else:
      self.mapbox.setLayoutProperty('isoLayer', 'visibility', 'none')
    pass

  def hide_ms_marker_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    if event_args['sender'].checked:
      self.marker.remove()
    else:
      self.marker.addTo(self.mapbox)
    pass

  def change_cluster_color_click(self, **event_args):
    """This method is called when the button is clicked"""
    from .Change_Cluster_Color import Change_Cluster_Color
    response = alert(content=Change_Cluster_Color(components=self.icon_grid.get_components()), dismissible=False, large=True, buttons=[], role='custom_alert')
    for key in Variables.marker:
      Variables.marker[key]['color'] = response[key]
      for marker in Variables.marker[key]['marker']:
        anvil.js.call('changeBackground', marker['_element'], Variables.marker[key]["color"][2])
    for component in self.icon_grid.get_components():
      if type(component) == CheckBox:
        key = component.text
      elif type(component) == Label:
        component.foreground = Variables.marker[key]["color"][1]
    pass

  
  def create_cluster_marker(self, cluster_data):
    print(cluster_data)

    ##### UMSCHREIBEN #####
    
    #Initialise Variables
    excel_markers = {}
    added_clusters = []
    colors = ['blue', 'green', 'grey', 'lightblue', 'orange', 'pink', 'red', 'white', 'yellow', 'gold']

    #Create Settings
    self.icon_grid.row_spacing = 0
    
    for asset in cluster_data['data']:

      # Create HTML Element for Icon
      el = document.createElement('div')
      el.className = f'{asset["address"]}'
      el.style.width = '40px'
      el.style.height = '40px'
      el.style.backgroundSize = '100%'
      el.style.backgroundrepeat = 'no-repeat'
      el.style.zIndex = '9001'

      cluster_name = asset['cluster']

      color = cluster_data['settings'][cluster_name]['color']
      if not cluster_name in added_clusters:
        checkbox = CheckBox(checked=True, text=cluster_name, spacing_above='none', spacing_below='none')
        checkbox.add_event_handler('change', self.check_box_marker_icons_change)
        icon = Label(icon='fa:circle', foreground=color[1], spacing_above='none', spacing_below='none')
        self.icon_grid.add_component(checkbox, row=cluster_name, col_xs=0, width_xs=8)
        self.icon_grid.add_component(icon, row=cluster_name, col_xs=8, width_xs=1)
        added_clusters.append(cluster_name)

      # #Get Coordinates of provided Adress for Marker
      req_str = self.build_request_string(asset)
      req_str += f'.json?access_token={self.token}'
      coords = anvil.http.request(req_str,json=True)
      coordinates = coords['features'][0]['geometry']['coordinates']

      cluster_data['settings'][cluster_name]['marker'] = []
      el.style.backgroundImage = f'url({color[2]})'
      new_list = self.set_excel_markers(cluster_data['settings'][cluster_name]['static'], coordinates, cluster_data['settings'][cluster_name]['marker'], el)
      cluster_data['settings'][cluster_name]['marker'] = new_list
      
      # Create Popup for Marker and add it to the Map
      # popup = mapboxgl.Popup({'closeOnClick': False, 'offset': 25})
      # popup.setHTML(data[0][markercount]['Informationen'])
      # popup_static = mapboxgl.Popup({'closeOnClick': False, 'offset': 5, 'className': 'static-popup', 'closeButton': False, 'anchor': 'top'}).setText(data[0][markercount]['Informationen']).setLngLat(coords['features'][0]['geometry']['coordinates'])
      # popup_static.addTo(self.mapbox)
      
      #Increase Markercount
      # markercount += 1
      
    # Add Marker-Arrays to global Variable Marker
    Variables.marker.update(cluster_data['settings'])

    self.hide_marker.enabled = True
    self.change_cluster_color.enabled = True