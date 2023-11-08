# Import of different Modules
from ._anvil_designer import Map2_0Template
from anvil import *
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
from anvil.tables import app_tables
from anvil.js.window import mapboxgl, MapboxGeocoder, document
from .. import Variables, Layer, Images, ExcelFrames
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
import anvil.js
import anvil.http
import json
import anvil.media
import math
import datetime
import time
import copy
import Functions
import functools
import Market_Study_Functions

global Variables, Layer, Images, ExcelFrames

class Map2_0(Map2_0Template):
  # Definition of every base function inside Map2_0

  def __init__(self, **properties):
    with anvil.server.no_loading_indicator:
      maintenance = False
      try:
        self.token = anvil.server.call_s('get_token')
      except:
        maintenance = True
      
      # Set Form properties and Data Bindings
      if maintenance:
        from .Maintenance import Maintenance
        alert(content=Maintenance(), dismissible=False, buttons=[], large=True)
      else:
        self.role = properties['role']
        self.init_components(**properties)
        self.dom = anvil.js.get_dom_node(self.spacer_1)
        self.time_dropdown.items = [("5 minutes", "5"), ("10 minutes", "10"), ("15 minutes", "15"), ("20 minutes", "20"), ("30 minutes", "30"), ("60 minutes", "60"), ("5 minutes layers", "-1")]
        self.app_url = anvil.server.call_s('get_app_url')
        self.last_menu_height = '30%'
        self.cluster_data = {}
        self.competitors = []
        self.custom_marker = []
        self.comp_marker = []
        self.last_popup = None
        self.last_target = None
        self.active_container = None
        self.prev_called = None
        html = document.getElementsByClassName('anvil-root-container')[0]
        html.style.cursor = 'default'
  
  def form_show(self, **event_args):

    with anvil.server.no_loading_indicator:
      screen = anvil.js.call('get_screen_width')
      width = screen[0]
      height = screen[1]
      
      if self.role == 'admin' or self.role == 'user':
        self.dist_layer.visible = True
        self.poi_categories.visible = True
        self.button_overlay.visible = True
        self.hide_ms_marker.visible = True
        self.competitor_btn.visible = True
        self.file_loader_upload.visible = True
        self.share.visible = True
        self.button_icons.visible = True
        draggable = True

      if self.role == 'admin':
        self.admin_button.visible = 'visible'
        self.db_upload.visible = 'visible'

      if self.role == 'guest':
        draggable = False
      #   self.button_icons.text = 'Cluster & Investment'

      if width <= 998:
        self.mobile = True
        self.mobile_btn_grid.visible = True
        self.mobile_menu_open = False
      else:
        self.mobile = False
        if self.role == 'guest':
          container = document.getElementById('appGoesHere')
          logo = document.createElement('img')
          logo.src = f'{self.app_url}/_/theme/Logo.png'
          logo.style.position = 'absolute'
          logo.style.pointerEvents = 'none'
          logo.style.bottom = '30px'
          logo.style.right = '20px'
          logo.style.width = '15%'
          container.appendChild(logo)
      
      # Initiate Map and set Listener on Page Load
      self.select_all_hc.tag.categorie = 'Healthcare'
      self.select_all_opnv.tag.categorie = 'ÖPNV'
      self.select_all_edu.tag.categorie = 'Student Living'
      self.select_all_food.tag.categorie = 'Food & Drinks'
      
      mapboxgl.accessToken = self.token
      self.mapbox = mapboxgl.Map({'container': self.dom,
                                  'style': "mapbox://styles/shinykampfkeule/cldkfk8qu000001thivb3l1jn",
                                  'center': [13.4092, 52.5167],
                                  'zoom': 8})
      # Create HTML Element for Icon
      el = document.createElement('div')
      el.className = 'marker'
      el.style.width = '50px'
      el.style.height = '50px'
      el.style.backgroundSize = '100%'
      el.style.backgroundrepeat = 'no-repeat'
      el.style.zIndex = '299'
      el.style.backgroundImage = f'url({self.app_url}/_/theme/Pins/CB_MapPin_Location.png)'
      
      self.marker = mapboxgl.Marker({'draggable': draggable, 'element': el, 'anchor': 'bottom'})
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
      self.mapbox.on("style.load", self.handle_style_change)
      self.mapbox.on("load", self.loadHash)
      self.mapbox.on("contextmenu", self.map_right_click)
      self.mapbox.on("click", self.map_right_click)

      document.addEventListener('click', functools.partial(self.remove_details, None))

  def loadHash(self, event):
    with anvil.server.no_loading_indicator:
      hash = get_url_hash()
      if not len(hash) == 0:
        data = anvil.server.call('get_map_settings', hash['name'])
        Variables.removed_markers = data['removed_markers']
        for component in self.style_grid.get_components():
          if component.text == data['map_style']:
            component.checked = True
            component.raise_event('change')
            break
        self.map_styles.raise_event('click')
        time.sleep(.5)
        if data['study_pin']:
          self.marker.setLngLat([data['marker_lng'], data['marker_lat']])
          self.mapbox.flyTo({"center": [data['marker_lng'], data['marker_lat']], "zoom": data['zoom']})
        else:
          self.mapbox.flyTo({"center": [data['center']['lng'], data['center']['lat']], "zoom": data['zoom']})
          self.marker.remove()
        if data['iso_layer']:
          self.time_dropdown.selected_value = data['distance_time']
          self.profile_dropdown.selected_value = data['distance_movement']
          self.profile_dropdown.raise_event('change')
          self.dist_layer.visible = True
          self.dist_layer.icon = 'fa:angle-down'
          self.dist_layer.raise_event('click')
          self.time_dropdown.enabled = False
          self.profile_dropdown.enabled = False
          self.checkbox_poi_x_hfcig.checked = data['iso_layer']
          self.iso_layer_active.visible = False
          self.checkbox_poi_x_hfcig.visible = False
        healthcare_components = self.poi_categories_healthcare_container.get_components()
        if data['poi_healthcare'][0] == '1':
          healthcare_components[0].checked = True
          healthcare_components[0].raise_event('change')
        else:
          for index, state in enumerate(data['poi_healthcare']):
            if index > 0 and state == '1':
              healthcare_components[index].checked = True
              healthcare_components[index].raise_event('change')
        education_components = self.education_grid.get_components()
        if data['poi_education'][0] == '1':
          education_components[0].checked = True
          education_components[0].raise_event('change')
        else:
          for index, state in enumerate(data['poi_education']):
            if index > 0 and state == '1':
              education_components[index].checked = True
              education_components[index].raise_event('change')
        food_drinks_components = self.food_drinks_grid.get_components()
        if data['poi_food_drinks'][0] == '1':
          food_drinks_components[0].checked = True
          food_drinks_components[0].raise_event('change')
        else:
          for index, state in enumerate(data['poi_food_drinks']):
            if index > 0 and state == '1':
              food_drinks_components[index].checked = True
              food_drinks_components[index].raise_event('change')
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
        if not len(data['cluster']['data']) == 0:
          self.create_cluster_marker(data['cluster'])
          self.change_cluster_color.visible = False
        if not len(data['competitors']['competitors']) == 0:
          self.create_comp_marker(data['competitors']['competitors'])
        for marker in data['custom_marker']:
          self.create_custom_marker(marker)
            
  def check_box_marker_icons_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      # Show or Hide Marker-Icon-Types
      Functions.show_hide_marker(self, event_args['sender'].checked, event_args['sender'].tooltip)

  def button_marker_icons_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      # Show or Hide all Marker Icons
  
      if event_args['sender'] == self.cluster_all:
        all_marker = self.icon_grid.get_components()
      else:
        all_marker = self.invest_grid.get_components()
      
      if event_args['sender'].checked == True:
        marker_state = True
      else:
        marker_state = False
        
      for marker in all_marker:
        if not type(marker) is Label:
          if not marker.checked == marker_state:
            Functions.show_hide_marker(self, marker_state, marker.tooltip)
            marker.checked = marker_state
     
  def check_box_overlays_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      #Change Overlays based on checked Checkbox
      
      layer_name = dict(event_args)['sender'].text.replace(" ", "_").lower()
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
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(self, True)
      # Check or uncheck various Check Boxes for different POI Categories
      if dict(event_args)['sender'].text == "Veterinary":
        Variables.last_bbox_vet = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
      elif dict(event_args)['sender'].text == "Social Facility":
        Variables.last_bbox_soc = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
      elif dict(event_args)['sender'].text == "Pharmacy":
        Variables.last_bbox_pha = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
      elif dict(event_args)['sender'].text == "Hospital":
        Variables.last_bbox_hos = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
      elif dict(event_args)['sender'].text == "Clinic":
        Variables.last_bbox_cli = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
      elif dict(event_args)['sender'].text == "Dentist":
        Variables.last_bbox_den = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
      elif dict(event_args)['sender'].text == "Doctor":
        Variables.last_bbox_doc = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)      
      elif dict(event_args)['sender'].text == "Nursing School":
        Variables.last_bbox_nsc = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools) 
      elif dict(event_args)['sender'].text == "Supermarket":
        Variables.last_bbox_sma = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
      elif dict(event_args)['sender'].text == "Restaurant":
        Variables.last_bbox_res = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
      elif dict(event_args)['sender'].text == "Cafe":
        Variables.last_bbox_caf = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
      elif dict(event_args)['sender'].text == "University":
        Variables.last_bbox_uni = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
      elif dict(event_args)['sender'].text == "Bus Stop":
        Variables.last_bbox_bus = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
      elif dict(event_args)['sender'].text == "Tram Stop":
        Variables.last_bbox_tra = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
      elif dict(event_args)['sender'].text == "Nursing Home":
        Variables.last_bbox_nh = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
      elif dict(event_args)['sender'].text == "Assisted Living":
        Variables.last_bbox_al = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
      elif dict(event_args)['sender'].text == "Podiatrist":
        Variables.last_bbox_pdt = self.create_icons(self.check_box_pdt.checked, Variables.last_bbox_pdt, "podiatrist", Variables.icon_podiatrist)
      elif dict(event_args)['sender'].text == "Hairdresser":
        Variables.last_bbox_hd = self.create_icons(self.check_box_hd.checked, Variables.last_bbox_hd, "hairdresser", Variables.icon_hairdresser)
      elif event_args['sender'].text == "S-Bahn/U-Bahn":
        Variables.last_bbox_al = self.create_icons(self.check_box_su.checked, Variables.last_bbox_su, "subway", f'{self.app_url}/_/theme/Pins/U_Bahn_Pin.png')
      elif event_args['sender'].text == "Airport":
        Variables.last_bbox_ap = self.create_icons(self.check_box_ap.checked, Variables.last_bbox_ap, "aerodrome", f'{self.app_url}/_/theme/Pins/Flughafen_Pin.png')
      Functions.manipulate_loading_overlay(self, False)

  def checkbox_poi_x_hfcig_change(self, **event_args):
    #This method is called when the Check Box for POI based on HFCIG is checked or unchecked
    with anvil.server.no_loading_indicator:
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
    with anvil.server.no_loading_indicator:
      anvil.js.call('hide_show_Popup')   
   
  def map_style_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      #This method is called when one of the Buttons for changing the Map-Style got clicked
      if dict(event_args)['sender'].text == "Satellite Map":
        self.check_street.checked = False
        self.check_soft.checked = False
        self.mapbox.setStyle('mapbox://styles/mapbox/satellite-streets-v11')
      elif dict(event_args)['sender'].text == "Street Map":
        self.check_satellite.checked = False
        self.check_soft.checked = False
        self.mapbox.setStyle('mapbox://styles/mapbox/outdoors-v11')
      elif dict(event_args)['sender'].text == "Soft Map":
        self.check_street.checked = False
        self.check_satellite.checked = False
        self.mapbox.setStyle('mapbox://styles/shinykampfkeule/cldkfk8qu000001thivb3l1jn')

  def button_toggle_menu_parts(self, **event_args):
    with anvil.server.no_loading_indicator:
      #This method is called when one of the Submenus should be opened or closed
      toggler = {
        'Distance Layer': {
          'container': self.dist_container,
          'icon_container': self.dist_layer
        },
        'Import & Cluster': {
          'container': self.icon_categories_all,
          'icon_container': self.button_icons
        },
        'Cluster & Investment': {
          'container': self.icon_categories_all,
          'icon_container': self.button_icons
        },
        'Overlays': {
          'container': self.layer_categories_card,
          'icon_container': self.button_overlay
        },
        'Map Styles': {
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
        'Student Living': {
          'container': self.education_grid,
          'icon_container': self.education_btn
        },
        'Food & Drinks': {
          'container': self.food_drinks_grid,
          'icon_container': self.food_drinks_btn
        },
        'Public Transport': {
          'container': self.opnv_container,
          'icon_container': self.opnv_button
        },
        'Cluster': {
          'container': self.cluster_panel,
          'icon_container': self.cluster_btn
        },
        'Investment Class': {
          'container': self.invest_panel,
          'icon_container': self.invest_class_btn
        },
        'Competitors': {
          'container': self.competitor_grid,
          'icon_container': self.competitor_btn
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
  def admin_button_click(self, **event_args): 
    with anvil.server.no_loading_indicator:
      #This method is called when the User used the Admin-Button (!!!Just for Admin!!!)  
      date = datetime.datetime.now()
      # anvil.server.call('micmaccircle')
      # anvil.server.call('manipulate')

      cool_dictionary = {
        'a': {
          'a': 1,
          'b': 2
        },
        'b': 3,
        'c': {
          'a': 1,
          'b': 2,
          'c': {
            'a': 1,
            'b': 2,
            'c': 3
          }
        }
      }

      anvil.server.call('test_function', cool_dictionary)
      
      # addresses = [
      #   "Im Lerchenfeld 3, 07743 Jena",
      #   "Brauereihof 19, 13585 Berlin",
      #   "Sächsische Str. 46, 10707 Berlin",
      #   "Belziger Str. 53 c, 10823 Berlin",
      #   "Bennigsenstr. 23/24, 12159 Berlin",
      #   "Britzer Damm 140, 12347 Berlin"
      # ]
      
      ''' Get Population of every Municipalitie inside Iso-Layer '''
      # sendData = anvil.server.call('separate_iso', Variables.activeIso)
      
      # lk_Array = []
      # value_Array = []
      
      # for key in sendData['data']:
        
      #   lk_Array.append(key)
        
      # counter = 2
      
      # while not counter == len(sendData['data'][key][1]):
        
      #   value = 0
        
      #   for lk in lk_Array:
          
      #     value += sendData['data'][lk][1][counter]
          
      #   value = (round(value / 2 * 100) / 100)
        
      #   value_Array.append(value)
        
      #   counter += 1
    
      # keyArray = ['Municipality']
      # areaArray = ['Area']
      # popArray = ['Population']
      # km2Array = ['Population per km2']
    
      # tableContentMun: str = f"""
      #     <tr>
      #       <th class='dataCell'>Municipality</th>
      #   """
    
      # for key in sendData['areas']:
        
      #   if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
        
      #     tableContentMun += f"""<th class='dataCell width450'>{key}</th>"""
      
      # tableContentMun += """<th></th><th></th><th></th><th class='dataCell'>Iso-Layer</th>"""
      
      # for key in sendData['areas']:
        
      #   if 'Iso' in key:
          
      #     tableContentMun += f"""<th class='dataCell'>{key}</th>"""
      
      # tableContentMun += """</tr><tr><td class='dataCell'>Area</td>"""
      
      # for key in sendData['areas']:
        
      #   if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
          
      #     tableContentMun += f"""<td class='dataCell'>{round(sendData['data'][key][0][9], 2)} km2</td>"""
      
      # tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Area</td>"""
      
      # for key in sendData['areas']:
        
      #   if 'Iso' in key:
          
      #     tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['area_complete'], 2)} km2</td>"""
      
      # tableContentMun += """</tr><tr><td class='dataCell'>Population</td>"""
      
      # for key in sendData['areas']:
        
      #   if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
          
      #     tableContentMun += f"""<td class='dataCell'>{sendData['data'][key][0][10]}</td>"""
      
      # tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Population</td>"""
      
      # for key in sendData['areas']:
        
      #   if 'Iso' in key:
          
      #     tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'])}</td>"""
        
      # tableContentMun += """</tr><tr><td class='dataCell'>Population per km2</td>"""
      
      # for key in sendData['areas']:
        
      #   if not key == 'Iso60' and not key == 'Iso30' and not key == 'Iso20' and not key == 'Iso15' and not key == 'Iso10' and not key == 'Iso5':
          
      #     tableContentMun += f"""<td class='dataCell'>{sendData['data'][key][0][13]}</td>"""
    
      # tableContentMun += """<td></td><td></td><td></td><td class='dataCell'>Population per km2</td>""" 
    
      # for key in sendData['areas']:
          
      #   if 'Iso' in key:
            
      #     tableContentMun += f"""<td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] / sendData['areas'][key]['area_complete'])}</td>"""
        
      # tableContentMun += """</tr><tr class='emptyRow'></tr>"""
      
      # for key in sendData['areas']:
        
      #   if 'Iso' in key:
      
      #     tableContentMun += f"""<tr>
      #                             <th class='dataCell'>{key}</th>
      #                           </tr>
      #                           <tr>
      #                             <th class='dataCell'>Gender</th>
      #                             <th class='dataCell'>Overall</th>
      #                             <th class='dataCell'>Under 3</th>
      #                             <th class='dataCell'>3 to Under 6</th>
      #                             <th class='dataCell'>6 to Under 10</th>
      #                             <th class='dataCell'>10 to Under 15</th>
      #                             <th class='dataCell'>15 to Under 18</th>
      #                             <th class='dataCell'>18 to Under 20</th>
      #                             <th class='dataCell'>20 to Under 25</th>
      #                             <th class='dataCell'>25 to Under 30</th>
      #                             <th class='dataCell'>30 to Under 35</th>
      #                             <th class='dataCell'>35 to Under 40</th>
      #                             <th class='dataCell'>40 to Under 45</th>
      #                             <th class='dataCell'>45 to Under 50</th>
      #                             <th class='dataCell'>50 to Under 55</th>
      #                             <th class='dataCell'>55 to Under 60</th>
      #                             <th class='dataCell'>60 to Under 65</th>
      #                             <th class='dataCell'>65 to Under 75</th>
      #                             <th class='dataCell'>75 and Older</th>
      #                           </tr>
      #                           <tr>
      #                             <td class='dataCell'>Overall</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[35] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[53] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[18] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[36] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[19] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[37] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[20] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[38] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[21] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[39] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[22] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[40] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[23] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[41] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[24] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[42] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[25] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[43] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[26] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[44] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[27] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[45] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[28] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[46] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[29] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[47] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[30] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[48] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[31] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[49] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[32] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[50] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[33] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[51] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[34] / 100)) + round(sendData['areas'][key]['pop_for_area'] * (value_Array[52] / 100))}</td>
      #                           </tr>
      #                           <tr>
      #                             <td class='dataCell'>Male</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[35] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[18] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[19] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[20] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[21] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[22] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[23] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[24] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[25] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[26] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[27] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[28] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[29] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[30] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[31] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[32] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[33] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[34] / 100))}</td>
      #                           </tr>
      #                           <tr>
      #                             <td class='dataCell'>Female</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[53] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[36] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[37] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[38] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[39] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[40] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[41] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[42] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[43] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[44] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[45] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[46] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[47] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[48] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[49] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[50] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[51] / 100))}</td>
      #                             <td class='dataCell'>{round(sendData['areas'][key]['pop_for_area'] * (value_Array[52] / 100))}</td>
      #                           </tr>
      #                           <tr class='emptyRow'></tr>
      #                         """
      # html: str = f"""
      #   <html>
      #     <head>
      #       <title>Iso-Layer People Data</title>
      #       <style>
      #         table {{border-collapse: collapse; text-align: center; width: 99vw}}
      #         .dataCell {{border: 1px solid black}}
      #         .emptyRow {{height: 2vh}}
      #       </style>
      #       <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1" />
      #     </head>
      #     <body>
      #       <table>
      #         {tableContentMun}
      #       </table>
      #     </body>
      #   </html>
      # """
    
      # anvil.js.call('open_tab', html)
      print('Ready')

  #######Noch bearbeiten#######[]

  def create_market_study(self, **event_args):
    with anvil.server.no_loading_indicator:
      if self.role == 'admin':
        print(datetime.datetime.now())

      Functions.manipulate_loading_overlay(self, True)
      anvil.js.call('update_loading_bar', 10, 'Generating basic Information')
      
      ''' Generate created Date of Market Study '''
      created_date = Functions.get_current_date_as_string()
    
      ''' Get unique Code to identify Files and Images with current MS-Creation '''
      Variables.unique_code = anvil.server.call("get_unique_code")

      anvil.js.call('update_loading_bar', 25, 'Getting map related information')
      
      ''' Get Map based Information '''
      street = anvil.js.call('getSearchedAddress').split(",")[0]
      marker_coords = {
          'lng': (dict(self.marker['_lngLat'])['lng']),
          'lat': (dict(self.marker['_lngLat'])['lat'])
      }
      purchase_power = anvil.server.call('get_purchasing_power', location={'lat': marker_coords['lat'], 'lng': marker_coords['lng']})
      iso = dict(self.mapbox.getSource('iso'))
      iso_time = self.time_dropdown.selected_value
      if iso_time == "-1":
          iso_time = "20"
      iso_movement = self.profile_dropdown.selected_value.lower()
      bounding_box = [0, 0, 0, 0]
      for point in iso['_data']['features'][0]['geometry']['coordinates'][0]:
          if point[0] < bounding_box[1] or bounding_box[1] == 0:
              bounding_box[1] = point[0]
          if point[0] > bounding_box[3] or bounding_box[3] == 0:
              bounding_box[3] = point[0]
          if point[1] < bounding_box[0] or bounding_box[0] == 0:
              bounding_box[0] = point[1]
          if point[1] > bounding_box[2] or bounding_box[2] == 0:
              bounding_box[2] = point[1]
    
      ''' Get Data for Nursing Homes and Assisted Living '''
      coords_nh = Market_Study_Functions.organize_ca_data(Variables.nursing_homes_entries, 'nursing_homes', marker_coords, self, Functions)
      coords_al = Market_Study_Functions.organize_ca_data(Variables.assisted_living_entries, 'assisted_living', marker_coords, self, Functions)
      data_comp_analysis_nh = Market_Study_Functions.build_req_string(coords_nh, 'nursing_homes')
      data_comp_analysis_al = Market_Study_Functions.build_req_string(coords_al, 'assisted_living')
    
      inpatients = 0
      beds_active = 0
      beds_planned = 0
      beds_construct = 0
      nursing_homes_active = 0
      nursing_homes_planned = 0
      nursing_homes_construct = 0
      invest_cost = []
      operator = []
      beds = []
      operator_public = []
      operator_nonProfit = []
      operator_private = []
      for care_entry in data_comp_analysis_nh['data']:
          beds_amount = 0
          if not care_entry[0]['anz_vers_pat'] == '-':
              inpatients += int(care_entry[0]['anz_vers_pat'])
          if care_entry[0]['status'] == "aktiv":
              nursing_homes_active += 1
              if not care_entry[0]['platz_voll_pfl'] == "-":
                  beds_active += int(care_entry[0]['platz_voll_pfl'])
                  beds_amount = int(care_entry[0]['platz_voll_pfl'])
              beds.append(beds_amount)
          elif care_entry[0]['status'] == "in Planung":
              nursing_homes_planned += 1
              if not care_entry[0]['platz_voll_pfl'] == "-":
                  beds_planned += int(care_entry[0]['platz_voll_pfl'])
          elif care_entry[0]['status'] == "im Bau":
              nursing_homes_construct += 1
              if not care_entry[0]['platz_voll_pfl'] == "-":
                  beds_construct += int(care_entry[0]['platz_voll_pfl'])
          if not care_entry[0]['invest'] == "-":
              invest_cost.append(float(care_entry[0]['invest']))
          if not care_entry[0]['betreiber'] == "-":
              if care_entry[0]['operator_type'] == "privat":
                  if not care_entry[0]['betreiber'] in operator_private:
                      operator_private.append(care_entry[0]['betreiber'])
              elif care_entry[0]['operator_type'] == "gemeinnützig":
                  if not care_entry[0]['betreiber'] in operator_nonProfit:
                      operator_nonProfit.append(care_entry[0]['betreiber'])
              elif care_entry[0]['operator_type'] == "kommunal":
                  if not care_entry[0]['betreiber'] in operator_public:
                      operator_public.append(care_entry[0]['betreiber'])
              if not care_entry[0]['betreiber'] in operator:
                  operator.append(care_entry[0]['betreiber'])
    
      ''' Get Place from Geocoder-API for Map-Marker and extract needed Information '''
      request = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{marker_coords['lng']},{marker_coords['lat']}.json?access_token={self.token}"
      response_data = anvil.http.request(request, json=True)
      marker_context = response_data['features'][0]['context']
      zipcode = "n.a."
      district = "n.a."
      city = "n.a."
      federal_state = "n.a."
      for info in marker_context:
          if "postcode" in info['id']:
              zipcode = info['text']
          elif "locality" in info['id']:
              district = info['text']
          elif "place" in info['id']:
              city = info['text']
          elif "region" in info['id']:
              federal_state = info['text']
      if federal_state == "n.a.":
          federal_state = city
      if district == "n.a.":
          district = city

      anvil.js.call('update_loading_bar', 45, 'Generating Location Analysis Text')
      
      ''' Get generated Analysis-Text for City '''
      from .ChatGPT import ChatGPT
      analysis_text = anvil.server.call('openai_test', city)
      Functions.manipulate_loading_overlay(self, False)
      analysis_text = alert(ChatGPT(generated_text=analysis_text), buttons=[], dismissible=False, large=True, role='custom_alert')
      Functions.manipulate_loading_overlay(self, True)
      
      anvil.js.call('update_loading_bar', 50, 'Calculating Data for Market Study')
    
      ''' Get Information from Database for County of Marker-Position and extract Data '''
      countie_data = anvil.server.call("get_demographic_district_data", marker_coords)
      countie = countie_data['ex_dem_lk']['name'].split(',')
      people_u80 = int(countie_data['dem_fc_lk']['g_65tou70_2020_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2020_abs'])
      people_o80 = int(countie_data['dem_fc_lk']['g_80plus_2020_abs'])
      people_u80_fc = int(countie_data['dem_fc_lk']['g_65tou70_2030_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2030_abs'])
      people_o80_fc = int(countie_data['dem_fc_lk']['g_80plus_2030_abs'])
      people_u80_fc_35 = int(countie_data['dem_fc_lk']['g_65tou70_2035_abs']) + int(countie_data['dem_fc_lk']['g_70tou80_2035_abs'])
      people_o80_fc_35 = int(countie_data['dem_fc_lk']['g_80plus_2035_abs'])
      change_u80 = float("{:.2f}".format(((people_u80_fc * 100) / people_u80) - 100))
      change_o80 = float("{:.2f}".format(((people_o80_fc * 100) / people_o80) - 100))
      population_trend = "{:.1f}".format((people_u80_fc_35 + people_o80_fc_35) * 100 / (people_u80 + people_o80) - 100)
      nursing_home_rate = round(float(countie_data['pfleg_stat_lk']['heimquote2019']) * 100, 1)
      keys = ['g_u6', 'g_6tou10', 'g_10tou16', 'g_16tou20', 'g_20tou30', 'g_30tou50', 'g_50tou65', 'g_65tou70', 'g_70tou80', 'g_80plus']
      population_fc_30 = 0
      population_fc_35 = 0
      for key in keys:
          population_fc_30 += int(countie_data['dem_fc_lk'][f'{key}_2030_abs'])
          population_fc_35 += int(countie_data['dem_fc_lk'][f'{key}_2035_abs'])
    
      ''' Get Entries from Care-Database based on District and extract Data '''
      care_data_district = anvil.server.call("get_care_district_data", countie_data['ex_dem_lk']['key'])
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
      occupancy_lk = round((inpatients_lk * 100) / beds_lk, 1)
      free_beds_lk = beds_lk - inpatients_lk
    
      ''' Calculate Data for Market Study '''
      new_r_care_rate_raw = float("{:.3f}".format(inpatients_lk / (people_u80 + people_o80)))
      new_care_rate_raw = round((inpatients_lk * 100 / round((nursing_home_rate * countie_data['ex_dem_lk']['all_compl']) + 1)) * 100, 1)
      pat_rec_full_care_fc_30_v1 = round(new_r_care_rate_raw * (people_u80_fc + people_o80_fc))
      care_rate_30_v1_raw = round((pat_rec_full_care_fc_30_v1 * 100 / (population_fc_30 * nursing_home_rate)) * 100, 1)
      pat_rec_full_care_fc_30_v2 = round((new_r_care_rate_raw + 0.003) * (people_u80_fc + people_o80_fc))
      care_rate_30_v2_raw = round((pat_rec_full_care_fc_30_v2 * 100 / (population_fc_30 * nursing_home_rate)) * 100, 1)
      pat_rec_full_care_fc_35_v1 = round(new_r_care_rate_raw * (people_u80_fc_35 + people_o80_fc_35))
      care_rate_35_v1_raw = round((pat_rec_full_care_fc_35_v1 * 100 / (population_fc_35 * nursing_home_rate)) * 100, 1)
      pat_rec_full_care_fc_35_v2 = round((new_r_care_rate_raw + 0.003) * (people_u80_fc_35 + people_o80_fc_35))
      care_rate_35_v2_raw = round((pat_rec_full_care_fc_35_v2 * 100 / (population_fc_35 * nursing_home_rate)) * 100, 1)
      inpatients_fc = round(pat_rec_full_care_fc_30_v1 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
      inpatients_fc_v2 = round(pat_rec_full_care_fc_30_v2 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
      inpatients_fc_35 = round(pat_rec_full_care_fc_35_v1 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
      inpatients_fc_35_v2 = round(pat_rec_full_care_fc_35_v2 * (round(((inpatients * 100) / inpatients_lk), 1) / 100))
      beds_30_v1 = round((pat_rec_full_care_fc_30_v1 / 0.95))
      beds_30_v2 = round((pat_rec_full_care_fc_30_v2 / 0.95))
      beds_35_v1 = round((pat_rec_full_care_fc_35_v1 / 0.95))
      beds_35_v2 = round((pat_rec_full_care_fc_35_v2 / 0.95))
      free_beds_30_v1 = beds_30_v1 - pat_rec_full_care_fc_30_v1
      free_beds_30_v2 = beds_30_v2 - pat_rec_full_care_fc_30_v2
      free_beds_35_v1 = beds_35_v1 - pat_rec_full_care_fc_35_v1
      free_beds_35_v2 = beds_35_v2 - pat_rec_full_care_fc_35_v2
    
      regulations = anvil.server.call('read_regulations', federal_state)
      facilities_bed_amount = 0
      facilities_bed_amount_future = 0
      for index, competitor in enumerate(data_comp_analysis_nh['data']):
          if not competitor[0]['ez'] == '-' or not competitor[0]['dz'] == '-':
              if not competitor[0]['ez'] == '-' and competitor[0]['ez'] is not None:
                  facility_single_rooms = int(competitor[0]['ez'])
              else:
                  facility_single_rooms = 0
              if not competitor[0]['dz'] == '-' and competitor[0]['dz'] is not None:
                  facility_double_rooms = int(competitor[0]['dz'])
              else:
                  facility_double_rooms = 0
              facility_rooms = facility_single_rooms + facility_double_rooms
              facility_single_room_quote = facility_single_rooms / facility_rooms
              facility_bed_amount = facility_single_rooms + facility_double_rooms * 2
              if not regulations['Existing']['sr_quote'] == '/':
                  facility_single_room_quote_future = float(regulations['Existing']['sr_quote'])
              else:
                  facility_single_room_quote_future = 0
              if not regulations['Existing']['max_beds'] == '/':
                  facility_max_beds_future = float(regulations['Existing']['max_beds'])
              else:
                  facility_max_beds_future = 999999
              if facility_single_room_quote < facility_single_room_quote_future or facility_bed_amount > facility_max_beds_future:
                  data_comp_analysis_nh['data'][index][0]['legal'] = "No"
              else:
                  data_comp_analysis_nh['data'][index][0]['legal'] = "Yes"
              if facility_single_room_quote < facility_single_room_quote_future:
                  facility_single_rooms_future = int(round(facility_rooms * facility_single_room_quote_future, 0))
                  facility_double_rooms_future = int(round(facility_rooms - facility_single_rooms_future, 0))
                  facility_bed_amount_future = int(
                      round(facility_single_rooms_future + facility_double_rooms_future * 2, 0))
              else:
                  facility_bed_amount_future = facility_bed_amount
              if facility_bed_amount_future > facility_max_beds_future:
                  facility_bed_amount_future = facility_max_beds_future
              facilities_bed_amount += facility_bed_amount
              facilities_bed_amount_future += facility_bed_amount_future
          else:
              data_comp_analysis_nh['data'][index][0]['legal'] = "-"
    
      loss_of_beds = facilities_bed_amount_future - facilities_bed_amount
      beds_adjusted_30_v1 = beds_active + beds_planned + beds_construct + loss_of_beds
      beds_adjusted_30_v2 = beds_active + beds_planned + beds_construct + loss_of_beds
      beds_adjusted_35_v1 = beds_active + beds_planned + beds_construct + loss_of_beds
      beds_adjusted_35_v2 = beds_active + beds_planned + beds_construct + loss_of_beds
      beds_surplus_35 = beds_adjusted_35_v1 - inpatients_fc_35
      beds_surplus_35_v2 = beds_adjusted_35_v2 - inpatients_fc_35_v2
      beds_surplus = beds_adjusted_30_v1 - inpatients_fc
      beds_surplus_v2 = beds_adjusted_30_v2 - inpatients_fc_v2
    
      share_url = self.create_share_map('market_study')

      anvil.js.call('update_loading_bar', 75, 'Generating Market Study')
      
      market_study_pages = ["cover", "summary", "location_analysis"]
      max_pages = 3
      summary_page = 2
      location_analysis_page = 3
      current_competitor_analysis_page = 4
    
      nursing_homes_amount = len(data_comp_analysis_nh['data'])
      assisted_living_amount = len(data_comp_analysis_al['data'])
      total_amount = nursing_homes_amount + assisted_living_amount
      list_beds = []
      list_years_of_construction_nh = []
      list_years_of_construction_al = []
      none_profit_operator_nh = 0
      none_profit_operator_al = 0
      public_operator_nh = 0
      public_operator_al = 0
      private_operator_nh = 0
      private_operator_al = 0
      home_invest = -1
      complied_regulations = 0
      uncomplied_regulations = 0
      invest_plot_data = []
      invest_costs_public = []
      invest_costs_non_profit = []
      invest_costs_private = []
      invest_costs_public_home = -1
      invest_costs_non_profit_home = -1
      invest_costs_private_home = -1
      competitor_pages = {}
      page = 1
    
      # Nursing Home Pages
      home_counter = 0
      total_beds = 0
      total_single_rooms = 0
      total_double_rooms = 0
      total_rooms = 0
      list_single_room_quota = []
      list_occupancy_rate = []
      list_invest_cost = []
      list_mdk_grade = []
      prev_competitor_distance = 0
      prev_competitor_index = 0
      current_page_height = 177

      for index, competitor in enumerate(data_comp_analysis_nh['data']):
          if index % 9 == 0:
              if index > 0:
                  competitor_pages[f'competitor_analysis_{page}'] = current_competitor_page
                  page += 1
                  current_competitor_analysis_page += 1
              from . import Nursing_Homes_Competitor_Skeleton
              current_competitor_page = copy.deepcopy(Nursing_Homes_Competitor_Skeleton.nursing_homes_competitor_skeleton)
              current_competitor_page['page_number'] = current_competitor_analysis_page
              current_competitor_page['text']['heading_city']['txt'] = city
              current_competitor_page['image']['location_map']['path'] = f"tmp/map_image_{Variables.unique_code}.png"
              current_page_height = 177
      
          if 'home' in competitor:
              home_counter += 1
              current_competitor_page['cell'][f'home_{home_counter}_icon'] = {
                  'color': [204, 182, 102],
                  'fill_color': [27, 41, 57],
                  'font': 'calibri',
                  'size': 14,
                  'x': 10,
                  'y': current_page_height,
                  'w': 6,
                  'h': 10,
                  'txt': '⌂',
                  'align': 'center',
                  'fill': True
              }
              current_competitor_page['cell'][f'home_{home_counter}_name'] = {
                  'color': [0, 176, 240] if not "keine " in competitor[0]['web'] else [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height,
                  'w': 50,
                  'h': 6,
                  'txt': competitor[0]['raw_name'] if len(competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
                  'align': 'left',
                  'fill': True,
                  'link': competitor[0]['web'] if not "keine " in competitor[0]['web'] else ""
              }
              current_competitor_page['cell'][f'home_{home_counter}_operator'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height + 4,
                  'w': 186,
                  'h': 6,
                  'txt': competitor[0]['raw_betreiber'] if len(competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
                  'align': 'left',
                  'fill': True
              }
              current_competitor_page['cell'][f'home_{home_counter}_top_30_operator'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 67,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_operator_type'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 77,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public",
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_status'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 89,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_year_of_construction'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 101,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': competitor[0]['baujahr'],
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_legal'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 111,
                  'y': current_page_height,
                  'w': 8,
                  'h': 6,
                  'txt': competitor[0]['legal'],
                  'align': 'center',
                  'fill': True,
              }
      
              if not competitor[0]['legal'] == '-':
                  if competitor[0]['legal'] == 'Yes':
                      complied_regulations += 1
                  else:
                      uncomplied_regulations += 1
              if competitor[0]['operator_type'] == 'privat':
                  private_operator_nh += 1
                  if not competitor[0]['invest'] == '-':
                      invest_costs_private.append(float(competitor[0]['invest']))
                      invest_costs_private_home = float(competitor[0]['invest'])
              elif competitor[0]['operator_type'] == 'kommunal':
                  public_operator_nh += 1
                  if not competitor[0]['invest'] == '-':
                      invest_costs_public.append(float(competitor[0]['invest']))
                      invest_costs_public_home = float(competitor[0]['invest'])
              elif competitor[0]['operator_type'] == 'gemeinnützig':
                  none_profit_operator_nh += 1
                  if not competitor[0]['invest'] == '-':
                      invest_costs_non_profit.append(float(competitor[0]['invest']))
                      invest_costs_non_profit_home = float(competitor[0]['invest'])
              if not competitor[0]['ez'] == '-':
                  single_rooms = int(competitor[0]['ez'])
              else:
                  single_rooms = '-'
              if not competitor[0]['dz'] == '-':
                  double_rooms = int(competitor[0]['dz'])
              else:
                  double_rooms = '-'
              if not competitor[0]['platz_voll_pfl'] == '-':
                  beds = competitor[0]['platz_voll_pfl']
              else:
                  beds = '-'
              if not single_rooms == '-':
                  if not double_rooms == '-':
                      rooms = single_rooms + double_rooms
                      single_room_quote = round(single_rooms / (single_rooms + double_rooms) * 100, 1)
                  else:
                      rooms = single_rooms
                      single_room_quote = 100.0
              else:
                  if not double_rooms == '-':
                      rooms = double_rooms
                      single_room_quote = 0.0
                  else:
                      rooms = '-'
                      single_room_quote = '-'
              if not beds == '-':
                  total_beds += beds
                  list_beds.append(beds)
              if not single_rooms == '-':
                  total_single_rooms += single_rooms
              if not double_rooms == '-':
                  total_double_rooms += double_rooms
              if not rooms == '-':
                  total_rooms += rooms
              if not single_room_quote == '-':
                  list_single_room_quota.append(single_room_quote)
              if not competitor[0]['occupancy'] == '-':
                  list_occupancy_rate.append(competitor[0]['occupancy'])
              if not competitor[0]['invest'] == '-':
                  list_invest_cost.append(float(competitor[0]['invest']))
                  home_invest = float(competitor[0]['invest'])
              if not competitor[0]['mdk_note'] == '-':
                  list_mdk_grade.append(float(competitor[0]['mdk_note']))
              if not competitor[0]['baujahr'] == '-':
                  list_years_of_construction_nh.append(int(competitor[0]['baujahr']))
              if not competitor[0]['invest'] == '-' and not competitor[0]['baujahr'] == '-':
                  invest_plot_data.append(['home', competitor[0]['invest'], competitor[0]['baujahr'], '⌂'])
      
              current_competitor_page['cell'][f'home_{home_counter}_beds'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 119,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}'.format(beds),
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_single_rooms'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 129,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': '{:,}'.format(single_rooms) if not single_rooms == '-' else single_rooms,
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_double_rooms'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 141,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': '{:,}'.format(double_rooms) if not single_rooms == '-' else single_rooms,
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_rooms'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 153,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}'.format(rooms) if not single_rooms == '-' else single_rooms,
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_single_room_quota'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 163,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}%'.format(single_room_quote) if not single_rooms == '-' else single_rooms,
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_occupancy'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 173,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}%'.format(round(competitor[0]['occupancy'] * 100), 1),
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_invest'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 183,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '-' if competitor[0]['invest'] == '-' else '{:,}€'.format(float(competitor[0]['invest'])),
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_quality'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 193,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '-' if competitor[0]['mdk_note'] == '-' else '{:,}'.format(float(competitor[0]['mdk_note'])),
                  'align': 'center',
                  'fill': True,
              }
      
          else:
              table_position = (index % 9) + 1
              if not prev_competitor_distance == competitor[1]:
                  prev_competitor_distance = competitor[1]
                  prev_competitor_index += 1
              current_competitor_page['cell'][f'competitor_{table_position}_icon'] = {
                  'color': [255, 255, 255],
                  'fill_color': [244, 81, 94],
                  'font': 'segoeui',
                  'size': 11,
                  'x': 10,
                  'y': current_page_height,
                  'w': 6,
                  'h': 10,
                  'txt': str(prev_competitor_index),
                  'align': 'center',
                  'fill': True
              }
              current_competitor_page['cell'][f'competitor_{table_position}_name'] = {
                  'color': [0, 176, 240] if not "keine " in competitor[0]['web'] else [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height,
                  'w': 50,
                  'h': 6,
                  'txt': competitor[0]['raw_name'] if len(competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
                  'align': 'left',
                  'link': competitor[0]['web'] if not "keine " in competitor[0]['web'] else ""
              }
              current_competitor_page['cell'][f'competitor_{table_position}_operator'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height + 4,
                  'w': 50,
                  'h': 6,
                  'txt': competitor[0]['raw_betreiber'] if len(competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
                  'align': 'left',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_top_30_operator'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 67,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_operator_type'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 77,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public",
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_status'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 89,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_year_of_construction'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 101,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': competitor[0]['baujahr'],
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_legal'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 111,
                  'y': current_page_height,
                  'w': 8,
                  'h': 6,
                  'txt': competitor[0]['legal'],
                  'align': 'center',
              }
      
              if not competitor[0]['legal'] == '-':
                  if competitor[0]['legal'] == 'Yes':
                      complied_regulations += 1
                  else:
                      uncomplied_regulations += 1
              if competitor[0]['operator_type'] == 'privat':
                  private_operator_nh += 1
                  if not competitor[0]['invest'] == '-':
                      invest_costs_private.append(float(competitor[0]['invest']))
              elif competitor[0]['operator_type'] == 'kommunal':
                  public_operator_nh += 1
                  if not competitor[0]['invest'] == '-':
                      invest_costs_public.append(float(competitor[0]['invest']))
              elif competitor[0]['operator_type'] == 'gemeinnützig':
                  none_profit_operator_nh += 1
                  if not competitor[0]['invest'] == '-':
                      invest_costs_non_profit.append(float(competitor[0]['invest']))
              if not competitor[0]['ez'] == '-':
                  single_rooms = int(competitor[0]['ez'])
              else:
                  single_rooms = '-'
              if not competitor[0]['dz'] == '-':
                  double_rooms = int(competitor[0]['dz'])
              else:
                  double_rooms = '-'
              if not competitor[0]['platz_voll_pfl'] == '-':
                  beds = competitor[0]['platz_voll_pfl']
              else:
                  beds = '-'
              if not single_rooms == '-':
                  if not double_rooms == '-':
                      rooms = single_rooms + double_rooms
                      single_room_quote = round(single_rooms / (single_rooms + double_rooms) * 100, 1)
                  else:
                      rooms = single_rooms
                      single_room_quote = 100.0
              else:
                  if not double_rooms == '-':
                      rooms = double_rooms
                      single_room_quote = 0.0
                  else:
                      rooms = '-'
                      single_room_quote = '-'
              if not beds == '-':
                  total_beds += beds
                  list_beds.append(beds)
              if not single_rooms == '-':
                  total_single_rooms += single_rooms
              if not double_rooms == '-':
                  total_double_rooms += double_rooms
              if not rooms == '-':
                  total_rooms += rooms
              if not single_room_quote == '-':
                  list_single_room_quota.append(single_room_quote)
              if not competitor[0]['occupancy'] == '-':
                  list_occupancy_rate.append(competitor[0]['occupancy'])
              if not competitor[0]['invest'] == '-':
                  list_invest_cost.append(float(competitor[0]['invest']))
              if not competitor[0]['mdk_note'] == '-':
                  list_mdk_grade.append(float(competitor[0]['mdk_note']))
              if not competitor[0]['baujahr'] == '-':
                  list_years_of_construction_nh.append(int(competitor[0]['baujahr']))
              if not competitor[0]['invest'] == '-' and not competitor[0]['baujahr'] == '-':
                  invest_plot_data.append(["private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public", competitor[0]['invest'], competitor[0]['baujahr'], prev_competitor_index])
  
              current_competitor_page['cell'][f'competitor_{table_position}_beds'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 119,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}'.format(beds),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_single_rooms'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 129,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': '{:,}'.format(single_rooms) if not single_rooms == '-' else single_rooms,
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_double_rooms'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 141,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': '{:,}'.format(double_rooms) if not double_rooms == '-' else double_rooms,
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_rooms'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 153,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}'.format(rooms) if not rooms == '-' else rooms,
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_single_room_quota'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 163,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}%'.format(single_room_quote) if not single_room_quote == '-' else single_room_quote,
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_occupancy'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 173,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}%'.format(round(competitor[0]['occupancy'] * 100), 1) if not competitor[0]['occupancy'] == '-' else competitor[0]['occupancy'],
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_invest'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 183,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '-' if competitor[0]['invest'] == '-' else '{:,}€'.format(float(competitor[0]['invest'])),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_quality'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 193,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': '-' if competitor[0]['mdk_note'] == '-' else '{:,}'.format(float(competitor[0]['mdk_note'])),
                  'align': 'center',
              }
      
          current_page_height += 12
  
          if index == len(data_comp_analysis_nh['data']) - 1:
              median_dictionary = anvil.server.call(
                  "get_multiple_median",
                  {
                      'single_room_quota': list_single_room_quota,
                      'occupancy_rate': list_occupancy_rate,
                      'invest_cost': list_invest_cost,
                      'mdk_grade': list_mdk_grade
                  }
              )
              if len(list_single_room_quota) > 0:
                  total_single_room_quota = median_dictionary['single_room_quota']
              else:
                  total_single_room_quota = 0
              if len(list_occupancy_rate) > 0:
                  total_occupancy_rate = median_dictionary['occupancy_rate']
              else:
                  total_occupancy_rate = 0
              if len(list_invest_cost) > 0:
                  minimum_invest_cost = min(list_invest_cost)
              else:
                  minimum_invest_cost = 0
              if len(list_invest_cost) > 0:
                  maximum_invest_cost = max(list_invest_cost)
              else:
                  maximum_invest_cost = 0
              if len(list_invest_cost) > 0:
                  total_invest_cost = median_dictionary['invest_cost']
              else:
                  total_invest_cost = 0
              if len(list_mdk_grade) > 0:
                  total_mdk_grade = median_dictionary['mdk_grade']
              else:
                  total_mdk_grade = 0
      
              current_competitor_page['cell'][f'competitor_sum_beds'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 119,
                  'y': 285,
                  'w': 10,
                  'h': 6,
                  'txt': 'Σ {:,}'.format(total_beds),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_sum_single_rooms'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 129,
                  'y': 285,
                  'w': 12,
                  'h': 6,
                  'txt': 'Σ {:,}'.format(total_single_rooms),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_sum_double_rooms'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 141,
                  'y': 285,
                  'w': 12,
                  'h': 6,
                  'txt': 'Σ {:,}'.format(total_double_rooms),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_sum_rooms'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 153,
                  'y': 285,
                  'w': 10,
                  'h': 6,
                  'txt': 'Σ {:,}'.format(total_rooms),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_median_single_room_quota'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 163,
                  'y': 285,
                  'w': 10,
                  'h': 6,
                  'txt': 'x̃ {:,}%'.format(round(total_single_room_quota, 1)),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_median_occupancy'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 173,
                  'y': 285,
                  'w': 10,
                  'h': 6,
                  'txt': 'x̃ {:,}%'.format(round(total_occupancy_rate * 100, 1)),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_median_invest'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 183,
                  'y': 285,
                  'w': 10,
                  'h': 6,
                  'txt': 'x̃ {:,}'.format(round(total_invest_cost, 2)),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_median_quality'] = {
                  'color': [0, 0, 0],
                  'font': 'seguisb',
                  'size': 8,
                  'x': 193,
                  'y': 285,
                  'w': 10,
                  'h': 6,
                  'txt': '{:,}'.format(total_mdk_grade),
                  'align': 'center',
              }
            
              competitor_pages[f'competitor_analysis_{page}'] = current_competitor_page
    
      # Assisted Living Pages
      home_counter = 0
      prev_competitor_distance = 0
      prev_competitor_index = 0
      current_page_height = 177
      
      for index, competitor in enumerate(data_comp_analysis_al['data']):
          if index % 9 == 0:
              competitor_pages[f'competitor_analysis_{page}'] = current_competitor_page
              page += 1
              current_competitor_analysis_page += 1
              from . import Assisted_Living_Competitor_Skeleton
              current_competitor_page = copy.deepcopy(Assisted_Living_Competitor_Skeleton.assisted_living_competitor_skeleton)
              current_competitor_page['page_number'] = current_competitor_analysis_page
              current_competitor_page['text']['heading_city']['txt'] = city
              current_competitor_page['image']['location_map']['path'] = f"tmp/map_image_{Variables.unique_code}.png"
              current_page_height = 177
      
          if 'home' in competitor:
              home_counter += 1
              current_competitor_page['cell'][f'home_{home_counter}_icon'] = {
                  'color': [204, 182, 102],
                  'fill_color': [27, 41, 57],
                  'font': 'calibri',
                  'size': 14,
                  'x': 10,
                  'y': current_page_height,
                  'w': 6,
                  'h': 10,
                  'txt': '⌂',
                  'align': 'center',
                  'fill': True
              }
              current_competitor_page['cell'][f'home_{home_counter}_name'] = {
                  'color': [0, 176, 240] if not "keine " in competitor[0]['web'] else [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height,
                  'w': 50,
                  'h': 6,
                  'txt': competitor[0]['raw_name'] if len(competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
                  'align': 'left',
                  'fill': True,
                  'link': competitor[0]['web'] if not "keine " in competitor[0]['web'] else ""
              }
              current_competitor_page['cell'][f'home_{home_counter}_operator'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height + 4,
                  'w': 186,
                  'h': 6,
                  'txt': competitor[0]['raw_betreiber'] if len(competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
                  'align': 'left',
                  'fill': True
              }
              current_competitor_page['cell'][f'home_{home_counter}_top_30_operator'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 67,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_operator_type'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 77,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public",
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_status'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 89,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_year_of_construction'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 101,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': competitor[0]['year_of_construction'],
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_apartments'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 111,
                  'y': current_page_height,
                  'w': 8,
                  'h': 6,
                  'txt': '{:,}'.format(int(competitor[0]['number_apts'])) if not competitor[0]['number_apts'] == '-' else competitor[0]['number_apts'],
                  'align': 'center',
                  'fill': True,
              }
              current_competitor_page['cell'][f'home_{home_counter}_empty'] = {
                  'color': [0, 0, 0],
                  'fill_color': [244, 239, 220],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 119,
                  'y': current_page_height,
                  'w': 84,
                  'h': 6,
                  'txt': "",
                  'align': 'center',
                  'fill': True,
              }
      
              if not competitor[0]['year_of_construction'] == '-':
                  list_years_of_construction_al.append(int(competitor[0]['year_of_construction']))
              if competitor[0]['type'] == 'gemeinnützig':
                  none_profit_operator_al += 1
              elif competitor[0]['type'] == 'kommunal':
                  public_operator_al += 1
              elif competitor[0]['type'] == 'privat':
                  private_operator_al += 1
      
          else:
              table_position = (index % 9) + 1
              if not prev_competitor_distance == competitor[1]:
                  prev_competitor_distance = competitor[1]
                  prev_competitor_index += 1
      
              current_competitor_page['cell'][f'competitor_{table_position}_icon'] = {
                  'color': [255, 255, 255],
                  'fill_color': [249, 147, 152],
                  'font': 'segoeui',
                  'size': 11,
                  'x': 10,
                  'y': current_page_height,
                  'w': 6,
                  'h': 10,
                  'txt': str(prev_competitor_index),
                  'align': 'center',
                  'fill': True
              }
              current_competitor_page['cell'][f'competitor_{table_position}_name'] = {
                  'color': [0, 176, 240] if not "keine " in competitor[0]['web'] else [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height,
                  'w': 50,
                  'h': 6,
                  'txt': competitor[0]['raw_name'] if len(competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
                  'align': 'left',
                  'link': competitor[0]['web'] if not "keine " in competitor[0]['web'] else ""
              }
              current_competitor_page['cell'][f'competitor_{table_position}_operator'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 17,
                  'y': current_page_height + 4,
                  'w': 50,
                  'h': 6,
                  'txt': competitor[0]['raw_betreiber'] if len(competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
                  'align': 'left'
              }
              current_competitor_page['cell'][f'competitor_{table_position}_top_30_operator'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 67,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_operator_type'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 77,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public",
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_status'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 89,
                  'y': current_page_height,
                  'w': 12,
                  'h': 6,
                  'txt': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_year_of_construction'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 101,
                  'y': current_page_height,
                  'w': 10,
                  'h': 6,
                  'txt': competitor[0]['year_of_construction'],
                  'align': 'center',
              }
              current_competitor_page['cell'][f'competitor_{table_position}_apartments'] = {
                  'color': [0, 0, 0],
                  'font': 'segoeui',
                  'size': 8,
                  'x': 111,
                  'y': current_page_height,
                  'w': 8,
                  'h': 6,
                  'txt': '{:,}'.format(int(competitor[0]['number_apts'])) if not competitor[0]['number_apts'] == '-' else competitor[0]['number_apts'],
                  'align': 'center',
              }
      
              if not competitor[0]['year_of_construction'] == '-':
                  list_years_of_construction_al.append(int(competitor[0]['year_of_construction']))
              if competitor[0]['type'] == 'gemeinnützig':
                  none_profit_operator_al += 1
              elif competitor[0]['type'] == 'kommunal':
                  public_operator_al += 1
              elif competitor[0]['type'] == 'privat':
                  private_operator_al += 1
      
          current_page_height += 12
      
          if index == len(data_comp_analysis_al['data']) - 1:
              competitor_pages[f'competitor_analysis_{page}'] = current_competitor_page
    
      market_study_data = {
          'number_of_pages': 0,
          'settings': {
              'fonts': ['segoeui', 'seguisb', 'segoeuisl', 'calibri']
          },
          'pages': {
              'cover': {
                      'rect': {
                          'blue_rect': {
                              'color': [32, 49, 68],
                              'x': 120,
                              'y': 0,
                              'w': 90,
                              'h': 297,
                              'style': 'F'
                          }
                      },
                      'text': {
                          'ms_heading': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 27,
                              'x': 10,
                              'y': 130,
                              'txt': 'Market Study'
                          },
                          'ms_care': {
                              'color': [200, 176, 88],
                              'font': 'seguisb',
                              'size': 80,
                              'x': 10,
                              'y': 155,
                              'txt': 'Care'
                          },
                          'street_heading': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 180,
                              'txt': 'Street, no.'
                          },
                          'zip_heading': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 186,
                              'txt': 'Zip code'
                          },
                          'city_heading': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 192,
                              'txt': 'City'
                          },
                          'district_heading': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 198,
                              'txt': 'District'
                          },
                          'federal_state_heading': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 204,
                              'txt': 'Federal State'
                          },
                          'country_heading': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 210,
                              'txt': 'Country'
                          },
                          'street_value': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 180,
                              'txt': street
                          },
                          'zip_value': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 186,
                              'txt': zipcode
                          },
                          'city_value': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 192,
                              'txt': city
                          },
                          'district_value': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 198,
                              'txt': district
                          },
                          'federal_state_value': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 204,
                              'txt': federal_state
                          },
                          'country_value': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 210,
                              'txt': 'Germany'
                          },
                          'radius_of_analysis': {
                              'color': [200, 176, 88],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 216,
                              'txt': 'Radius of analysis'
                          },
                          'radius_of_analysis_value': {
                              'color': [200, 176, 88],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 55,
                              'y': 216,
                              'txt': f'{iso_time} minutes of {iso_movement}'
                          },
                          'ms_text_1': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 240,
                              'txt': 'The'
                          },
                          'ms_text_2': {
                              'color': [0, 0, 0],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 18,
                              'y': 240,
                              'txt': 'Market Study'
                          },
                          'ms_text_3': {
                              'color': [200, 176, 88],
                              'font': 'seguisb',
                              'size': 12,
                              'x': 45,
                              'y': 240,
                              'txt': 'Care'
                          },
                          'ms_text_4': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 55,
                              'y': 240,
                              'txt': 'is a web based service'
                          },
                          'ms_text_5': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 246,
                              'txt': 'by Capital Bay, which provides investors with access'
                          },
                          'ms_text_6': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 252,
                              'txt': 'to data on the current German care market including'
                          },
                          'ms_text_7': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 258,
                              'txt': 'demographical forecasts and competitor analysis.'
                          },
                          'ms_text_8': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 264,
                              'txt': 'This allows for targeted examination of the market,'
                          },
                          'ms_text_9': {
                              'color': [0, 0, 0],
                              'font': 'segoeui',
                              'size': 12,
                              'x': 10,
                              'y': 270,
                              'txt': 'using protractile radii.'
                          },
                          'version': {
                              'color': [166, 166, 166],
                              'font': 'segoeui',
                              'size': 9,
                              'x': 10,
                              'y': 290,
                              'txt': f'Version 2.1.0 - Generated on {created_date}'
                          }
                      },
                      'image': {
                          'logo': {
                              'x': 147,
                              'y': 12,
                              'w': 36,
                              'path': "img/LogoTrans.png"
                          },
                          'map': {
                              'x': 135,
                              'y': 30,
                              'w': 60,
                              'path': f"tmp/summary_map_{Variables.unique_code}.png"
                          },
                          'population': {
                              'x': 161,
                              'y': 195,
                              'w': 8,
                              'path': "img/pop_trend.png"
                          },
                          'beds': {
                              'x': 158,
                              'y': 245,
                              'w': 14,
                              'path': "img/beds.png"
                          }
                      },
                      'cell': {
                          'keyfacts': {
                              'color': [200, 176, 88],
                              'font': 'seguisb',
                              'size': 14,
                              'x': 120,
                              'y': 150,
                              'w': 90,
                              'txt': 'LOCATION KEYFACTS',
                              'align': 'center'
                          },
                          'purchasing_power_value': {
                              'color': [255, 255, 255],
                              'font': 'segoeuisl',
                              'size': 36,
                              'x': 120,
                              'y': 180,
                              'w': 90,
                              'txt': '{:,}%'.format(purchase_power),
                              'align': 'center'
                          },
                          'population_value': {
                              'color': [255, 255, 255],
                              'font': 'segoeuisl',
                              'size': 36,
                              'x': 120,
                              'y': 230,
                              'w': 90,
                              'txt': '{:,}%'.format(float(population_trend)) if float(population_trend) < 0 else '+{:,}%'.format(float(population_trend)),
                              'align': 'center'
                          },
                          'beds_value': {
                              'color': [255, 255, 255],
                              'font': 'segoeuisl',
                              'size': 36,
                              'x': 120,
                              'y': 280,
                              'w': 90,
                              'txt': '{:,}'.format(beds_surplus_35_v2),
                              'align': 'center'
                          }
                      },
                      'multi_cell': {
                          'purchasing_power_heading': {
                              'color': [255, 255, 255],
                              'font': 'segoeui',
                              'size': 9,
                              'x': 120,
                              'y': 160,
                              'w': 90,
                              'h': 4,
                              'txt': 'Purchasing Power\nat the location - As of 2022',
                              'align': 'center'
                          },
                          'population_trend_heading': {
                              'color': [255, 255, 255],
                              'font': 'segoeui',
                              'size': 9,
                              'x': 120,
                              'y': 210,
                              'w': 90,
                              'h': 4,
                              'txt': 'Population trend of the 65+ age group\nat the location - 2035',
                              'align': 'center'
                          },
                          'beds_heading': {
                              'color': [255, 255, 255],
                              'font': 'segoeui',
                              'size': 9,
                              'x': 120,
                              'y': 260,
                              'w': 90,
                              'h': 4,
                              'txt': 'Surplus or deficit of beds\nat the location - 2035',
                              'align': 'center'
                          },
                      }
                  },
              'summary': {
                  'page_number': 2,
                  'rect': {
                      'blue_rect_1': {
                          'color': [32, 49, 68],
                          'x': 76,
                          'y': 50.3,
                          'w': 24,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'blue_rect_2': {
                          'color': [32, 49, 68],
                          'x': 76,
                          'y': 60.3,
                          'w': 24,
                          'h': 44.7,
                          'style': 'F'
                      },
                      'blue_rect_3': {
                          'color': [32, 49, 68],
                          'x': 76,
                          'y': 105.3,
                          'w': 24,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'blue_rect_4': {
                          'color': [32, 49, 68],
                          'x': 76,
                          'y': 115.3,
                          'w': 24,
                          'h': 52.7,
                          'style': 'F'
                      },
                      'blue_rect_5': {
                          'color': [32, 49, 68],
                          'x': 76,
                          'y': 168.3,
                          'w': 24,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'blue_rect_6': {
                          'color': [32, 49, 68],
                          'x': 76,
                          'y': 178.3,
                          'w': 24,
                          'h': 74.7,
                          'style': 'F'
                      },
                      'gray_rect_1': {
                          'color': [223, 223, 223],
                          'x': 101,
                          'y': 50.3,
                          'w': 49,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'gray_rect_2': {
                          'color': [223, 223, 223],
                          'x': 101,
                          'y': 60.3,
                          'w': 49,
                          'h': 44.7,
                          'style': 'F'
                      },
                      'gray_rect_3': {
                          'color': [223, 223, 223],
                          'x': 101,
                          'y': 105.3,
                          'w': 49,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'gray_rect_4': {
                          'color': [223, 223, 223],
                          'x': 101,
                          'y': 115.3,
                          'w': 49,
                          'h': 52.7,
                          'style': 'F'
                      },
                      'gray_rect_5': {
                          'color': [223, 223, 223],
                          'x': 101,
                          'y': 168.3,
                          'w': 49,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'gray_rect_6': {
                          'color': [223, 223, 223],
                          'x': 101,
                          'y': 178.3,
                          'w': 49,
                          'h': 74.7,
                          'style': 'F'
                      },
                      'lightgray_rect_1': {
                          'color': [242, 242, 242],
                          'x': 151,
                          'y': 50.3,
                          'w': 49,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'lightgray_rect_2': {
                          'color': [242, 242, 242],
                          'x': 151,
                          'y': 60.3,
                          'w': 49,
                          'h': 44.7,
                          'style': 'F'
                      },
                      'lightgray_rect_3': {
                          'color': [242, 242, 242],
                          'x': 151,
                          'y': 105.3,
                          'w': 49,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'lightgray_rect_4': {
                          'color': [242, 242, 242],
                          'x': 151,
                          'y': 115.3,
                          'w': 49,
                          'h': 52.7,
                          'style': 'F'
                      },
                      'lightgray_rect_5': {
                          'color': [242, 242, 242],
                          'x': 151,
                          'y': 168.3,
                          'w': 49,
                          'h': 9.7,
                          'style': 'F'
                      },
                      'lightgray_rect_6': {
                          'color': [242, 242, 242],
                          'x': 151,
                          'y': 178.3,
                          'w': 49,
                          'h': 74.7,
                          'style': 'F'
                      },
                      'demographic_top_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 50,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'demographic_bottom_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 60,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'demographic_top_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 50,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demographic_bottom_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 60,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demographic_top_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 50,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demographic_bottom_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 60,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'inpatient_care_top_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 105,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'inpatient_care_bottom_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 115,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'inpatient_care_top_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 105,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'inpatient_care_bottom_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 115,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'inpatient_care_top_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 105,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'inpatient_care_bottom_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 115,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demand_supply_top_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 168,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'demand_supply_bottom_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 178,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'demand_supply_top_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 168,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demand_supply_bottom_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 178,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demand_supply_top_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 168,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'demand_supply_bottom_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 178,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'final_line_1': {
                          'color': [0, 0, 0],
                          'x': 10,
                          'y': 253,
                          'w': 65,
                          'h': .3,
                          'style': 'F'
                      },
                      'final_line_2': {
                          'color': [0, 0, 0],
                          'x': 101,
                          'y': 253,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      },
                      'final_line_3': {
                          'color': [0, 0, 0],
                          'x': 151,
                          'y': 253,
                          'w': 49,
                          'h': .3,
                          'style': 'F'
                      }
                  },
                  'text': {
                      'heading_city': {
                          'color': [218, 218, 218],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 30,
                          'txt': city
                      },
                      'page_name': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 40,
                          'txt': 'Current Situation'
                      }
                  },
                  'cell': {
                      'demographic_trend_analysis': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 12,
                          'y': 55,
                          'w': 20,
                          'txt': 'Demographic trend analysis',
                          'align': 'left'
                      },
                      'population_city_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 65,
                          'w': 20,
                          'txt': f'Population {city} (City)',
                          'align': 'left'
                      },
                      'population_county_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 71,
                          'w': 20,
                          'txt': f'Population {countie[0]} (County)',
                          'align': 'left'
                      },
                      'population_county_in_percent_heading': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 12,
                          'y': 77,
                          'w': 20,
                          'txt': 'in %',
                          'align': 'left'
                      },
                      'population_aged_65_79_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 83,
                          'w': 20,
                          'txt': 'of which population aged 65-79 years',
                          'align': 'left'
                      },
                      'population_aged_65_79_in_percent_heading': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 15,
                          'y': 89,
                          'w': 20,
                          'txt': 'in %',
                          'align': 'left'
                      },
                      'population_aged_80_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 95,
                          'w': 20,
                          'txt': 'of which population aged 80+',
                          'align': 'left'
                      },
                      'population_aged_80_in_percent_heading': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 15,
                          'y': 101,
                          'w': 20,
                          'txt': 'in %',
                          'align': 'left'
                      },
                      'full_inpatient_care': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 12,
                          'y': 110,
                          'w': 20,
                          'txt': 'Full inpatient care',
                          'align': 'left'
                      },
                      'care_rate_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 133,
                          'w': 20,
                          'txt': 'Care rate of population',
                          'align': 'left'
                      },
                      'nursing_home_rate_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 139,
                          'w': 20,
                          'txt': 'There of nursing home rate',
                          'align': 'left'
                      },
                      'full_inpatient_care_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 145,
                          'w': 20,
                          'txt': 'Patients receiving full inpatient care',
                          'align': 'left'
                      },
                      'occupancy_rate_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 151,
                          'w': 20,
                          'txt': 'Occupancy rate',
                          'align': 'left'
                      },
                      'number_of_beds_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 157,
                          'w': 20,
                          'txt': 'Number of beds',
                          'align': 'left'
                      },
                      'number_of_free_beds_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 163,
                          'w': 20,
                          'txt': 'Number of free beds',
                          'align': 'left'
                      },
                      'demand_supply': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 12,
                          'y': 173,
                          'w': 20,
                          'txt': 'Demand & Supply',
                          'align': 'left'
                      },
                      'demand_supply_viewing_radius': {
                          'color': [200, 176, 88],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 183,
                          'w': 20,
                          'txt': f'Viewing radius: {iso_time} minutes of {iso_movement}',
                          'align': 'left'
                      },
                      'nursing_homes_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 189,
                          'w': 20,
                          'txt': 'Nursing homes',
                          'align': 'left'
                      },
                      'beds_supply_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 195,
                          'w': 20,
                          'txt': 'Beds in supply',
                          'align': 'left'
                      },
                      'demand_occupancy_rate_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 201,
                          'w': 20,
                          'txt': 'Occupancy rate',
                          'align': 'left'
                      },
                      'planned_nursing_homes_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 207,
                          'w': 20,
                          'txt': 'Nursing homes in planning',
                          'align': 'left'
                      },
                      'constructing_nursing_homes_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 213,
                          'w': 20,
                          'txt': 'Nursing homes under construction',
                          'align': 'left'
                      },
                      'beds_planning_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 219,
                          'w': 20,
                          'txt': 'Beds in planning',
                          'align': 'left'
                      },
                      'beds_constructing_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 225,
                          'w': 20,
                          'txt': 'Beds under construction',
                          'align': 'left'
                      },
                      'loss_of_beds_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 231,
                          'w': 20,
                          'txt': 'Beds lost while meeting federal state law',
                          'align': 'left'
                      },
                      'adjusted_beds_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 237,
                          'w': 20,
                          'txt': 'Adjusted number of beds',
                          'align': 'left'
                      },
                      'demand_inpatients_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 243,
                          'w': 20,
                          'txt': 'Demand of number of inpatients',
                          'align': 'left'
                      },
                      'surplus_deficit_heading': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 12,
                          'y': 249,
                          'w': 20,
                          'txt': 'Surplus or deficit of beds',
                          'align': 'left'
                      },
                      'scenario_1_text': {
                          'color': [128, 128, 128],
                          'font': 'segoeui',
                          'size': 7,
                          'x': 12,
                          'y': 275,
                          'w': 20,
                          'txt': '¹In scenario 1 the relative situation (product of nursing home rate and care rate) as in 2020 is assumed to be constant for the entire forecasting period.',
                          'align': 'left'
                      },
                      'scenario_2_text': {
                          'color': [128, 128, 128],
                          'font': 'segoeui',
                          'size': 7,
                          'x': 12,
                          'y': 281,
                          'w': 20,
                          'txt': '²In scenario 2, it is assumed that the proportion of the nursing home rate will increase by 0.003 percent-points from 2020 to 2035.',
                          'align': 'left'
                      },
                      '2020_heading': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 76,
                          'y': 55,
                          'w': 23,
                          'txt': '2020',
                          'align': 'right'
                      },
                      'population_city_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 65,
                          'w': 23,
                          'txt': '{:,}'.format(countie_data['dem_city']['bevoelkerung_ges']),
                          'align': 'right'
                      },
                      'population_county_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 71,
                          'w': 23,
                          'txt': '{:,}'.format(countie_data['ex_dem_lk']['all_compl']),
                          'align': 'right'
                      },
                      'population_county_in_percent_2020': {
                          'color': [255, 255, 255],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 76,
                          'y': 77,
                          'w': 23,
                          'txt': '100%',
                          'align': 'right'
                      },
                      'population_aged_65_79_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 83,
                          'w': 23,
                          'txt': '{:,}'.format(people_u80),
                          'align': 'right'
                      },
                      'population_aged_65_79_in_percent_2020': {
                          'color': [255, 255, 255],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 76,
                          'y': 89,
                          'w': 23,
                          'txt': '{:,}%'.format(round(people_u80 * 100 / countie_data['ex_dem_lk']['all_compl'])),
                          'align': 'right'
                      },
                      'population_aged_80_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 95,
                          'w': 23,
                          'txt': '{:,}'.format(people_o80),
                          'align': 'right'
                      },
                      'population_aged_80_in_percent_2020': {
                          'color': [255, 255, 255],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 76,
                          'y': 101,
                          'w': 23,
                          'txt': '{:,}%'.format(round(people_o80 * 100 / countie_data['ex_dem_lk']['all_compl'])),
                          'align': 'right'
                      },
                      'care_rate_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 133,
                          'w': 23,
                          'txt': '{:,}%'.format(new_care_rate_raw),
                          'align': 'right'
                      },
                      'nursing_home_rate_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 139,
                          'w': 23,
                          'txt': '{:,}%'.format(nursing_home_rate),
                          'align': 'right'
                      },
                      'full_inpatient_care_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 145,
                          'w': 23,
                          'txt': '{:,}'.format(inpatients_lk),
                          'align': 'right'
                      },
                      'occupancy_rate_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 151,
                          'w': 23,
                          'txt': '{:,}%'.format(occupancy_lk),
                          'align': 'right'
                      },
                      'number_of_beds_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 157,
                          'w': 23,
                          'txt': '{:,}'.format(beds_lk),
                          'align': 'right'
                      },
                      'number_of_free_beds_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 163,
                          'w': 23,
                          'txt': '{:,}'.format(free_beds_lk),
                          'align': 'right'
                      },
                      'nursing_homes_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 189,
                          'w': 23,
                          'txt': '{:,}'.format(nursing_homes_active),
                          'align': 'right'
                      },
                      'beds_supply_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 195,
                          'w': 23,
                          'txt': '{:,}'.format(beds_active),
                          'align': 'right'
                      },
                      'demand_occupancy_rate_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 201,
                          'w': 23,
                          'txt': '{:,}%'.format(occupancy_lk),
                          'align': 'right'
                      },
                      'planned_nursing_homes_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 207,
                          'w': 23,
                          'txt': '-' if nursing_homes_planned == 0 else '{:,}'.format(nursing_homes_planned),
                          'align': 'right'
                      },
                      'constructing_nursing_homes_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 213,
                          'w': 23,
                          'txt': '-' if nursing_homes_construct == 0 else '{:,}'.format(nursing_homes_construct),
                          'align': 'right'
                      },
                      'beds_planning_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 219,
                          'w': 23,
                          'txt': '-' if beds_planned == 0 else '{:,}'.format(beds_planned),
                          'align': 'right'
                      },
                      'beds_constructing_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 225,
                          'w': 23,
                          'txt': '-' if beds_construct == 0 else '{:,}'.format(beds_construct),
                          'align': 'right'
                      },
                      'adjusted_beds_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 237,
                          'w': 23,
                          'txt': '{:,}'.format(beds_active),
                          'align': 'right'
                      },
                      'demand_inpatients_2020': {
                          'color': [255, 255, 255],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 76,
                          'y': 243,
                          'w': 23,
                          'txt': '{:,}'.format(inpatients),
                          'align': 'right'
                      },
                      '2030_heading': {
                          'color': [0, 0, 0],
                          'fill_color': [223, 223, 223],
                          'font': 'segoeui',
                          'size': 12,
                          'x': 101,
                          'y': 50,
                          'w': 48,
                          'h': 10,
                          'txt': '2030',
                          'align': 'right'
                      },
                      'population_county_2030': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 71,
                          'w': 48,
                          'txt': '{:,}'.format(population_fc_30),
                          'align': 'right'
                      },
                      'population_county_in_percent_2030': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 77,
                          'w': 48,
                          'txt': '100%',
                          'align': 'right'
                      },
                      'population_aged_65_79_2030': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 83,
                          'w': 48,
                          'txt': '{:,}'.format(people_u80_fc),
                          'align': 'right'
                      },
                      'population_aged_65_79_in_percent_2030': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 89,
                          'w': 48,
                          'txt': '{:,}%'.format(round((people_u80_fc * 100) / population_fc_30)),
                          'align': 'right'
                      },
                      'population_aged_80_2030': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 95,
                          'w': 48,
                          'txt': '{:,}'.format(people_o80_fc),
                          'align': 'right'
                      },
                      'population_aged_80_in_percent_2030': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 101,
                          'w': 48,
                          'txt': '{:,}%'.format(round((people_o80_fc * 100) / population_fc_30)),
                          'align': 'right'
                      },
                      'scenario_1_2030': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 101,
                          'y': 120,
                          'w': 23,
                          'txt': 'Scenario 1',
                          'align': 'right'
                      },
                      'care_rate_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 133,
                          'w': 23,
                          'txt': '{:,}%'.format(care_rate_30_v1_raw),
                          'align': 'right'
                      },
                      'nursing_home_rate_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 139,
                          'w': 23,
                          'txt': '{:,}%'.format(nursing_home_rate),
                          'align': 'right'
                      },
                      'full_inpatient_care_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 145,
                          'w': 23,
                          'txt': '{:,}'.format(pat_rec_full_care_fc_30_v1),
                          'align': 'right'
                      },
                      'occupancy_rate_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 151,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'number_of_beds_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 157,
                          'w': 23,
                          'txt': '{:,}'.format(beds_30_v1),
                          'align': 'right'
                      },
                      'number_of_free_beds_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 163,
                          'w': 23,
                          'txt': '{:,}'.format(free_beds_30_v1),
                          'align': 'right'
                      },
                      'beds_supply_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 195,
                          'w': 23,
                          'txt': '{:,}'.format(beds_active + beds_planned + beds_construct),
                          'align': 'right'
                      },
                      'demand_occupancy_rate_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 201,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'loss_of_beds_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 231,
                          'w': 23,
                          'txt': '{:,}'.format(loss_of_beds),
                          'align': 'right'
                      },
                      'adjusted_beds_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 237,
                          'w': 23,
                          'txt': '{:,}'.format(beds_adjusted_30_v1),
                          'align': 'right'
                      },
                      'demand_inpatients_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 243,
                          'w': 23,
                          'txt': '{:,}'.format(inpatients_fc),
                          'align': 'right'
                      },
                      'surplus_deficit_2030_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 101,
                          'y': 249,
                          'w': 23,
                          'txt': '{:,}'.format(beds_surplus),
                          'align': 'right'
                      },
                      'scenario_2_2030': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 125,
                          'y': 120,
                          'w': 23,
                          'txt': 'Scenario 2',
                          'align': 'right'
                      },
                      'care_rate_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 133,
                          'w': 23,
                          'txt': '{:,}%'.format(care_rate_30_v2_raw),
                          'align': 'right'
                      },
                      'nursing_home_rate_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 139,
                          'w': 23,
                          'txt': '{:,}%'.format(nursing_home_rate),
                          'align': 'right'
                      },
                      'full_inpatient_care_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 145,
                          'w': 23,
                          'txt': '{:,}'.format(pat_rec_full_care_fc_30_v2),
                          'align': 'right'
                      },
                      'occupancy_rate_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 151,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'number_of_beds_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 157,
                          'w': 23,
                          'txt': '{:,}'.format(beds_30_v2),
                          'align': 'right'
                      },
                      'number_of_free_beds_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 163,
                          'w': 23,
                          'txt': '{:,}'.format(free_beds_30_v2),
                          'align': 'right'
                      },
                      'beds_supply_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 195,
                          'w': 23,
                          'txt': '{:,}'.format(beds_active + beds_planned + beds_construct),
                          'align': 'right'
                      },
                      'demand_occupancy_rate_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 201,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'loss_of_beds_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 231,
                          'w': 23,
                          'txt': '{:,}'.format(loss_of_beds),
                          'align': 'right'
                      },
                      'adjusted_beds_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 237,
                          'w': 23,
                          'txt': '{:,}'.format(beds_adjusted_30_v2),
                          'align': 'right'
                      },
                      'demand_inpatients_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 243,
                          'w': 23,
                          'txt': '{:,}'.format(inpatients_fc_v2),
                          'align': 'right'
                      },
                      'surplus_deficit_2030_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 125,
                          'y': 249,
                          'w': 23,
                          'txt': '{:,}'.format(beds_surplus_v2),
                          'align': 'right'
                      },
                      '2035_heading': {
                          'color': [0, 0, 0],
                          'fill_color': [242, 242, 242],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 151,
                          'y': 50,
                          'w': 48,
                          'h': 10,
                          'txt': '2035',
                          'align': 'right'
                      },
                      'population_county_2035': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 71,
                          'w': 48,
                          'txt': '{:,}'.format(population_fc_35),
                          'align': 'right'
                      },
                      'population_county_in_percent_2035': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 77,
                          'w': 48,
                          'txt': '100%',
                          'align': 'right'
                      },
                      'population_aged_65_79_2035': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 83,
                          'w': 48,
                          'txt': '{:,}'.format(people_u80_fc_35),
                          'align': 'right'
                      },
                      'population_aged_65_79_in_percent_2035': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 89,
                          'w': 48,
                          'txt': '{:,}%'.format(round(people_u80_fc_35 * 100 / population_fc_35)),
                          'align': 'right'
                      },
                      'population_aged_80_2035': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 95,
                          'w': 48,
                          'txt': '{:,}'.format(people_o80_fc_35),
                          'align': 'right'
                      },
                      'population_aged_80_in_percent_2035': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 101,
                          'w': 48,
                          'txt': '{:,}%'.format(round(people_o80_fc_35 * 100 / population_fc_35)),
                          'align': 'right'
                      },
                      'scenario_1_2035': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 151,
                          'y': 120,
                          'w': 23,
                          'txt': 'Scenario 1',
                          'align': 'right'
                      },
                      'care_rate_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 133,
                          'w': 23,
                          'txt': '{:,}%'.format(care_rate_35_v1_raw),
                          'align': 'right'
                      },
                      'nursing_home_rate_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 139,
                          'w': 23,
                          'txt': '{:,}%'.format(nursing_home_rate),
                          'align': 'right'
                      },
                      'full_inpatient_care_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 145,
                          'w': 23,
                          'txt': '{:,}'.format(pat_rec_full_care_fc_35_v1),
                          'align': 'right'
                      },
                      'occupancy_rate_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 151,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'number_of_beds_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 157,
                          'w': 23,
                          'txt': '{:,}'.format(beds_35_v1),
                          'align': 'right'
                      },
                      'number_of_free_beds_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 163,
                          'w': 23,
                          'txt': '{:,}'.format(free_beds_35_v1),
                          'align': 'right'
                      },
                      'beds_supply_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 195,
                          'w': 23,
                          'txt': '{:,}'.format(beds_active + beds_planned + beds_construct),
                          'align': 'right'
                      },
                      'demand_occupancy_rate_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 201,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'loss_of_beds_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 231,
                          'w': 23,
                          'txt': '{:,}'.format(loss_of_beds),
                          'align': 'right'
                      },
                      'adjusted_beds_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 237,
                          'w': 23,
                          'txt': '{:,}'.format(beds_adjusted_35_v1),
                          'align': 'right'
                      },
                      'demand_inpatients_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 243,
                          'w': 23,
                          'txt': '{:,}'.format(inpatients_fc_35),
                          'align': 'right'
                      },
                      'surplus_deficit_2035_s1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 151,
                          'y': 249,
                          'w': 23,
                          'txt': '{:,}'.format(beds_surplus_35),
                          'align': 'right'
                      },
                      'scenario_2_2035': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 175,
                          'y': 120,
                          'w': 24,
                          'txt': 'Scenario 2',
                          'align': 'right'
                      },
                      'care_rate_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 133,
                          'w': 23,
                          'txt': '{:,}%'.format(care_rate_35_v2_raw),
                          'align': 'right'
                      },
                      'nursing_home_rate_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 139,
                          'w': 23,
                          'txt': '{:,}%'.format(nursing_home_rate),
                          'align': 'right'
                      },
                      'full_inpatient_care_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 145,
                          'w': 23,
                          'txt': '{:,}'.format(pat_rec_full_care_fc_35_v2),
                          'align': 'right'
                      },
                      'occupancy_rate_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 151,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'number_of_beds_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 157,
                          'w': 23,
                          'txt': '{:,}'.format(beds_35_v2),
                          'align': 'right'
                      },
                      'number_of_free_beds_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 163,
                          'w': 23,
                          'txt': '{:,}'.format(free_beds_35_v2),
                          'align': 'right'
                      },
                      'beds_supply_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 195,
                          'w': 23,
                          'txt': '{:,}'.format(beds_active + beds_planned + beds_construct),
                          'align': 'right'
                      },
                      'demand_occupancy_rate_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 201,
                          'w': 23,
                          'txt': '95.0%',
                          'align': 'right'
                      },
                      'loss_of_beds_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 231,
                          'w': 23,
                          'txt': '{:,}'.format(loss_of_beds),
                          'align': 'right'
                      },
                      'adjusted_beds_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 237,
                          'w': 23,
                          'txt': '{:,}'.format(beds_adjusted_35_v2),
                          'align': 'right'
                      },
                      'demand_inpatients_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 243,
                          'w': 23,
                          'txt': '{:,}'.format(inpatients_fc_35_v2),
                          'align': 'right'
                      },
                      'surplus_deficit_2035_s2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 175,
                          'y': 249,
                          'w': 23,
                          'txt': '{:,}'.format(beds_surplus_35_v2),
                          'align': 'right'
                      }
                  },
                  'multi_cell': {
                      'scenario_1_2030_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 7,
                          'x': 101,
                          'y': 122,
                          'w': 24,
                          'h': 4,
                          'txt': "Constant care\nsituation¹",
                          'align': 'right'
                      },
                      'scenario_2_2030_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 7,
                          'x': 125,
                          'y': 122,
                          'w': 24,
                          'h': 4,
                          'txt': "Increase in care needs of 0,003%²",
                          'align': 'right'
                      },
                      'scenario_1_2035_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 7,
                          'x': 151,
                          'y': 122,
                          'w': 24,
                          'h': 4,
                          'txt': "Constant care\nsituation¹",
                          'align': 'right'
                      },
                      'scenario_2_2035_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 7,
                          'x': 175,
                          'y': 122,
                          'w': 24,
                          'h': 4,
                          'txt': "Increase in care needs of 0,003%²",
                          'align': 'right'
                      }
                  },
              },
              'location_analysis': {
                  'page_number': 3,
                  'text': {
                      'heading_city': {
                          'color': [218, 218, 218],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 30,
                          'txt': city
                      },
                      'page_name': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 40,
                          'txt': 'Location Analysis'
                      },
                      'investment_object': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 30,
                          'y': 210,
                          'txt': 'Investment object'
                      },
                      'nursing_home_competitor': {
                          'color': [128, 128, 128],
                          'font': 'segoeuisl',
                          'size': 9,
                          'x': 30,
                          'y': 216,
                          'txt': 'Competitor'
                      },
                      'nursing_home': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 30,
                          'y': 220,
                          'txt': 'Nursing home'
                      },
                      'assisted_living_competitor': {
                          'color': [128, 128, 128],
                          'font': 'segoeuisl',
                          'size': 9,
                          'x': 30,
                          'y': 226,
                          'txt': 'Competitor'
                      },
                      'assisted_living': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 30,
                          'y': 230,
                          'txt': 'Assisted Living'
                      },
                      'nursing_home_assisted_living_competitor': {
                          'color': [128, 128, 128],
                          'font': 'segoeuisl',
                          'size': 9,
                          'x': 30,
                          'y': 236,
                          'txt': 'Competitor'
                      },
                      'nursing_home_assisted_living': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 30,
                          'y': 240,
                          'txt': 'Nursing home & Assisted living'
                      },
                      'distance_layer': {
                          'color': [128, 128, 128],
                          'font': 'segoeuisl',
                          'size': 9,
                          'x': 30,
                          'y': 246,
                          'txt': 'Distance layer'
                      },
                      'distance_amount': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 30,
                          'y': 250,
                          'txt': f'{iso_time} minutes of {iso_movement}'
                      }
                  },
                  'image': {
                      'location_map': {
                          'x': 10,
                          'y': 50,
                          'w': 200,
                          'path': f"tmp/map_image_{Variables.unique_code}.png"
                      },
                      'invest_marker': {
                          'x': 13.5,
                          'y': 204,
                          'w': 8,
                          'path': "img/home_pin.png"
                      },
                      'nursing_home_marker': {
                          'x': 14,
                          'y': 214,
                          'w': 7,
                          'path': "img/nh_pin.png"
                      },
                      'assisted_living_marker': {
                          'x': 14,
                          'y': 224,
                          'w': 7,
                          'path': "img/al_pin.png"
                      },
                      'nh_al_marker': {
                          'x': 15,
                          'y': 234,
                          'w': 7,
                          'path': "img/mixed_pin.png"
                      },
                      'distance_layer': {
                          'x': 15,
                          'y': 244,
                          'w': 7,
                          'path': "img/distance_layer.png"
                      },
                      'web_view': {
                          'x': 178,
                          'y': 55,
                          'w': 25,
                          'path': "img/web_view.png",
                          'link': share_url
                      }
                  },
                  'multi_cell': {
                      'gpt_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 115,
                          'y': 205,
                          'w': 85,
                          'h': 4,
                          'txt': analysis_text,
                          'align': 'left'
                      }
                  }
              },
              'good_to_know': {
                  'page_number': 7,
                  'line': {
                      'operator_top_line': {
                          'x1': 10,
                          'y1': 65,
                          'x2': 100,
                          'y2': 65
                      },
                      'operator_bottom_line': {
                          'x1': 10,
                          'y1': 76,
                          'x2': 100,
                          'y2': 76
                      },
                      'prices_top_line': {
                          'x1': 110,
                          'y1': 65,
                          'x2': 203,
                          'y2': 65
                      },
                      'prices_bottom_line': {
                          'x1': 110,
                          'y1': 76,
                          'x2': 203,
                          'y2': 76
                      },
                      'purchase_power_top_line': {
                          'x1': 10,
                          'y1': 199,
                          'x2': 100,
                          'y2': 199
                      },
                      'purchase_power_bottom_line': {
                          'x1': 10,
                          'y1': 210,
                          'x2': 100,
                          'y2': 210
                      }
                  },
                  'text': {
                      'heading_city': {
                          'color': [218, 218, 218],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 30,
                          'txt': city
                      },
                      'page_name': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 40,
                          'txt': 'Good to know'
                      },
                      'market_shares': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 17,
                          'x': 10,
                          'y': 55,
                          'txt': 'Market shares'
                      },
                      'operator': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 10,
                          'y': 72,
                          'txt': 'Operator'
                      },
                      'prices': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 110,
                          'y': 72,
                          'txt': 'Prices'
                      },
                      'purchase_power': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 10,
                          'y': 206,
                          'txt': 'Purchasing power index (municipality)'
                      }
                  },
                  'image': {
                      'operator_chart': {
                          'x': -5,
                          'y': 105,
                          'w': 120,
                          'path': "tmp/operator_chart.png"
                      },
                      'invest_scatter_chart': {
                          'x': 105,
                          'y': 85,
                          'w': 100,
                          'path': "tmp/invest_cost_scatter_chart.png"
                      },
                      'purchasing_power_chart': {
                          'x': 10,
                          'y': 190,
                          'w': 90,
                          'path': "tmp/purchasing_power_chart.png"
                      }
                  },
                  'cell': {
                      'operator_viewing_radius': {
                          'color': [200, 176, 88],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 80,
                          'w': 20,
                          'txt': f"Viewing radius: {iso_time} minutes of {iso_movement}",
                          'align': 'left'
                      },
                      'number_facilities_nh': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 85,
                          'w': 20,
                          'txt': 'Number of facilities (NH)',
                          'align': 'left'
                      },
                      'number_facilities_nh_value': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 80,
                          'y': 85,
                          'w': 20,
                          'txt': '{:,}'.format(len(data_comp_analysis_nh['data'])),
                          'align': 'right'
                      },
                      'number_facilities_al': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 90,
                          'w': 20,
                          'txt': 'Number of facilities (AL)',
                          'align': 'left'
                      },
                      'number_facilities_al_value': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 80,
                          'y': 90,
                          'w': 20,
                          'txt': '{:,}'.format(len(data_comp_analysis_al['data'])),
                          'align': 'right'
                      },
                      'median_beds': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 95,
                          'w': 20,
                          'txt': 'Median numbers of beds (NH)',
                          'align': 'left'
                      },
                      'median_beds_value': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 80,
                          'y': 95,
                          'w': 20,
                          'txt': '20',
                          'align': 'right'
                      },
                      'median_year_of_construct_nh': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 100,
                          'w': 20,
                          'txt': 'Median year of construction (NH)',
                          'align': 'left'
                      },
                      'median_year_of_construct_value': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 80,
                          'y': 100,
                          'w': 20,
                          'txt': '1997',
                          'align': 'right'
                      },
                      'median_year_of_construct_al': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 105,
                          'w': 20,
                          'txt': 'Median year of construction (AL)',
                          'align': 'left'
                      },
                      'median_year_of_construct_al_value': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 80,
                          'y': 105,
                          'w': 20,
                          'txt': '2010',
                          'align': 'right'
                      },
                      'operator_types': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 10,
                          'y': 115,
                          'w': 20,
                          'txt': 'Operator types',
                          'align': 'left'
                      },
                      'prices_viewing_radius': {
                          'color': [200, 176, 88],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 110,
                          'y': 80,
                          'w': 20,
                          'txt': f"Viewing radius: {iso_time} minutes of {iso_movement}",
                          'align': 'left'
                      },
                      'invest_cost_nursing_home': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 110,
                          'y': 85,
                          'w': 20,
                          'txt': 'Invest costs in Nursing homes',
                          'align': 'left'
                      }
                  },
                  'multi_cell': {
                      'invest_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 110,
                          'y': 270,
                          'w': 90,
                          'h': 4,
                          'txt': f"The investment cost rates of the facilities within the catchment area range between €{minimum_invest_cost} and €{maximum_invest_cost}.  The median investment cost amount to €{'{:.2f}'.format(total_invest_cost)}. {f'The investment costs at the facility, that is subject to this study amounts to €{home_invest}.' if not home_invest == -1 else ''}",
                          'align': 'left'
                      }
                  }
              },
              'regulations': {
                  'page_number': 8,
                  'rect': {
                      'grey_rect': {
                          'color': [242, 242, 242],
                          'x': 10,
                          'y': 50,
                          'w': 190,
                          'h': 110,
                          'style': 'F'
                      }
                  },
                  'line': {
                      'state_top_line': {
                          'x1': 15,
                          'y1': 84,
                          'x2': 195,
                          'y2': 84
                      },
                      'state_bottom_line': {
                          'x1': 15,
                          'y1': 95,
                          'x2': 195,
                          'y2': 95
                      }
                  },
                  'text': {
                      'heading_city': {
                          'color': [218, 218, 218],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 30,
                          'txt': city
                      },
                      'page_name': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 40,
                          'txt': 'Regulations'
                      }
                  },
                  'cell': {
                      'regulations_heading': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 15,
                          'x': 15,
                          'y': 60,
                          'w': 20,
                          'txt': 'Regulations of federal state',
                          'align': 'left'
                      },
                      'federal_state': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 15,
                          'y': 90,
                          'w': 20,
                          'txt': 'Federal state',
                          'align': 'left'
                      },
                      'federal_state_value': {
                          'color': [255, 255, 255],
                          'fill_color': [32, 49, 68],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 85,
                          'y': 84,
                          'w': 110,
                          'h': 11,
                          'txt': regulations['federal_state'],
                          'align': 'left',
                          'fill': True
                      },
                      'single_room_quota': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 110,
                          'w': 20,
                          'txt': 'Single room quota (min.)',
                          'align': 'left'
                      },
                      'home_size': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 116,
                          'w': 20,
                          'txt': 'Maximum home size',
                          'align': 'left'
                      },
                      'room_size': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 122,
                          'w': 20,
                          'txt': 'Minimum room size (SR/DR)',
                          'align': 'left'
                      },
                      'common_area': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 128,
                          'w': 20,
                          'txt': 'Minimum common area/residential',
                          'align': 'left'
                      },
                      'comment': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 134,
                          'w': 20,
                          'txt': 'Comment',
                          'align': 'left'
                      },
                      'legal_basis': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 9,
                          'x': 15,
                          'y': 153,
                          'w': 20,
                          'txt': 'Legal basis',
                          'align': 'left'
                      },
                      'new': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 85,
                          'y': 100,
                          'w': 20,
                          'txt': 'New',
                          'align': 'left'
                      },
                      'new_single_room_quota': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 85,
                          'y': 110,
                          'w': 20,
                          'txt': f"{int(regulations['New']['sr_quote_raw'] * 100)}%" if not type(regulations['New']['sr_quote_raw']) == str else regulations['New']['sr_quote_raw'],
                          'align': 'left'
                      },
                      'new_home_size': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 85,
                          'y': 116,
                          'w': 20,
                          'txt': regulations['New']['max_beds_raw'],
                          'align': 'left'
                      },
                      'new_room_size': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 85,
                          'y': 122,
                          'w': 20,
                          'txt': regulations['New']['min_room_size'],
                          'align': 'left'
                      },
                      'new_common_area': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 85,
                          'y': 128,
                          'w': 20,
                          'txt': regulations['New']['min_common_area_resident'],
                          'align': 'left'
                      },
                      'new_legal_basis': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 85,
                          'y': 153,
                          'w': 20,
                          'txt': regulations['New']['legal_basis'],
                          'align': 'left'
                      },
                      'existing': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 140,
                          'y': 100,
                          'w': 20,
                          'txt': 'Existing',
                          'align': 'left'
                      },
                      'existing_single_room_quota': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 140,
                          'y': 110,
                          'w': 20,
                          'txt': f"{int(regulations['Existing']['sr_quote_raw'] * 100)}%" if not type(regulations['Existing']['sr_quote_raw']) == str else regulations['Existing']['sr_quote_raw'],
                          'align': 'left'
                      },
                      'existing_home_size': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 140,
                          'y': 116,
                          'w': 20,
                          'txt': regulations['Existing']['max_beds_raw'],
                          'align': 'left'
                      },
                      'existing_room_size': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 140,
                          'y': 122,
                          'w': 20,
                          'txt': regulations['Existing']['min_room_size'],
                          'align': 'left'
                      },
                      'existing_common_area': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 140,
                          'y': 128,
                          'w': 20,
                          'txt': regulations['Existing']['min_common_area_resident'],
                          'align': 'left'
                      },
                      'existing_legal_basis': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 140,
                          'y': 153,
                          'w': 20,
                          'txt': regulations['Existing']['legal_basis'],
                          'align': 'left'
                      }
                  },
                  'multi_cell': {
                      'regulations_text': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 8,
                          'x': 15,
                          'y': 70,
                          'w': 180,
                          'h': 4,
                          'txt': f"This market study consideres {len(data_comp_analysis_nh['data'])} nursing homes within the vicinity of {iso_time} minutes {iso_movement}. Thereof, {complied_regulations} facilities comply with the federal state regulations and {uncomplied_regulations} facilities that do not fullfill the federal requirements. Assuming that only 80% of the respective facilities need to comply with the below shown federal state regulations, the resulting loss of beds in the market until 2030 will amount to {loss_of_beds}.",
                          'align': 'left'
                      },
                      'new_comment': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 85,
                          'y': 134,
                          'w': 55,
                          'h': 4,
                          'txt': regulations['New']['comment'],
                          'align': 'left'
                      },
                      'existing_comment': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 140,
                          'y': 134,
                          'w': 55,
                          'h': 4,
                          'txt': regulations['Existing']['comment'],
                          'align': 'left'
                      }
                  }
              },
              'methodic': {
                  'page_number': 9,
                  'rect': {
                      'grey_rect': {
                          'color': [242, 242, 242],
                          'x': 10,
                          'y': 50,
                          'w': 205,
                          'h': 227,
                          'style': 'F'
                      }
                  },
                  'text': {
                      'about_the_study': {
                          'color': [218, 218, 218],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 30,
                          'txt': 'About the study'
                      },
                      'methodic': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 40,
                          'txt': 'Methodic'
                      }
                  },
                  'multi_cell': {
                      'heading_1': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 15,
                          'y': 65,
                          'w': 80,
                          'h': 4,
                          'txt': 'Methodology, Data analysis &\nforecasting',
                          'align': 'left'
                      },
                      'paragraph_1': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 15,
                          'y': 80,
                          'w': 80,
                          'h': 4,
                          'txt': 'The market study highlights the current state of the\ninpatient care market in Germany and provides a\nforecast for the demand for nursing care until 2030\nand 2035. The study emphasizes the key drivers of\ndemand and the methodology employed to arrive at\nthe forecasted figures\n\nThe study utilizes a combination of publicly available\nsecondary research. Secondary research includes\nanalyzing geographical, demographical and\nstatistical databases as well as government\npublications and reputable healthcare sources to\ngather quantitative data.\n\nThe collected data is analyzed to identify trends,\ngrowth drivers, and market dynamics. The analysis\nencompasses factors such as population\ndemographics, healthcare policies and available\nmarket information on existing and future care\nfacilities, prevalence of chronic diseases, and\neconomic indicators affecting the demand for\ninpatient care.\n\nTo forecast the future demand for nursing care, a\ncombination of demographic projection, trend\nanalysis and consideration of new care facilities to\nbe launched on the market is employed.\nDemographic projection takes into account\npopulation growth, aging trends, and migration\npatterns. Trend analysis examines historical data and\nidentifies patterns and growth rates to project future\ndemand. New care facilities takes into account\nbuildings that are in planning or under construction.\n\nAll findings of the market study will consider the\nfactors mentioned above to provide a\ncomprehensive understanding of the current state of\nthe inpatient care market.',
                          'align': 'left'
                      },
                      'heading_2': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 15,
                          'y': 240,
                          'w': 70,
                          'h': 4,
                          'txt': 'Limitations',
                          'align': 'left'
                      },
                      'paragraph_2': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 15,
                          'y': 250,
                          'w': 80,
                          'h': 4,
                          'txt': 'The forecast is based on available data and assumes\nthat there will be no major disruptive events or\npolicy changes that could significantly impact the\ndemand for inpatient care.',
                          'align': 'left'
                      },
                      'heading_3': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 120,
                          'y': 68,
                          'w': 80,
                          'h': 4,
                          'txt': 'Data sources',
                          'align': 'left'
                      },
                      'paragraph_3': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 120,
                          'y': 80,
                          'w': 80,
                          'h': 4,
                          'txt': 'Statistisches Bundesamt\nStatista\nPflegemarkt.com\nPflegemarktdatenbank (updates every 3 months)\nDemografieportal\nPflegeheim-Atlas Deutschland 2021, Wuest Partner\n21st Real Estate\nChatGPT\nOpen Street Maps\nMalbox',
                          'align': 'left'
                      }
                  }
              },
              'contact': {
                  'page_number': 10,
                  'rect': {
                      'grey_rect': {
                          'color': [242, 242, 242],
                          'x': 10,
                          'y': 50,
                          'w': 205,
                          'h': 60,
                          'style': 'F'
                      }
                  },
                  'text': {
                      'keep_in_touch': {
                          'color': [218, 218, 218],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 30,
                          'txt': 'Keep in touch'
                      },
                      'capital_bay_team': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 27,
                          'x': 10,
                          'y': 40,
                          'txt': 'Capital Bay Team'
                      },
                      'left_person_name': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 25,
                          'y': 65,
                          'txt': 'Stephanie Kühn'
                      },
                      'left_person_position': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 25,
                          'y': 70,
                          'txt': 'Head of Transaction Management'
                      },
                      'left_person_company': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 25,
                          'y': 75,
                          'txt': 'CB Transaction Management GmbH'
                      },
                      'left_person_address': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 25,
                          'y': 80,
                          'txt': 'Sachsendamm 4/5, 10829 Berlin'
                      },
                      'left_person_phone': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 25,
                          'y': 85,
                          'txt': 'T + 49 30 120866215'
                      },
                      'right_person_name': {
                          'color': [0, 0, 0],
                          'font': 'seguisb',
                          'size': 12,
                          'x': 100,
                          'y': 65,
                          'txt': 'Daniel Ziv'
                      },
                      'right_person_position': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 100,
                          'y': 70,
                          'txt': 'Junior Transaction Manager'
                      },
                      'right_person_company': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 100,
                          'y': 75,
                          'txt': 'CB Transaction Management GmbH'
                      },
                      'right_person_address': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 100,
                          'y': 80,
                          'txt': 'Sachsendamm 4/5, 10829 Berlin'
                      },
                      'right_person_phone': {
                          'color': [0, 0, 0],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 100,
                          'y': 85,
                          'txt': 'T + 49 30 120866281'
                      }
                  },
                  'image': {
                      'contact': {
                          'x': 25,
                          'y': 100,
                          'w': 178,
                          'path': "img/contact.jpg"
                      }
                  },
                  'cell': {
                      'left_person_mail': {
                          'color': [0, 176, 240],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 25,
                          'y': 90,
                          'w': 20,
                          'txt': 'stephanie.kuehn@capitalbay.de',
                          'align': 'left',
                          'link': 'mailto:stephanie.kuehn@capitalbay.de'
                      },
                      'right_person_mail': {
                          'color': [0, 176, 240],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 100,
                          'y': 90,
                          'w': 20,
                          'txt': 'daniel.ziv@capitalbay.de',
                          'align': 'left',
                          'link': 'mailto:daniel.ziv@capitalbay.de'
                      }
                  },
                  'multi_cell': {
                      'bottom_text_left': {
                          'color': [191, 191, 191],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 25,
                          'y': 230,
                          'w': 90,
                          'h': 4,
                          'txt': "This study has been prepared by Capital Bay Group\nS.A. (hereinafter Capital Bay) to provide investors and\nbusiness partners of Capital Bay with an overview of\ncurrent developments in the care and assisted living\nsector of the real estate industry. Capital Bay\nemphasizes that this study is not a sufficient basis for\ndecision making and user discretion is necessary for\nthe decision making process.\n\nThis study has been prepared with reasonable care.\nThe information presented has not been verified by\nCapital Bay for completeness or accuracy.\nIt has beenobtained from the sources indicated and\nsupplemented by Capital Bay's own market\nknowledge. No confidential or non-public information\nhas been made use.",
                          'align': 'left'
                      },
                      'bottom_text_right': {
                          'color': [191, 191, 191],
                          'font': 'segoeui',
                          'size': 9,
                          'x': 110,
                          'y': 230,
                          'w': 90,
                          'h': 4,
                          'txt': "Capital Bay is not responsible for any incomplete or\ninaccurate information and readers are urged to verify\nthe information themselves before making any\ndecision. Capital Bay shall not be liable for any\nomissions or inaccuracies in this report or for any\nother oral or written statements made in connection\nwith this report.\n\n© 2023 Capital Bay Group\nAll rights reserved.",
                          'align': 'left'
                      }
                  }
              }
          }
      }
      
      for page in competitor_pages:
          market_study_data['pages'][page] = competitor_pages[page]
          market_study_pages.append(page)
          max_pages += 1
      
      max_pages += 4
      market_study_pages.append('good_to_know')
      market_study_pages.append('regulations')
      market_study_pages.append('methodic')
      market_study_pages.append('contact')
      market_study_data['number_of_pages'] = max_pages
      market_study_data['pages']['good_to_know']['page_number'] = max_pages - 3
      market_study_data['pages']['regulations']['page_number'] = max_pages - 2
      market_study_data['pages']['methodic']['page_number'] = max_pages - 1
      market_study_data['pages']['contact']['page_number'] = max_pages
      
      good_to_know_median = anvil.server.call(
          'get_multiple_median',
          {
              'beds': list_beds,
              'years_of_construction_nh': list_years_of_construction_nh,
              'years_of_construction_al': list_years_of_construction_al
          }
      )
      market_study_data['pages']['good_to_know']['cell']['median_beds_value']['txt'] = str(good_to_know_median['beds'])
      market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_value']['txt'] = str(good_to_know_median['years_of_construction_nh'])
      market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_al_value']['txt'] = str(good_to_know_median['years_of_construction_al'])
      
      # Create Map Request for Competitor Map
      competitor_map_request_data = self.build_competitor_map_request(
          coords_nh,
          Variables.home_address_nh,
          coords_al,
          [],
          'nursing_home'
      )
      competitor_map_request_data = self.build_competitor_map_request(
          competitor_map_request_data['controlling_marker'],
          Variables.home_address_al,
          competitor_map_request_data['working_marker'],
          competitor_map_request_data['request'],
          'assisted_living'
      )
      competitor_map_request = self.build_home_marker_map_request(
          competitor_map_request_data['controlling_marker']['marker_coords']['lng'],
          competitor_map_request_data['controlling_marker']['marker_coords']['lat'],
          competitor_map_request_data['request']
      )
      
      chart_data = {
          'operator': {
              'nursing_home_data': [none_profit_operator_nh, public_operator_nh, private_operator_nh],
              'assisted_living_data': [none_profit_operator_al, public_operator_al, private_operator_al]
          },
          'invest_cost_overall': invest_plot_data,
          'purchasing_power': purchase_power,
          'invest_cost_public': {
              'data': invest_costs_public,
              'home': invest_costs_public_home
          },
          'invest_cost_non_profit': {
              'data': invest_costs_non_profit,
              'home': invest_costs_non_profit_home
          },
          'invest_cost_private': {
              'data': invest_costs_private,
              'home': invest_costs_private_home
          },
      }
      
      # Generate Market Study PDF
      anvil.server.call(
          'generate_market_study_pdf',
          market_study_data,  # Dictionary of Data to fill Market Study PDF
          bounding_box,  # Bounding Box of the Map
          Variables.unique_code,  # Unique creation Code for current Market Study
          market_study_pages,  # Ordered List of Pages inside Market Study
          competitor_map_request,  # Request Data for Competitor Map
          Variables.activeIso,  # Data of current Iso Layer
          marker_coords,  # Coordinates of Map Marker
          chart_data,  # Data to create all needed charts
      )

      anvil.js.call('update_loading_bar', 100, 'Download Market Study')
      
      # Download Market Study PDF
      market_study = app_tables.pictures.search()[0]
      anvil.media.download(market_study['pic'])
      print(datetime.datetime.now())

      anvil.js.call('update_loading_bar', 0, '')
      Functions.manipulate_loading_overlay(self, False)
  
  def upload_mspdf_change(self, file, **event_args):
    with anvil.server.no_loading_indicator:
      from .Copy_Upload_Link import Copy_Upload_Link
      #This method is called when the Dropdown-Menu has changed
      folder = app_files.market_studies
      file = folder.create_file(f"market_study_{Variables.unique_code}", file)
      alert(Copy_Upload_Link(link = file._obj["alternateLink"]), buttons=[], dismissible=False, large=True, role='custom_alert')
      # anvil.js.call('show_mun_info', f'<h1>Google Drive Share Link for Market Study PDF</h1><br><br><p id="toCopyText">{file._obj["alternateLink"]}</p><br><button type="button" onClick="copy_to_clipboard()">Copy Link</button><br><br><button type="button" onClick="hide_mun_info()">&#10006;</button>')
      self.upload_mspdf.clear()
    
#####  Button Functions   #####
###############################
#####  Dropdown Functions #####

  def distance_dropdown_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
      
      Functions.refresh_icons(self)

  #####  Dropdown Functions #####
  ###############################
  #####  Upload Functions   #####

  #This method is called when a new file is loaded into the FileLoader
  def file_loader_upload_change(self, file, **event_args):  
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(self, True)
      anvil.js.call('update_loading_bar', 5, 'Reading Excel File')
      #Call Server-Function to safe the File  
      self.cluster_data = anvil.server.call('save_local_excel_file', file)
      if self.cluster_data == None:
        Functions.manipulate_loading_overlay(self, False)
        anvil.js.call('update_loading_bar', 100, 'Error while processing Excel File')
        alert('Irgendwas ist schief gelaufen. Bitte Datei neu hochladen!')
        anvil.js.call('update_loading_bar', 0, '')
        self.file_loader_upload.clear()
      else:
        self.cluster_btn.visible = False
        self.invest_class_btn.visible = False
        self.cluster_all.visible = False
        self.i_class_all.visible = False
        self.icon_grid.visible = False
        self.invest_grid.visible = False
        self.change_cluster_color.visible = False
        self.invest_class_btn.raise_event('click')
        self.cluster_btn.raise_event('click')
        for key in Variables.marker.keys():
          for marker in Variables.marker[key]['marker']:
            marker.remove()
        Variables.marker = {}
        self.icon_grid.clear()
        self.invest_grid.clear()
        if self.mobile:
          self.mobile_hide_click()
        anvil.js.call('update_loading_bar', 15, 'Creating Markers and Clusters')
        #Initialise Variables
        excel_markers = {}
        added_clusters = []
        added_invest_classes = []
        invest_components = {}
        cluster_components = {}
        colors = [
          ['white', '#ffffff', '/_/theme/Pins/CB_MapPin_white.png'],
          ['blue', '#234ce2', '/_/theme/Pins/CB_MapPin_blue.png'],
          ['green', '#438e39', '/_/theme/Pins/CB_MapPin_green.png'],
          ['grey', '#b3b3b3', '/_/theme/Pins/CB_MapPin_grey.png'],
          ['lightblue', '#2fb2e0', '/_/theme/Pins/CB_MapPin_lightblue.png'],
          ['orange', '#fc9500', '/_/theme/Pins/CB_MapPin_orange.png'],
          ['pink', '#e254b7', '/_/theme/Pins/CB_MapPin_pink.png'],
          ['red', '#d32f2f', '/_/theme/Pins/CB_MapPin_red.png'],
          ['yellow', '#f4de42', '/_/theme/Pins/CB_MapPin_yellow.png'],
          ['gold', '#ccb666', '/_/theme/Pins/CB_MapPin_gold.png']
        ]
  
        invests = {
          'Super Core': '/_/theme/Pins/CB_MapPin_Sc.png',
          'Core/ Core+': '/_/theme/Pins/CB_MapPin_CC.png',
          'Value Add': '/_/theme/Pins/CB_MapPin_VA.png',
          'Opportunistic': '/_/theme/Pins/CB_MapPin_Opp.png',
          'Development': '/_/theme/Pins/CB_MapPin_Dev.png',
          'Workout': '/_/theme/Pins/CB_MapPin_Wo.png',
          'Unclassified': '/_/theme/Pins/CB_MapPin_gold.png'
        }
    
        #Create Settings
        self.icon_grid.row_spacing = 0
        counter = 0
        
        for asset in self.cluster_data:
    
          # Create HTML Element for Icon
          el = document.createElement('div')
          el.className = f'{asset["address"]}'
          el.style.width = '40px'
          el.style.height = '40px'
          el.style.backgroundSize = '100%'
          el.style.backgroundrepeat = 'no-repeat'
          el.style.zIndex = '250'
  
          # Create HTML Element for Invest Class Icon
          inv_el = document.createElement('div')
          inv_el.className = f'{asset["address"]}_investment'
          inv_el.style.width = '40px'
          inv_el.style.height = '40px'
          inv_el.style.backgroundSize = '100%'
          inv_el.style.backgroundrepeat = 'no-repeat'
          inv_el.style.zIndex = '251'

          cluster_name = asset['cluster']
          if asset['invest_class'] == "Select please":
            invest_name = "Unnamed"
          else:
            invest_name = asset['invest_class']
    
          if cluster_name not in added_clusters:
            counter += 1
            color = colors[counter]
            text = f"{cluster_name[:11]}..." if len(cluster_name) > 11 else cluster_name
            checkbox = CheckBox(checked=True, text=text, spacing_above='none', spacing_below='none', font='Roboto+Flex', font_size=13, role='switch-rounded', tooltip=cluster_name)
            checkbox.add_event_handler('change', self.check_box_marker_icons_change)
            icon = Label(icon='fa:circle', foreground=color[1], spacing_above='none', spacing_below='none', icon_align='top')
            cluster_components[cluster_name] = [checkbox, icon]
            added_clusters.append(cluster_name)
  
          if invest_name not in added_invest_classes:
            text = f"{invest_name[:11]}..." if len(invest_name) > 11 else invest_name
            checkbox = CheckBox(checked=False, text=text, spacing_above='none', spacing_below='none', font='Roboto+Flex', font_size=13, role='switch-rounded', tooltip=invest_name)
            checkbox.add_event_handler('change', self.check_box_marker_icons_change)
            invest_components[invest_name] = checkbox
            added_invest_classes.append(invest_name)
    
          # #Get Coordinates of provided Adress for Marker
          req_str = self.build_request_string(asset)
          req_str += f'.json?access_token={self.token}'
          coords = anvil.http.request(req_str,json=True)
          for entry in coords['features']:
            if asset['zip'] in entry['place_name']:
              coordinates = entry['geometry']['coordinates']
              break
          if not cluster_name in excel_markers.keys():
            excel_markers[cluster_name] = {'color': color, 'static': 'none', 'marker': []}
          el.style.backgroundImage = f'url({self.app_url}{excel_markers[cluster_name]["color"][2]})'
          new_list = self.set_excel_markers(excel_markers[cluster_name]['static'], coordinates, excel_markers[cluster_name]['marker'], el, asset)
          excel_markers[cluster_name]['marker'] = new_list
          if not invest_name in excel_markers.keys():
            excel_markers[invest_name] = {'pin': invests[invest_name], 'static': 'none', 'marker': []}
          inv_el.style.backgroundImage = f"url({self.app_url}{invests[invest_name]})"
          new_list = self.set_excel_markers(excel_markers[invest_name]['static'], coordinates, excel_markers[invest_name]['marker'], inv_el, asset)
          excel_markers[invest_name]['marker'] = new_list

        anvil.js.call('update_loading_bar', 60, 'Adding Menu Items')
        
        for key in sorted(cluster_components):
          self.icon_grid.add_component(cluster_components[key][0], row=key, col_xs=1, width_xs=8)
          self.icon_grid.add_component(cluster_components[key][1], row=key, col_xs=9, width_xs=1)
          
          sorted_keys = ['Super Core', 'Core/ Core+', 'Value Add', 'Opportunistic', 'Development', 'Workout', 'Unclassified']
        for key in sorted(invest_components.keys(), key=lambda x: sorted_keys.index(x)):
          self.invest_grid.add_component(invest_components[key], row=key, col_xs=1, width_xs=8)
          
        # Add Marker-Arrays to global Variable Marker
        Variables.marker.update(excel_markers)

        anvil.js.call('update_loading_bar', 80, 'Waiting for individual Cluster Colors')
        self.change_cluster_color_click()
        anvil.js.call('remove_span')

        anvil.js.call('update_loading_bar', 95, 'Loading created Markers')
        for checkbox in self.invest_grid.get_components():
          checkbox.raise_event('change')
  
        self.cluster_btn.visible = True
        self.invest_class_btn.visible = True
        self.cluster_all.visible = True
        self.i_class_all.visible = True
        self.icon_grid.visible = True
        self.invest_grid.visible = True
        self.change_cluster_color.visible = True
        self.invest_class_btn.raise_event('click')
        self.cluster_btn.raise_event('click')

        anvil.js.call('update_loading_bar', 100, 'Finishing Process')
        self.file_loader_upload.clear()
        Functions.manipulate_loading_overlay(self, False)
        anvil.js.call('update_loading_bar', 0, '')

  # This Function is called when a DB Update should be done
  def db_upload_change(self, file, **event_args):
    splitted_file_name = file.name.split(' ')
    if 'Betreutes' in splitted_file_name:
      anvil.server.call('write_caredb_bw', file)
    elif 'Pflegeheime' in splitted_file_name:
      anvil.server.call('write_caredb_care', file)
    else:
      print('Uploaded incorrect File')
    self.db_upload.clear()

  #####  Upload Functions   #####
  ###############################
  #####   Extra Functions   #####
  
  #This method is called when the Geocoder was used 
  def move_marker(self, result):
    with anvil.server.no_loading_indicator:
      #Set iso-Layer for new coordinates
      lnglat = result['result']['geometry']['coordinates']
      self.marker.setLngLat(lnglat)
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
      
      Functions.refresh_icons(self)
  
  #This method is called when the draggable Marker was moved
  def marker_dragged(self, drag):
    with anvil.server.no_loading_indicator:
      #Set iso-Layer for new Markerposition
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
      
      Functions.refresh_icons(self)
    
  #This method is called when the draggable Marker was moved or when the Geocoder was used
  def get_iso(self, profile, contours_minutes):
    with anvil.server.no_loading_indicator:
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
    with anvil.server.no_loading_indicator:
      #Check which Layer is active
      if click.features[0].layer.source == 'federal_states':
        
        #Create Popup and add it to the Map
        bl_name = click.features[0].properties.name
        bl_id = click.features[0].id
        clicked_lngLat = dict(click.lngLat)
        popup = mapboxgl.Popup({'className': 'markerPopup'}).setLngLat(clicked_lngLat).setHTML(f"<p class='popup_distance'><b>Bundesland:</b> {bl_name}</p>").addTo(self.mapbox)
      
      #Check which Layer is active
      elif click.features[0].layer.source == 'administrative_districts':
        
        #Create Popup and add it to the Map
        bl_name = click.features[0].properties.NAME_1
        rb_name = click.features[0].properties.NAME_2
        clicked_lngLat = dict(click.lngLat)
        popup = mapboxgl.Popup({'className': 'markerPopup'}).setLngLat(clicked_lngLat).setHTML(f"<p class='popup_distance'><b>Bundesland:</b> {bl_name}</p><p class='popup_distance'><b>Regierungsbezirk:</b> {rb_name}</p>").addTo(self.mapbox)
      
      #Check which Layer is active
      elif click.features[0].layer.source == 'counties':
        
        #Create Popup and add it to the Map
        bl_name = click.features[0].properties.lan_name
        lk_name = click.features[0].properties.krs_name
        clicked_lngLat = dict(click.lngLat)
        popup = mapboxgl.Popup({'className': 'markerPopup'}).setLngLat(clicked_lngLat).setHTML(f"<p class='popup_distance'><b>Bundesland:</b> {bl_name}</p><p class='popup_distance'><b>Landkreis:</b> {lk_name}</p>").addTo(self.mapbox)
    
      elif click.features[0].layer.source == 'municipalities':
        
        if hasattr(click.features[0].properties, 'GEN'):
          
          gm_name = click.features[0].properties.GEN
          
        else:
          
          gm_name = click.features[0].properties.name
        
        key = click.features[0].properties.AGS
        demographic, exact_demographic = anvil.server.call('get_data_from_database', key)
      
        popup_text = f'<button type="button" onClick="hide_mun_info()">&#10006;</button><br><br><h3>Municipality: {gm_name}</h3><b>ID:</b> {key}<br><b>Area:</b> {"{:.2f}".format(float(demographic["flaeche"]))}km&sup2;<br><br><b>Population:</b> {demographic["bevoelkerung_ges"]}<br><b>per km&sup2:</b> {demographic["bevoelkerung_jekm2"]}<br><br><table><tr><th class="firstCol">Gender</th><th>Overall</th><th>Under 3</th><th>3 to <br>Under 6</th><th>6 to <br>Under 10</th><th>10 to Under 15</th><th>15 to Under 18</th><th>18 to Under 20</th><th>20 to Under 25</th><th>25 to Under 30</th><th>30 to Under 35</th><th>35 to Under 40</th><th>40 to Under 45</th><th>45 to Under 50</th><th>50 to Under 55</th><th>55 to Under 60</th><th>60 to Under 65</th><th>65 to Under 75</th><th>75 and older</th></tr><tr><th class="firstCol">Overall</th><td>100%</td><td>{"{:.1f}".format(float(exact_demographic["all_u3"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_3tou6"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_6tou10"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_10tou15"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_15tou18"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_18tou20"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_20tou25"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_25tou30"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_30tou35"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_35tou40"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_40tou45"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_45tou50"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_50tou55"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_55tou60"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_60tou65"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_65tou75"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["all_75"]))}%</td></tr><tr><th class="firstCol">Male</th><td>{"{:.1f}".format(float(exact_demographic["man_compl"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_u3"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_3tou6"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_6tou10"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_10tou15"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_15tou18"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_18tou20"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_20tou25"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_25tou30"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_30tou35"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_35tou40"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_40tou45"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_45tou50"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_50tou55"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_55tou60"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_60tou65"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_65tou75"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["man_75"]))}%</td></tr><tr><th class="firstCol">Female</th><td>{"{:.1f}".format(float(exact_demographic["woman_compl"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_u3"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_3tou6"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_6tou10"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_10tou15"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_15tou18"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_18tou20"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_20tou25"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_25tou30"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_30tou35"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_35tou40"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_40tou45"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_45tou50"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_50tou55"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_55tou60"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_60tou65"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_65tou75"]))}%</td><td>{"{:.1f}".format(float(exact_demographic["woman_75"]))}%</td></tr></table><br><br><br><b>Grad der Verstädterung:</b> {demographic["verstaedterung_bez"]}'

        from .Municipality_Info import Municipality_Info
        alert(Municipality_Info(data={'demographic': demographic, 'exact_demographic': exact_demographic, 'gm_name': gm_name, 'key': key, }), large=True, role='custom_alert_big')
        
      #Check which Layer is active
      elif click.features[0].layer.source == 'bezirke':
        
        #Create Popup and add it to the Map
        dt_name = click.features[0].properties.name
        dt_id = click.features[0].id
        clicked_lngLat = dict(click.lngLat)
        popup = mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bezirk:</b> {dt_name}').addTo(self.mapbox)

  #This method is called when the User clicked on a Point of Interest on the Map   #Eventuell nicht mehr benötigt
  def poi(self, click):
    with anvil.server.no_loading_indicator:
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
  def place_layer(self):
    with anvil.server.no_loading_indicator:
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
                'line_width': .25}, 
                {'id_fill': 'administrative_districts',
                'id_outline': 'outline_administrative_districts', 
                'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/3_regierungsbezirke/1_sehr_hoch.geo.json',
                'line_width': .25},
              {'id_fill': 'counties',
                'id_outline': 'outline_counties', 
                'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/landkreise.geojson',
                'line_width': .25},
              {'id_fill': 'municipalities',
                'id_outline': 'outline_municipalities', 
                'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/municipalities.geojson',
                'line_width': .25},
              {'id_fill': 'districts',
                'id_outline': 'outline_districts', 
                'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/bln_hh_mun_dist.geojson',
                'line_width': .25},
              {'id_fill': 'netherlands',
                'id_outline': 'outline_netherlands', 
                'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/netherlands.geojson',
                'line_width': .25}]
      
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
            'fill-color': '#3f6085',
            'fill-opacity': [
              'case',
              ['boolean', ['feature-state', 'hover'], False],
              0.3,
              0
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
              'line-color': '#1b2939',
              'line-width': entry['line_width']
            }
        })

      if not Variables.activeLayer == None:
        self.mapbox.setLayoutProperty(Variables.activeLayer, 'visibility', 'visible')
        self.mapbox.setLayoutProperty(f'outline_{Variables.activeLayer}', 'visibility', 'visible')
  
  #This method is called from the check_box_change-Functions to place Icons on Map  
  def create_icons(self, check_box, last_bbox, category, picture):
    with anvil.server.no_loading_indicator:
      # Check if Checkbox is checked
      if check_box == True:

        marker_coords = [self.marker['_lngLat']['lng'], self.marker['_lngLat']['lat']]
        
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
      
            Functions.create_marker(self, check_box, last_bbox, category, picture, bbox, marker_coords, mapboxgl)
      
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

          forbidden_categories = ["nursing_homes", "assisted_living"]
          icons = Variables.icons[f'{category}']
          if not category in forbidden_categories:
            if self.max_marker.text < len(Variables.icons[f'{category}']):
              icons = Variables.icons[f'{category}'][:self.max_marker.text]
          
          # Loop through every Element in global Icon-Elements
          for el in icons:
          
            # Add Element to Map
            el.addTo(self.mapbox)
    
          # Change last Category
          Variables.last_cat = f'{category}'
      
      # Do if Checkbox is unchecked
      else:

        if category == "subway":
          for id in self.opnv_layer:
            self.mapbox.setLayoutProperty(id, 'visibility', 'none')
      
        # Loop through every Element in global Icon-Elements
        for el in Variables.icons[f'{category}']:
          
          # Remove Element from Map
          el.remove()
      
      # Send Value back to origin Function
      return (last_bbox)
      
  #This method is called from the file uploader to set Markers based on Excel-Data
  def set_excel_markers(self, marker_cat, coords, marker_list, el, asset):
    with anvil.server.no_loading_indicator:
      if asset['acqisition_date'] == 'Unclassified':
        date = 'N/A'
      else:
        date = asset['acqisition_date']
      popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
        f"<p class='popup_type'><b>{asset['address']}</b></p>"
        f"<p class='popup_type'>{asset['zip']} {asset['city']}<p>"
        f"<p class='popup_type'>{asset['federal_state']}</p>"
        f"<p class='popup_type'>Cluster: {asset['cluster']}<p>"
        f"<p class='popup_type'>Invest Class: {asset['invest_class']}<p>"
        f"<p class='popup_type'>Acqisition Date: {date}<p>"
      )
      marker_cat = mapboxgl.Marker({'draggable': False, 'element': el, 'anchor': 'bottom'}).setPopup(popup)
      marker_el = marker_cat.getElement()

      anvil.js.call('addHoverEffect', marker_el, popup, self.mapbox, marker_cat, asset, asset['cluster'], "Hahahahahahahahahahahahahahahaha", self.mobile)
      
      # Add Marker to the Map
      newmarker = marker_cat.setLngLat(coords).addTo(self.mapbox)
  
      # Add Marker Marker-Array
      marker_list.append(newmarker)
      return(marker_list)
    
  #This method is called when the Mouse is moved inside or out of an active Layer
  def change_hover_state(self, mouse):
    with anvil.server.no_loading_indicator:
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
    with anvil.server.no_loading_indicator:
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

  def build_competitor_map_request(self, working_marker, home_marker, controlling_marker, request, type):
    request_static_map_raw = f"%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B"
    request_static_map = request_static_map_raw
    marker_number = 0
    last_coord_dist = 0

    for working_marker_index, working_marker_coordinate in enumerate(working_marker['sorted_coords']):
      if working_marker_coordinate in home_marker:
        working_marker['sorted_coords'][working_marker_index].append('home')
      elif not last_coord_dist == working_marker_coordinate[1]:
        marker_number += 1
        if type == 'nursing_home':
          icon = f'{marker_number}Nursing@0.6x.png'
        else:
          icon = f'{marker_number}@0.6x.png'
        if not working_marker_coordinate[2]:
            for controlling_maker_index, controlling_maker_coordinate in enumerate(controlling_marker['sorted_coords']):
              if abs(controlling_maker_coordinate[1] - working_marker_coordinate[1]) <= .015:
                distance = anvil.server.call(
                  'get_point_distance',
                  [float(working_marker_coordinate[0]['coords'][0]), float(working_marker_coordinate[0]['coords'][1])],
                  [float(controlling_maker_coordinate[0]['coords'][0]), float(controlling_maker_coordinate[0]['coords'][1])]
                )
                if distance <= .01:
                  if type == 'nursing_home':
                    icon = f'Nursing{marker_number}@0.6x.png'
                  else:
                    icon = f'Assisted{marker_number}@0.6x.png'
                  controlling_marker['sorted_coords'][controlling_maker_index].append(True)
                  working_marker['sorted_coords'][working_marker_index].append(True)
                  break
        else:
          if type == 'nursing_home':
            icon = f'Nursing{marker_number}@0.6x.png'
          else:
            icon = f'Assisted{marker_number}@0.6x.png'
        url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/{icon}'
        encoded_url = url.replace("/", "%2F")
        if not (working_marker_index + 1) % 20 == 1 and not request_static_map[-1] == "B":
          request_static_map += f"%2C"
        request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{working_marker_coordinate[0]['coords'][0]},{working_marker_coordinate[0]['coords'][1]}%5D%7D%7D"
        if working_marker_index == len(working_marker['sorted_coords']) - 1 or (working_marker_index + 1) % 20 == 0:
          request_static_map += "%5D%7D"
          request.append(request_static_map)
          request_static_map = request_static_map_raw
      last_coord_dist = working_marker_coordinate[1]

    return {'request': request, 'working_marker': working_marker, 'controlling_marker': controlling_marker}

  def build_home_marker_map_request(self, longitude, latitude, request):
    request_static_map = f"%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B"
    url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/PinCBx075.png'
    encoded_url = url.replace("/", "%2F")
    request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{longitude},{latitude}%5D%7D%7D%5D%7D"
    request.append(request_static_map)
    return request
  
  def change_icons(self, checkbox):
    with anvil.server.no_loading_indicator:
      if checkbox == "Veterinary" and self.check_box_vet.checked == True:
        Variables.last_bbox_vet = self.create_icons(False, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
        Variables.last_bbox_vet = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
      elif checkbox == "Social facility" and self.check_box_soc.checked == True:
        Variables.last_bbox_soc = self.create_icons(False, Variables.last_bbox_soc, "social_facility", Variables.icon_social)  
        Variables.last_bbox_soc = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
      elif checkbox == "Pharmacy" and self.check_box_pha.checked == True:
        Variables.last_bbox_pha = self.create_icons(False, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
        Variables.last_bbox_pha = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
      elif checkbox == "Hospital" and self.check_box_hos.checked == True:
        Variables.last_bbox_hos = self.create_icons(False, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
        Variables.last_bbox_hos = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
      elif checkbox == "Clinic" and self.check_box_cli.checked == True:
        Variables.last_bbox_cli = self.create_icons(False, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
        Variables.last_bbox_cli = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
      elif checkbox == "Dentist" and self.check_box_den.checked == True:
        Variables.last_bbox_den = self.create_icons(False, Variables.last_bbox_den, "dentist", Variables.icon_dentist) 
        Variables.last_bbox_den = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
      elif checkbox == "Doctors" and self.check_box_doc.checked == True:
        Variables.last_bbox_doc = self.create_icons(False, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)
        Variables.last_bbox_doc = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)
      elif checkbox == "Nursing School" and self.check_box_nsc.checked == True:
        Variables.last_bbox_nsc = self.create_icons(False, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools)
        Variables.last_bbox_nsc = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools)    
      elif checkbox == "Supermarket" and self.check_box_sma.checked == True:
        Variables.last_bbox_sma = self.create_icons(False, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
        Variables.last_bbox_sma = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
      elif checkbox == "Restaurant" and self.check_box_res.checked == True:
        Variables.last_bbox_res = self.create_icons(False, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant) 
        Variables.last_bbox_res = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
      elif checkbox == "Cafe" and self.check_box_cafe.checked == True:
        Variables.last_bbox_caf = self.create_icons(False, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
        Variables.last_bbox_caf = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
      elif checkbox == "University" and self.check_box_uni.checked == True:
        Variables.last_bbox_uni = self.create_icons(False, Variables.last_bbox_uni, "university", Variables.icon_university) 
        Variables.last_bbox_uni = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
      elif checkbox == "Bus Stop" and self.check_box_bus.checked == True:
        Variables.last_bbox_bus = self.create_icons(False, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)
        Variables.last_bbox_bus = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
      elif checkbox == "Tram Stop" and self.check_box_tra.checked == True:
        Variables.last_bbox_tra = self.create_icons(False, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
        Variables.last_bbox_tra = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
      elif checkbox == "Nursing Home" and self.pdb_data_cb.checked == True:
        Variables.last_bbox_nh = self.create_icons(False, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
        Variables.last_bbox_nh = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
      elif checkbox == "Assisted Living" and self.pdb_data_al.checked == True:
        Variables.last_bbox_al = self.create_icons(False, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
        Variables.last_bbox_al = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)

  def select_all_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      if event_args['sender'].tag.categorie == 'Healthcare':
        for component in self.poi_categories_healthcare_container.get_components():
          if not component == event_args['sender']:
            component.checked = event_args['sender'].checked
            component.raise_event('change')
      elif event_args['sender'].tag.categorie == 'Student Living':
        for component in self.education_grid.get_components():
          if not component == event_args['sender']:
            component.checked = event_args['sender'].checked
            component.raise_event('change')
      elif event_args['sender'].tag.categorie == 'Food & Drinks':
        for component in self.food_drinks_grid.get_components():
          if not component == event_args['sender']:
            component.checked = event_args['sender'].checked
            component.raise_event('change')
      elif event_args['sender'].tag.categorie == 'ÖPNV':
        for component in self.opnv_container.get_components():
          if not component == event_args['sender']:
            component.checked = event_args['sender'].checked
            component.raise_event('change')
      pass

  def iso_layer_active_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      if event_args['sender'].checked:
        self.mapbox.setLayoutProperty('isoLayer', 'visibility', 'visible')
      else:
        self.mapbox.setLayoutProperty('isoLayer', 'visibility', 'none')
      pass

  def hide_ms_marker_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      """This method is called when this checkbox is checked or unchecked"""
      if event_args['sender'].checked:
        self.marker.addTo(self.mapbox)
      else:
        self.marker.remove()
      pass

  def change_cluster_color_click(self, **event_args):
    """This method is called when the button is clicked"""
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(self, True)
      from .Change_Cluster_Color import Change_Cluster_Color
      Functions.manipulate_loading_overlay(self, False)
      response = alert(content=Change_Cluster_Color(components=self.icon_grid.get_components(), mobile=self.mobile), dismissible=False, large=True, buttons=[], role='custom_alert')
      Functions.manipulate_loading_overlay(self, True)
      for key in Variables.marker:
        if key in response:
          Variables.marker[key]['color'] = response[key]
          for marker in Variables.marker[key]['marker']:
            anvil.js.call('changeBackground', marker['_element'], Variables.marker[key]["color"][2])
      for component in self.icon_grid.get_components():
        if type(component) == CheckBox:
          key = component.tooltip
        elif type(component) == Label:
          component.foreground = Variables.marker[key]["color"][1]
      if len(event_args.keys()) > 0:
        Functions.manipulate_loading_overlay(self, False)
      pass
  
  def create_cluster_marker(self, cluster_data):
    with anvil.server.no_loading_indicator:
      ##### UMSCHREIBEN #####
      
      #Initialise Variables
      excel_markers = {}
      added_clusters = []
      added_invest_classes = []
      colors = [
          ['white', '#ffffff', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_white.png'],
          ['blue', '#234ce2', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_blue.png'],
          ['green', '#438e39', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_green.png'],
          ['grey', '#b3b3b3', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_grey.png'],
          ['lightblue', '#2fb2e0', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_lightblue.png'],
          ['orange', '#fc9500', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_orange.png'],
          ['pink', '#e254b7', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_pink.png'],
          ['red', '#d32f2f', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_red.png'],
          ['yellow', '#f4de42', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_yellow.png'],
          ['gold', '#ccb666', 'https://zetghzb6w4un4lyk.anvil.app/debug/T5E7J2EZIGF6AR3RZYZ7UHVIF5XNZWTG%3DZ3JSVNM5PITXRDNWBYDJB25T/_/theme/Pins/CB_MapPin_gold.png']
        ]

      invests = {
          'Super Core': '/_/theme/Pins/CB_MapPin_Sc.png',
          'Core/ Core+': '/_/theme/Pins/CB_MapPin_CC.png',
          'Value Add': '/_/theme/Pins/CB_MapPin_VA.png',
          'Opportunistic': '/_/theme/Pins/CB_MapPin_Opp.png',
          'Development': '/_/theme/Pins/CB_MapPin_Dev.png',
          'Workout': '/_/theme/Pins/CB_MapPin_Wo.png',
          'Unclassified': '/_/theme/Pins/CB_MapPin_gold.png'
        }
  
      #Create Settings
      self.icon_grid.row_spacing = 0
      counter = 0
      
      for asset in cluster_data['data']:
  
        # Create HTML Element for Icon
        el = document.createElement('div')
        el.className = f'{asset["address"]}'
        el.style.width = '40px'
        el.style.height = '40px'
        el.style.backgroundSize = '100%'
        el.style.backgroundrepeat = 'no-repeat'
        el.style.zIndex = '251'

        # Create HTML Element for Invest Class Icon
        inv_el = document.createElement('div')
        inv_el.className = f'{asset["address"]}_investment'
        inv_el.style.width = '40px'
        inv_el.style.height = '40px'
        inv_el.style.backgroundSize = '100%'
        inv_el.style.backgroundrepeat = 'no-repeat'
        inv_el.style.zIndex = '252'
        
        cluster_name = asset['cluster']
        invest_name = asset['invest_class']
  
        color = cluster_data['settings'][cluster_name]['color']
        if cluster_name not in added_clusters:
          text = f"{cluster_name[:11]}..." if len(cluster_name) > 11 else cluster_name
          checkbox = CheckBox(checked=True, text=text, spacing_above='none', spacing_below='none', font='Roboto+Flex', font_size=13, role='switch-rounded', tooltip=cluster_name)
          checkbox.add_event_handler('change', self.check_box_marker_icons_change)
          icon = Label(icon='fa:circle', foreground=color[1], spacing_above='none', spacing_below='none')
          self.icon_grid.add_component(checkbox, row=cluster_name, col_xs=1, width_xs=8)
          self.icon_grid.add_component(icon, row=cluster_name, col_xs=9, width_xs=1)
          added_clusters.append(cluster_name)

        if invest_name not in added_invest_classes:
          text = f"{invest_name[:11]}..." if len(invest_name) > 11 else invest_name
          checkbox = CheckBox(checked=False, text=text, spacing_above='none', spacing_below='none', font='Roboto+Flex', font_size=13, role='switch-rounded', tooltip=invest_name)
          checkbox.add_event_handler('change', self.check_box_marker_icons_change)
          self.invest_grid.add_component(checkbox, row=invest_name, col_xs=1, width_xs=12)
          added_invest_classes.append(invest_name)
  
        # #Get Coordinates of provided Adress for Marker
        req_str = self.build_request_string(asset)
        req_str += f'.json?access_token={self.token}'
        coords = anvil.http.request(req_str,json=True)
        for entry in coords['features']:
          if asset['zip'] in entry['place_name']:
            coordinates = entry['geometry']['coordinates']
            break

        if 'marker' not in cluster_data['settings'][cluster_name].keys():
          cluster_data['settings'][cluster_name]['marker'] = []
        el.style.backgroundImage = f'url({color[2]})'
        new_list = self.set_excel_markers(cluster_data['settings'][cluster_name]['static'], coordinates, cluster_data['settings'][cluster_name]['marker'], el, asset)
        cluster_data['settings'][cluster_name]['marker'] = new_list
        if 'marker' not in cluster_data['settings'][invest_name].keys():
          cluster_data['settings'][invest_name]['marker'] = []
        inv_el.style.backgroundImage = f"url({self.app_url}{invests[invest_name]})"
        new_list = self.set_excel_markers(cluster_data['settings'][invest_name]['static'], coordinates, cluster_data['settings'][invest_name]['marker'], inv_el, asset)
        cluster_data['settings'][invest_name]['marker'] = new_list
        
        # Create Popup for Marker and add it to the Map
        # popup = mapboxgl.Popup({'closeOnClick': False, 'offset': 25})
        # popup.setHTML(data[0][markercount]['Informationen'])
        # popup_static = mapboxgl.Popup({'closeOnClick': False, 'offset': 5, 'className': 'static-popup', 'closeButton': False, 'anchor': 'top'}).setText(data[0][markercount]['Informationen']).setLngLat(coords['features'][0]['geometry']['coordinates'])
        # popup_static.addTo(self.mapbox)
        
        #Increase Markercount
        # markercount += 1
        
      # Add Marker-Arrays to global Variable Marker
      Variables.marker.update(cluster_data['settings'])
  
      anvil.js.call('remove_span')
      
      self.cluster_btn.visible = True
      self.invest_class_btn.visible = True
      self.cluster_all.visible = True
      self.i_class_all.visible = True
      self.invest_class_btn.raise_event('click')
      self.cluster_btn.raise_event('click')
      self.button_icons.raise_event('click')
  
  def mobile_hide_click(self, **event_args):
    with anvil.server.no_loading_indicator:
      if self.mobile:
        mobile_menu = document.getElementsByClassName('left-nav')[0]
        if self.mobile_menu_open:
          mobile_menu.style.overflowY = 'hidden'
          mobile_menu.style.height = '7%'
          mobile_menu.scrollTop = 0
          self.mobile_menu_open = False
        else:
          mobile_menu.style.height = '100%'
          mobile_menu.style.overflowY = 'auto'
          self.mobile_menu_open = True

  def share_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.create_share_map('click')

  def create_share_map(self, mode):
    """This method is called when the button is clicked"""
    with anvil.server.no_loading_indicator:
      # if mode == 'click':
        # Functions.manipulate_loading_overlay(self, True)
      searched_address = anvil.js.call('getSearchedAddress')
      date = datetime.datetime.now()
      str_date = str(date).split('.')
      searched_address = searched_address + str_date[0]
      changed_address = searched_address.replace(' ', '_').replace(',', '').replace('Deutschland', '').replace(':', '-')
      poi_healthcare = ""
      poi_education = ""
      poi_food_drinks = ""
      poi_opnv = ""
      overlay = ""
      for category in self.poi_categories_healthcare_container.get_components():
        if category.checked:
          poi_healthcare += '1'
        else:
          poi_healthcare += '0'
      for category in self.education_grid.get_components():
        if category.checked:
          poi_education += '1'
        else:
          poi_education += '0'
      for category in self.food_drinks_grid.get_components():
        if category.checked:
          poi_food_drinks += '1'
        else:
          poi_food_drinks += '0'
      for category in self.opnv_container.get_components():
        if category.checked:
          poi_opnv += '1'
        else:
          poi_opnv += '0'
      for component in self.layer_categories.get_components():
        if component.checked:
          overlay = component.text
          break
      for component in self.style_grid.get_components():
        if component.checked:
          map_style = component.text
          break
      if self.cluster_all.checked:
        cluster_selects = '1'
      else :
        cluster_selects = '0'
      for component in self.icon_grid.get_components():
        if type(component) is not Label:
          if component.checked:
            cluster_selects += '1'
          else:
            cluster_selects += '0'
      if self.i_class_all.checked:
        iclass_selects = '1'
      else:
        iclass_selects = '0'
      for component in self.invest_grid.get_components():
        if type(component) is not Label:
          if component.checked:
            iclass_selects += '1'
          else:
            iclass_selects += '0'
      study_pin = self.hide_ms_marker.checked
  
      deleted_marker = {}
      for setting in Variables.marker:
        popped = Variables.marker[setting].pop('marker')
        deleted_marker[setting] = popped
      cluster = {
        'data': self.cluster_data,
        'settings': Variables.marker
      }

      from .Name_Share_Link import Name_Share_Link
      Functions.manipulate_loading_overlay(self, False)
      name = alert(content=Name_Share_Link(searched_address=changed_address), buttons=[], dismissible=False, large=True, role='custom_alert')
      Functions.manipulate_loading_overlay(self, True)
      self.url = anvil.server.call('get_app_url') + f'#?name={name}'
      center = self.mapbox.getCenter()
      
      dataset = {
        'marker_lng': self.marker['_lngLat']['lng'],
        'marker_lat': self.marker['_lngLat']['lat'],
        'cluster': cluster,
        'distance_movement': self.profile_dropdown.selected_value,
        'distance_time': self.time_dropdown.selected_value,
        'overlay': overlay,
        'map_style': map_style,
        'poi_healthcare': poi_healthcare,
        'poi_education': poi_education,
        'poi_food_drinks': poi_food_drinks,
        'poi_opnv': poi_opnv,
        'iso_layer': self.checkbox_poi_x_hfcig.checked,
        'name': name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss"),
        'url': self.url.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss"),
        'study_pin': study_pin,
        'zoom': self.mapbox.getZoom(),
        'center': {'lng': center.lng, 'lat': center.lat},
        'competitors': {'competitors': self.competitors},
        'custom_marker': self.custom_marker,
        'cluster_selects': cluster_selects,
        'iclass_selects': iclass_selects,
        'removed_markers': Variables.removed_markers
      }
  
      anvil.server.call('save_map_settings', dataset)
  
      for setting in deleted_marker:
        Variables.marker[setting]['marker'] = deleted_marker[setting]

      if mode == 'click':
        grid = GridPanel()
        label = TextBox(text=self.url, enabled=False)
        button = Button(text="Copy Link")
        button.add_event_handler('click', self.copy_to_clipboard)
        grid.add_component(label, row="label", col_xs=1, width_xs=10)
        grid.add_component(button, row="button", col_xs=1, width_xs=10)
  
        # Functions.manipulate_loading_overlay(self, False)
        alert(grid, large=True, dismissible=False, role='custom_alert')
      else:
        return self.url.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue").replace("ß", "ss")

  def handle_style_change(self, event):
    self.place_layer()
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

  def map_right_click(self, event):

    if event['type'] == 'contextmenu':

      self.clicked_coords = [event['lngLat']['lng'], event['lngLat']['lat']]

      popup = document.getElementById('mapPopup')
      if popup:
        popup.remove()
    
      screen = anvil.js.call('get_screen_width')
      width = screen[0]
      height = screen[1]
  
      popup = document.createElement('div')
      popup.id = 'mapPopup'
      popup.style.top = f"{event['point']['y']}px"
      popup.style.left = f"{event['point']['x'] + 259}px"

      btn = document.createElement('button')
      btn.id = 'addMarker'
      btn.innerText = 'Create Marker'

      btn.addEventListener('click', self.create_marker)

      popup.appendChild(btn)
  
      body = document.getElementsByTagName('body')
      body[0].appendChild(popup)

    elif event['type'] == 'click':

      popup = document.getElementById('mapPopup')
      if popup:
        popup.remove()
  
  def create_marker(self, event):

    from .Custom_Marker import Custom_Marker
    marker_data = alert(Custom_Marker(url=self.app_url), buttons=[], dismissible=False, large=True, role='custom_alert')
    self.create_custom_marker(marker_data)
    self.custom_marker.append(marker_data)

  def create_custom_marker(self, marker_data):
    # Create HTML Element for Icon
    el = document.createElement('div')
    el.className = 'marker'
    el.id = f'custom_marker'
    if 'Information' in marker_data['icon']:
      el.style.width = '50px'
      el.style.height = '50px'
    else:
      el.style.width = '40px'
      el.style.height = '40px'
    el.style.backgroundSize = '100%'
    el.style.backgroundrepeat = 'no-repeat'
    el.style.zIndex = '220'
    el.style.cursor = 'pointer'
    el.style.backgroundImage = f"url({marker_data['icon']})"
    
    popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
      f"<p class='popup_name'><b>{marker_data['name']}</b></p>"
      f"<p class='popup_type'>{marker_data['text']}</p>"
    )

    if marker_data['address'] is None:
      coords = self.clicked_coords
    else:
      coords = marker_data['address']['geometry']['coordinates']
    newicon = mapboxgl.Marker(el, {'anchor': 'bottom'}).setLngLat(coords).setOffset([0, 0]).addTo(self.mapbox).setPopup(popup)

    popup = document.getElementById('mapPopup')
    if popup:
      popup.remove()

  def copy_to_clipboard(self, **event_args):
    anvil.js.window.navigator.clipboard.writeText(self.url)

  def comp_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(self, True)
      anvil.js.call('update_loading_bar', 5, 'Reading Excel File')
      #Call Server-Function to safe the File  
      marker_coords = [self.marker['_lngLat']['lng'], self.marker['_lngLat']['lat']]
      comps = anvil.server.call('read_comp_file', file, marker_coords)
      if comps == None:
        Functions.manipulate_loading_overlay(self, False)
        anvil.js.call('update_loading_bar', 100, 'Error while processing Excel File')
        alert('Irgendwas ist schief gelaufen. Bitte Datei neu hochladen!')
        anvil.js.call('update_loading_bar', 0, '')
        self.file_loader_upload.clear()
      else:
        for marker in self.comp_marker:
          marker.remove()
        self.comp_marker = []
        Functions.manipulate_loading_overlay(self, False)
        anvil.js.call('update_loading_bar', 50, 'Waiting for Competitor Selection')
        from .Comp_Sort import Comp_Sort
        results = alert(Comp_Sort(data=comps, marker_coords=marker_coords), buttons=[], dismissible=False, large=True, role='custom_alert')
        Functions.manipulate_loading_overlay(self, True)
        anvil.js.call('update_loading_bar', 80, 'Creating Marker')
        self.create_comp_marker(results)
        self.competitors = results
        anvil.js.call('update_loading_bar', 100, 'Finishing Process')
        Functions.manipulate_loading_overlay(self, False)
        self.download_comps.visible = True
        anvil.js.call('update_loading_bar', 0, '')
      self.comp_loader.clear()
    pass

  def create_comp_marker(self, results):
    for index, result in enumerate(results):
        # Create HTML Element for Icon
        el = document.createElement('div')
        el.className = 'marker'
        el.id = f'competitor_marker'
        el.style.width = '40px'
        el.style.height = '40px'
        el.style.backgroundSize = '100%'
        el.style.backgroundrepeat = 'no-repeat'
        el.style.zIndex = '220'
        el.style.cursor = 'pointer'
    
        el.style.backgroundImage = f"url({self.app_url}/_/theme/Pins/Comp{index+1}.png)"

        popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
          f"<p class='popup_name'><b>{result['operator']}</b></p>"
          f"<p class='popup_type'>{result['address']}</p>"
          f"<p class='popup_type'>{result['zip']} {result['city']}, {result['federal_state']}</p>"
          f"<p class='popup_type'>{result['distance']} km</p>"
        )
    
        newicon = mapboxgl.Marker(el, {'anchor': 'bottom'}).setLngLat(result['coords']).setOffset([0, 0]).addTo(self.mapbox).setPopup(popup)
        newiconElement = newicon.getElement()

        details = f"<h1>{result['operator']}</h1>"
        details += f"<p>{result['address']}</p>"
        details += f"<p>{result['zip']} {result['city']}, {result['federal_state']}</p>"
        details += f"<p>{result['distance']} km"
        details += "<div class='partingLine'></div>"
        details += f"<p>360 Operator: {result['360_operator']}</p>"
        details += f"<p>Living Concept: {result['living_concept']}</p>"
        details += f"<a href='https://www.stayurban.de/apartments/'>{result['web']}</a>"
        details += "<div class='partingLine'></div>"
        details += f"<p>Equipment: {result['equiment']}</p>"
        details += f"<p>Note: {result['note']}</p>"
        details += f"<p>Community Spaces: {result['community_spaces']}</p>"
        details += f"<p>Furnishing: {result['furnishing']}</p>"
        details += f"<p>Services: {result['services']}</p>"
        details += "<div class='partingLine'></div>"
        details += f"<p>Apartments: {result['apartments']}</p>"
        details += f"<p>Size Range(m²): {result['size_range_sqm']}</p>"
        details += f"<p>Rent per m² Range(€): {result['rent_range_sqm']}</p>"
        details += f"<p>Rent per month Range(€): {result['rent_range_month']}</p>"
        details += "<div class='partingLine'></div>"
        details += f"<p>Created: {result['created']}</p>"
        details += f"<p>Updated: {result['updated']}</p>"
        if not self.role == 'guest':
          details += "<div class='rmv_container'><button id='remove' class='btn btn-default'>Remove Marker</button></div>"

        anvil.js.call('addHoverEffect', newiconElement, popup, self.mapbox, newicon, result, 'Competitor', details, self.role)
        self.comp_marker.append(newicon)  
  
  def download_comps_click(self, **event_args):
    """This method is called when the button is clicked"""
    from .Competitor_list import Competitor_list
    data = ExcelFrames.comp_data
    keys = ['operator', 'address', 'distance', '360_operator', 'living_concept', 
            'apartments', 'size_range_sqm', 'rent_range_sqm', 'rent_range_month', 'equiment', 'community_spaces', 'furnishing', 'services', 
           'note', 'web', 'created']
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    row = 4
    unique_code = anvil.server.call("get_unique_code")
    for index, competitor in enumerate(self.competitors):
      for col_index, key in enumerate(keys):
        color = '#000000'
        left = 0
        right = 0
        content = f"{competitor[key]}"
        text_wrap = True
        if key == 'distance':
          content = f"{competitor[key]} km"
        elif key == 'size_range_sqm':
          content_data = competitor[key].split('-')
          content = f"{content_data[0]} sqm - {content_data[1]} sqm"
        elif key == 'rent_range_sqm':
          content_data = competitor[key].split('-')
          content = f"{content_data[0]} € - {content_data[1]} €"
        elif key == 'rent_range_month':
          content_data = competitor[key].split('-')
          content = f"{content_data[0]} € - {content_data[1]} €"
        elif key == 'web':
          color = '#0000ff'
          text_wrap = False
        elif key == 'operator':
          left = 1
        elif key == 'created':
          right = 1
        data['data'].append({
          'type': "text",
          'insert': "write",
          'cell': f"{letters[col_index]}{row + index}",
          'content': content,
          'format': {
            'font': "Segoe UI",
            'font_size': 10,
            'color': color,
            'bottom': 1,
            'top': 0,
            'left': left,
            'right': right,
            'text_wrap': text_wrap
          }
        })
    anvil.server.call('create_comp_excel', data, unique_code)
    table = app_tables.pictures.search()
    comp_list = app_tables.pictures.search()[0]
    anvil.media.download(comp_list['pic'])
    pass

  def addHoverEffect(self, icon_element, popup, marker, ele, category, marker_details):
    icon_element.addEventListener('mouseenter', functools.partial(self.add_popup, popup, category, marker_details, icon_element))
    icon_element.addEventListener('mouseleave', functools.partial(self.remove_popup, popup))
    icon_element.addEventListener('click', functools.partial(self.show_details, category, marker_details, icon_element, dict(popup['_lngLat'])))

  def add_popup(self, popup, category, marker_details, icon_element, event):
    if not popup == self.last_popup:
      self.last_popup = popup
      popup.addTo(self.mapbox)
      pop = document.getElementsByClassName('mapboxgl-popup-content')[0]
      pop.addEventListener('mouseenter', functools.partial(self.readd_popup, popup))
      pop.addEventListener('mouseleave', functools.partial(self.remove_popup, popup))
      pop.addEventListener('click', functools.partial(self.show_details, category, marker_details, icon_element, dict(popup['_lngLat'])))

  def readd_popup(self, popup, event):
    if not popup == self.last_popup:
      popup.remove()
      popup.addTo(self.mapbox)
      self.last_popup = popup

  def remove_popup(self, popup, event):
    popup.remove()
    self.last_popup = None

  def show_details(self, category, marker_details, icon_element, marker_coords, event):
    if self.role == 'guest':
      if category == 'nursing_homes' or category == 'assisted_living' or category == 'nursing_school' or category == 'Competitor':
        self.remove_details(marker_details, None)
        self.last_target = marker_details
        self.active_container = icon_element
        content = document.getElementsByClassName('content')[0]
        marker_details_dom = content.getElementsByClassName('marker_details')
        if len(marker_details_dom) < 1:
          details = document.createElement('div')
          icon_element.style.width = "50px"
          icon_element.style.height = "50px"
          icon_element.style.zIndex = "221"
          details.innerHTML = marker_details
          details.className = 'marker_details'
          details.id = 'marker_details'
          content.appendChild(details)
    else:
      self.remove_details(marker_details, None)
      self.last_target = marker_details
      self.active_container = icon_element
      self.prev_called = marker_details
      content = document.getElementsByClassName('content')[0]
      marker_details_dom = content.getElementsByClassName('marker_details')
      if len(marker_details_dom) < 1:
        details = document.createElement('div')
        icon_element.style.width = "50px"
        icon_element.style.height = "50px"
        icon_element.style.zIndex = "221"
        details.innerHTML = marker_details
        details.className = 'marker_details'
        details.id = 'marker_details'
        content.appendChild(details)
        btn = document.getElementById('remove')
        btn.addEventListener('click', functools.partial(self.remove_marker, category, marker_coords))
        
  def remove_details(self, marker_details, event, **event_args):
    if not marker_details == self.last_target and not self.last_target == None and self.prev_called == None:
      self.active_container.style.width = "40px"
      self.active_container.style.height = "40px"
      self.active_container.style.zIndex = "220"
      details = document.getElementById('marker_details')
      content = document.getElementsByClassName('content')[0]
      content.removeChild(details)
      self.last_target = None
    self.prev_called = None

  def remove_marker(self, category, marker_coords, event):
    for index, marker in enumerate(Variables.activeIcons[category]):
      if marker['_lngLat']['lng'] == marker_coords['lng'] and marker['_lngLat']['lat'] == marker_coords['lat']:
        deleted_icon = Variables.activeIcons[category].pop(index)
        if not category in Variables.removed_markers.keys():
          Variables.removed_markers[category] = [dict(marker['_lngLat'])]
        else:
          Variables.removed_markers[category].append(dict(marker['_lngLat']))
        marker.remove()
