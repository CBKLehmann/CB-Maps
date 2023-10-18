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

  #######Noch bearbeiten#######

  def create_market_study(self, **event_args):
    '''Import Functions for creating Market Study'''
    from market_study_classes import Basic_App_Informations

    basic_app_informations = Basic_App_Informations(self)


    '''Execute Code without the standard Anvil Loading Animation'''
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(self, True)
      self.mobile_hide_click()
      anvil.js.call('update_loading_bar', 0, 'Getting map-based Informations')
      
      #nh_checked = self.pdb_data_cb.checked
      #al_checked = self.pdb_data_al.checked
  
      unique_code = anvil.server.call("get_unique_code")
      searched_address = anvil.js.call('getSearchedAddress')
      street = searched_address.split(",")[0]
  
      lng_lat_marker = {
                        "lng": (dict(self.marker['_lngLat'])['lng']),
                        "lat": (dict(self.marker['_lngLat'])['lat'])
                      }
  
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
      iso_time = self.time_dropdown.selected_value
      if iso_time == "-1":
        iso_time = "20"
      movement = self.profile_dropdown.selected_value.lower()
  
      marker_coords = dict(self.marker.getLngLat())

      # #####Get Database Informations#####

      anvil.js.call('update_loading_bar', 10, 'Get Informations from Database')
  
      #Get Information from Database for County of Marker-Position
      countie_data = anvil.server.call("get_demographic_district_data", marker_coords)
      countie = countie_data['ex_dem_lk']['name'].split(',')
  
      #Get Entries from Care-Database based on District
      care_data_district = anvil.server.call("get_care_district_data", countie_data['ex_dem_lk']['key'])

      # #####Calculate Data for Market Study#####

      anvil.js.call('update_loading_bar', 25, 'Calculate Data for Market Study')
  
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

      # #####Calculate Data for Market Study#####

      Functions.manipulate_loading_overlay(self, False)
      anvil.js.call('update_loading_bar', 35, 'Waiting for User Input')
      
      #Get organized Coords for Nursing Homes
      coords_nh = self.organize_ca_data(Variables.nursing_homes_entries, 'nursing_homes', lng_lat_marker)
      
      #Get Data for both Nursing Homes
      data_comp_analysis_nh = self.build_req_string(coords_nh, 'nursing_homes')

      # #####Calculate Data for Market Study#####

      Functions.manipulate_loading_overlay(self, True)
      anvil.js.call('update_loading_bar', 40, 'Calculate Nursing Home Data for Market Study')
      
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

      # #####Calculate Data for Market Study#####

      Functions.manipulate_loading_overlay(self, False)
      anvil.js.call('update_loading_bar', 45, 'Waiting for User Input')
      
      #Get organized Coords for both Assisted Living
      coords_al = self.organize_ca_data(Variables.assisted_living_entries, 'assisted_living', lng_lat_marker)
          
      #Get Data for both Assisted Living
      data_comp_analysis_al = self.build_req_string(coords_al, 'assisted_living') 

      # #####Calculate Data for Market Study#####

      Functions.manipulate_loading_overlay(self, True)
      anvil.js.call('update_loading_bar', 50, 'Calculate Assisted Living Data for Market Study')
      
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
      for care_entry in data_comp_analysis_nh['data']:
        beds_amount = 0
        if not care_entry[0]['anz_vers_pat'] == '-':
          inpatients += int(care_entry[0]['anz_vers_pat'])
        if care_entry[0]['status'] == "aktiv":
          nursing_homes_active += 1
          # if not care_entry[0]['ez'] == "-":
          #   beds_active += int(care_entry[0]['ez'])
          #   beds_amount += int(care_entry[0]['ez'])
          # if not care_entry[0]['dz'] == "-":
          #   beds_active += int(care_entry[0]['dz']) * 2
          #   beds_amount += int(care_entry[0]['dz']) * 2
          if not care_entry[0]['platz_voll_pfl'] == "-":
            beds_active += int(care_entry[0]['platz_voll_pfl'])
            beds_amount = int(care_entry[0]['platz_voll_pfl'])
          beds.append(beds_amount)
        elif care_entry[0]['status'] == "in Planung":
          nursing_homes_planned += 1
          # if not care_entry[0]['ez'] == "-":
          #   beds_planned += int(care_entry[0]['ez'])
          # if not care_entry[0]['dz'] == "-":
          #   beds_planned += int(care_entry[0]['dz']) * 2
          if not care_entry[0]['platz_voll_pfl'] == "-":
            beds_planned += int(care_entry[0]['platz_voll_pfl'])
        elif care_entry[0]['status'] == "im Bau":
          nursing_homes_construct += 1
          # if not care_entry[0]['ez'] == "-":
          #   beds_construct += int(care_entry[0]['ez'])
          # if not care_entry[0]['dz'] == "-":
          #   beds_construct += int(care_entry[0]['dz']) * 2
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
        if not care_entry[0]['baujahr'] == "-":
          year.append(int(care_entry[0]['baujahr']))
        # if not care_entry['pg_3'] == "-":
        #   pg3_cost.append(float(care_entry['pg_3']))
        # if not care_entry['eee'] == "-":
        #   copayment_cost.append(float(care_entry['eee']))
        # if not care_entry['uuv'] == "-":
        #   board_cost.append(float(care_entry['uuv']))
  
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
      # pg3_median_raw = anvil.server.call("get_median", pg3_cost)
      # pg3_median = "{:.2f}".format(pg3_median_raw)
      # copayment_median_raw = anvil.server.call("get_median", copayment_cost)
      # copayment_median = "{:.2f}".format(copayment_median_raw)
      # board_median_raw = anvil.server.call("get_median", board_cost)
      # board_median = "{:.2f}".format(board_median_raw)
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

      purchase_power = anvil.server.call('get_purchasing_power', location={'lat': lng_lat_marker['lat'], 'lng': lng_lat_marker['lng']})

      # #####Create Excel for Market Study#####

      anvil.js.call('update_loading_bar', 60, 'Create Excel for Market Study Part 1')
      
      # Copy and Fill Dataframe for Excel-Cover
      #cover_frame = copy.deepcopy(ExcelFrames.cover_data)
      #cover_frame['data'][1]['content'] = zipcode
      #cover_frame['data'][2]['content'] = city.upper()

      population_trend = "{:.1f}".format(((people_u80_fc_35 + people_o80_fc_35) * 100) / (people_u80 + people_o80) - 100)
      if float(population_trend) < 0:
        population_trend_string = f"{population_trend}%"
      else:
        population_trend_string = f"+{population_trend}%"

      date = datetime.datetime.now()
      if len(str(date.day)) == 1:
        day = f"0{date.day}"
      else:
        day = date.day
      if len(str(date.month)) == 1:
        month = f"0{date.month}"
      else:
        month = date.month
      year = date.year
      if len(str(date.hour)) == 1:
        hour = f"0{date.hour}"
      else:
        hour = date.hour
      if len(str(date.minute)) == 1:
        minute = f"0{date.minute}"
      else:
        minute = date.minute
      created_date = f"{day}.{month}.{year} {hour}:{minute}"

      # Calculate updated Beds based on Regulations
      # single_rooms_current = 0
      # double_rooms_current = 0
      # rooms_fulfillment = 0
      # fulfillment = 0.8
      # beds_loss = 0
      # rooms_future = 0
      # current_rooms = 0
      regulations = anvil.server.call('read_regulations', federal_state)
      facilities_amount = 0
      facilities_single_rooms = 0
      facilities_double_rooms = 0
      facilities_bed_amount = 0
      facilities_rooms = 0
      facilities_single_room_quote = 0
      facilities_single_rooms_future = 0
      facilities_double_rooms_future = 0
      facilities_bed_amount_future = 0
      facilities_single_room_quote_future = 0
      for index, competitor in enumerate(data_comp_analysis_nh['data']):
        if not competitor[0]['ez'] == '-' or not competitor[0]['dz'] == '-':
          facilities_amount += 1
          ''' Get amount of single Rooms inside Facility '''
          if not competitor[0]['ez'] == '-' and competitor[0]['ez'] is not None:
            facility_single_rooms = int(competitor[0]['ez'])
          else:
            facility_single_rooms = 0
          ''' Get amount of double Rooms inside Facility '''
          if not competitor[0]['dz'] == '-' and competitor[0]['dz'] is not None:
            facility_double_rooms = int(competitor[0]['dz'])
          else:
            facility_double_rooms = 0
          ''' Get overall amount of Rooms inside Facility '''
          facility_rooms = facility_single_rooms + facility_double_rooms
          ''' Get single room quote of facility '''
          facility_single_room_quote = facility_single_rooms / facility_rooms
          ''' Get bed amount of facility '''
          facility_bed_amount = facility_single_rooms + facility_double_rooms * 2
          ''' Get single room quota from regulations '''
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
          ''' Check if single room quota is below quota from regulations '''
          if facility_single_room_quote < facility_single_room_quote_future:
            ''' Calculate future amount of single rooms based on quota from regulations '''
            facility_single_rooms_future = int(round(facility_rooms * facility_single_room_quote_future, 0))
            ''' Calculate future amount of double rooms based on quota from regulations '''
            facility_double_rooms_future = int(round(facility_rooms - facility_single_rooms_future, 0))
            ''' Calculate future amount of beds based on quota from regulations '''
            facility_bed_amount_future = int(round(facility_single_rooms_future + facility_double_rooms_future * 2, 0))
          else:
            facility_single_room_quote_future = facility_single_room_quote
            facility_single_rooms_future = facility_single_rooms
            facility_double_rooms_future = facility_double_rooms
            facility_bed_amount_future = facility_bed_amount
          ''' Add current facility values to overall values '''
          if facility_bed_amount_future > facility_max_beds_future:
              facility_bed_amount_future = facility_max_beds_future
          facilities_single_rooms += facility_single_rooms
          facilities_double_rooms += facility_double_rooms
          facilities_bed_amount += facility_bed_amount
          facilities_rooms += facility_rooms
          facilities_single_room_quote += facility_single_room_quote
          facilities_single_rooms_future += facility_single_rooms_future
          facilities_double_rooms_future += facility_double_rooms_future
          facilities_bed_amount_future += facility_bed_amount_future
          facilities_single_room_quote_future += facility_single_room_quote_future
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
      beds_surplus_30_avg = round((beds_surplus + beds_surplus_v2) / 2)
      beds_surplus_35_avg = round((beds_surplus_35 + beds_surplus_35_v2) / 2)
      beds_in_reserve_fc = round(beds_adjusted * 0.05)

      market_study_pages = ["COVER", "SUMMARY", "LOCATION ANALYSIS"]
      share_url = self.create_share_map('market_study')

      max_pages = 2
      summary_page = 2
      location_analysis_page = 3
      competitor_analysis_pages = [4]
      
      market_study_data = copy.deepcopy(ExcelFrames.market_study_data)
      market_study_data['pages']['COVER']['cell_content']['images']['AB7']['file'] = f"tmp/summary_map_{unique_code}.png"
      market_study_data['pages']['COVER']['cell_content']['textboxes']['Y29']['text'] = "{:.2f}".format(purchase_power)
      market_study_data['pages']['COVER']['cell_content']['textboxes']['Y38']['text'] = population_trend_string
      market_study_data['pages']['COVER']['cell_content']['textboxes']['Y47']['text'] = f"{beds_surplus_35_v2:,}"
      market_study_data['pages']['COVER']['cell_content']['textboxes']['C51']['text'] = f"Version 2.1.0 Generated on {created_date}"
      market_study_data['pages']['COVER']['cell_content']['cells']['L30']['text'] = street
      market_study_data['pages']['COVER']['cell_content']['cells']['L31']['text'] = zipcode
      market_study_data['pages']['COVER']['cell_content']['cells']['L32']['text'] = city
      market_study_data['pages']['COVER']['cell_content']['cells']['L33']['text'] = district
      market_study_data['pages']['COVER']['cell_content']['cells']['L34']['text'] = federal_state
      market_study_data['pages']['COVER']['cell_content']['cells']['L36']['text'] = f"{iso_time} minutes of {movement}"
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P10']['text'] = countie_data['dem_city']['bevoelkerung_ges']
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P11']['text'] = countie_data['ex_dem_lk']['all_compl']
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P13']['text'] = people_u80
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P14']['text'] = round(people_u80 / countie_data['ex_dem_lk']['all_compl'], 2)
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P15']['text'] = people_o80
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P16']['text'] = round(people_o80 / countie_data['ex_dem_lk']['all_compl'], 2)
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P20']['text'] = new_care_rate_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P21']['text'] = nursing_home_rate
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P22']['text'] = inpatients_lk
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P23']['text'] = occupancy_lk_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P24']['text'] = beds_lk
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P25']['text'] = free_beds_lk
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P29']['text'] = nursing_homes_active
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P30']['text'] = beds_active
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P31']['text'] = occupancy_lk_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P32']['text'] = '-' if nursing_homes_planned == 0 else nursing_homes_planned
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P33']['text'] = '-' if nursing_homes_construct == 0 else nursing_homes_construct
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P34']['text'] = '-' if beds_planned == 0 else beds_planned
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P35']['text'] = '-' if beds_construct == 0 else beds_construct
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P37']['text'] = beds_active
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['P38']['text'] = inpatients
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R20']['text'] = care_rate_30_v1_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R21']['text'] = nursing_home_rate
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R22']['text'] = pat_rec_full_care_fc_30_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R24']['text'] = beds_30_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R25']['text'] = free_beds_30_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R30']['text'] = beds_active + beds_planned + beds_construct
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R36']['text'] = loss_of_beds
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R37']['text'] = beds_adjusted_30_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R38']['text'] = inpatients_fc
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['R39']['text'] = beds_surplus      
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S11']['text'] = population_fc
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S13']['text'] = people_u80_fc
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S14']['text'] = round(people_u80_fc / population_fc, 2)
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S15']['text'] = people_o80_fc
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S16']['text'] = round(people_o80_fc / population_fc, 2)
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S20']['text'] = care_rate_30_v2_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S21']['text'] = nursing_home_rate
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S22']['text'] = pat_rec_full_care_fc_30_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S24']['text'] = beds_30_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S25']['text'] = free_beds_30_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S30']['text'] = beds_active + beds_planned + beds_construct
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S36']['text'] = loss_of_beds
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S37']['text'] = beds_adjusted_30_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S38']['text'] = inpatients_fc_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['S39']['text'] = beds_surplus_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U20']['text'] = care_rate_35_v1_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U21']['text'] = nursing_home_rate
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U22']['text'] = pat_rec_full_care_fc_35_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U24']['text'] = beds_35_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U25']['text'] = free_beds_35_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U30']['text'] = beds_active + beds_planned + beds_construct
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U36']['text'] = loss_of_beds
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U37']['text'] = beds_adjusted_35_v1
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U38']['text'] = inpatients_fc_35
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['U39']['text'] = beds_surplus_35
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V11']['text'] = population_fc_35
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V13']['text'] = people_u80_fc_35
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V14']['text'] = round(people_u80_fc_35 / population_fc_35, 2)
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V15']['text'] = people_o80_fc_35
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V16']['text'] = round(people_o80_fc_35 / population_fc_35, 2)
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V20']['text'] = care_rate_35_v2_raw
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V21']['text'] = nursing_home_rate
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V22']['text'] = pat_rec_full_care_fc_35_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V24']['text'] = beds_35_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V25']['text'] = free_beds_35_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V30']['text'] = beds_active + beds_planned + beds_construct
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V36']['text'] = loss_of_beds
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V37']['text'] = beds_adjusted_35_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V38']['text'] = inpatients_fc_35_v2
      market_study_data['pages']['SUMMARY']['cell_content']['cells']['V39']['text'] = beds_surplus_35_v2
      market_study_data['pages']['SUMMARY']['cell_content']['merge_cells']['C4:P5']['text'] = city
      market_study_data['pages']['SUMMARY']['cell_content']['merge_cells']['C10:O10']['text'] = f"Population {city} (City)"
      market_study_data['pages']['SUMMARY']['cell_content']['merge_cells']['C11:O11']['text'] = f"Population {countie[0]} (County)"
      market_study_data['pages']['SUMMARY']['cell_content']['merge_cells']['C28:O28']['text'] = f"Viewing radius: {iso_time} minutes of {movement}"

      anvil.js.call('update_loading_bar', 65, 'Generating Analysis Text')
      
      analysis_text = "I`m a placeholder Text"
      # analysis_text = anvil.server.call('openai_test', city)
      from .ChatGPT import ChatGPT
      Functions.manipulate_loading_overlay(self, False)
      analysis_text = alert(ChatGPT(generated_text=analysis_text), buttons=[], dismissible=False, large=True, role='custom_alert')
      Functions.manipulate_loading_overlay(self, True)

      anvil.js.call('update_loading_bar', 70, 'Create Excel for Market Study Part 2')
      
      market_study_data['pages']['LOCATION ANALYSIS']['cell_content']['merge_cells']['C4:J5']['text'] = city
      market_study_data['pages']['LOCATION ANALYSIS']['cell_content']['merge_cells']['H23:R38']['text'] = analysis_text
      market_study_data['pages']['LOCATION ANALYSIS']['cell_content']['merge_cells']['C21:S21']['text'] = share_url
      market_study_data['pages']['LOCATION ANALYSIS']['cell_content']['cells']['E37']['text'] = f"{iso_time} minutes of {movement}"
      # market_study_data['pages']['LOCATION ANALYSIS']['cell_content']['images']['Q9']['settings']['url'] = share_url

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
      
      if total_amount <= 13:
        # Single Page
        market_study_pages.append("COMPETITOR ANALYSIS 1")
        
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['merge_cells']['C9:E9'] = {
          'text': "Nursing Homes",
          'format': 'nh_heading'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['merge_cells']['C26:M26'] = {
          'text': '¹The Facility does / does not comply with the respective federal state regulation. For more info see page "Good to Know"',
          'format': 'foot_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['G9'] = {
          'text': "Operator name",
          'format': "operator_heading"
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['H9'] = {
          'text': "Web",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['I9'] = {
          'text': "Top 30 Operator",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['J9'] = {
          'text': "Operator type",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['K9'] = {
          'text': "Asset status",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['L9'] = {
          'text': "Year of construction",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['M9'] = {
          'text': "Apartments (AL)",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['N9'] = {
          'text': "Legally compliant¹",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['O9'] = {
          'text': "Care beds",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['P9'] = {
          'text': "Single rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['Q9'] = {
          'text': "Double rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['R9'] = {
          'text': "Rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['S9'] = {
          'text': "Single room quota",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['T9'] = {
          'text': "Occupancy rates",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['U9'] = {
          'text': "Invest cost (p. day in €)",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells']['V9'] = {
          'text': "MDK grade (2019)",
          'format': 'rotated_text'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['merge_cells']['C3:X4']['text'] = city

        current_row = 11
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

        for index, competitor in enumerate(data_comp_analysis_nh['data']):
          if 'home' in competitor:
            home_counter += 1
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'C{current_row}'] = {
              'text': '⌂',
              'format': 'home_icon'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'home_line_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'G{current_row}'] = {
              'text': competitor[0]['raw_betreiber'],
              'format': 'home_line_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'home_line_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'L{current_row}'] = {
              'text': competitor[0]['baujahr'],
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'M{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'N{current_row}'] = {
              'text': competitor[0]['legal'],
              'format': 'home_line_centered'
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
                single_room_quote = single_rooms / (single_rooms + double_rooms)
              else:
                rooms = single_rooms
                single_room_quote = 1
            else:
              if not double_rooms == '-':
                rooms = double_rooms
                single_room_quote = 0
              else:
                rooms = '-'
                beds = '-'
                single_room_quote = '-'
            
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'O{current_row}'] = {
              'text': beds,
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'P{current_row}'] = {
              'text': single_rooms,
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'Q{current_row}'] = {
              'text': double_rooms,
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'R{current_row}'] = {
              'text': rooms,
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'S{current_row}'] = {
              'text': single_room_quote,
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'T{current_row}'] = {
              'text': competitor[0]['occupancy'],
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'U{current_row}'] = {
              'text': '-' if competitor[0]['invest'] == '-' else float(competitor[0]['invest']),
              'format': 'home_line_centered_number_double'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'V{current_row}'] = {
              'text': '-' if competitor[0]['mdk_note'] == '-' else float(competitor[0]['mdk_note']),
              'format': 'home_line_centered_number'
            }

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
            else:
              home_invest = -1
            if not competitor[0]['mdk_note'] == '-':
              list_mdk_grade.append(float(competitor[0]['mdk_note']))
            if not competitor[0]['baujahr'] == '-':
              list_years_of_construction_nh.append(int(competitor[0]['baujahr']))
            if not competitor[0]['invest'] == '-' and not competitor[0]['baujahr'] == '-':
              invest_plot_data.append(['home', competitor[0]['invest'], competitor[0]['baujahr'], '⌂'])
          
          else:
            if not prev_competitor_distance == competitor[1]:
              prev_competitor_distance = competitor[1]
              prev_competitor_index += 1
              
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'C{current_row}'] = {
              'text': index + 1 - home_counter,
              'format': 'row_number'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'row_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'G{current_row}'] = {
              'text': '-' if competitor[0]['raw_betreiber'] == '-' else competitor[0]['raw_betreiber'],
              'format': 'row_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'row_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public",
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'L{current_row}'] = {
              'text': '-' if competitor[0]['baujahr'] == '-' else competitor[0]['baujahr'],
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'M{current_row}'] = {
              'text': "-",
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'N{current_row}'] = {
              'text': competitor[0]['legal'],
              'format': 'row_centered'
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
                single_room_quote = single_rooms / (single_rooms + double_rooms)
              else:
                rooms = single_rooms
                single_room_quote = 1
            else:
              if not double_rooms == '-':
                rooms = double_rooms
                single_room_quote = 0
              else:
                rooms = '-'
                single_room_quote = '-'
              
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'O{current_row}'] = {
              'text': beds,
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'P{current_row}'] = {
              'text': single_rooms,
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'Q{current_row}'] = {
              'text': double_rooms,
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'R{current_row}'] = {
              'text': rooms,
              'format': 'row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'S{current_row}'] = {
              'text': single_room_quote,
              'format': 'row_centered_percentage'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'T{current_row}'] = {
              'text': competitor[0]['occupancy'],
              'format': 'row_centered_percentage'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'U{current_row}'] = {
              'text': '-' if competitor[0]['invest'] == '-' else float(competitor[0]['invest']),
              'format': 'row_centered_number_double'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'V{current_row}'] = {
              'text': '-' if competitor[0]['mdk_note'] == '-' else float(competitor[0]['mdk_note']),
              'format': 'row_centered_number'
            }

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
              invest_plot_data.append(['non-profit' if competitor[0]['operator_type'] == 'gemeinnützig' else 'private' if competitor[0]['operator_type'] == 'privat' else 'public', competitor[0]['invest'], competitor[0]['baujahr'], index - home_counter + 1])
  
          current_row += 1

        if len(list_single_room_quota) > 0:
          total_single_room_quota = anvil.server.call("get_median", list_single_room_quota)
        else:
          total_single_room_quota = 0
        if len(list_occupancy_rate) > 0:
          total_occupancy_rate = anvil.server.call("get_median", list_occupancy_rate)
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
          total_invest_cost = anvil.server.call("get_median", list_invest_cost)
        else:
          total_invest_cost = 0
        if len(list_mdk_grade) > 0:
          total_mdk_grade = anvil.server.call("get_median", list_mdk_grade)
        else:
          total_mdk_grade = 0

        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'O{current_row}'] = {
          'text': total_beds,
          'format': 'overall_sum'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'P{current_row}'] = {
          'text': total_single_rooms,
          'format': 'overall_sum'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'Q{current_row}'] = {
          'text': total_double_rooms,
          'format': 'overall_sum'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'R{current_row}'] = {
          'text': total_rooms,
          'format': 'overall_sum'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'S{current_row}'] = {
          'text': total_single_room_quota,
          'format': 'overall_median_percentage'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'T{current_row}'] = {
          'text': total_occupancy_rate,
          'format': 'overall_median_percentage'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'U{current_row}'] = {
          'text': total_invest_cost,
          'format': 'overall_median'
        }
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'V{current_row}'] = {
          'text': total_mdk_grade,
          'format': 'overall_median'
        }
        
        current_row += 1
        
        market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['merge_cells'][f'C{current_row}:E{current_row}'] = {
          'text': "Assisted Living",
          'format': 'al_heading'
        }

        current_row += 1
        prev_competitor_distance = 0
        prev_competitor_index = 0
        
        for index, competitor in enumerate(data_comp_analysis_al['data']):
          home_counter = 0
          if 'home' in competitor:
            home_counter += 1
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'C{current_row}'] = {
              'text': '⌂',
              'format': 'home_icon'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'home_line_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'G{current_row}'] = {
              'text': competitor[0]['raw_betreiber'],
              'format': 'home_line_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'home_line_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'L{current_row}'] = {
              'text': competitor[0]['year_of_construction'],
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'M{current_row}'] = {
              'text': competitor[0]['number_apts'],
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'N{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'O{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'P{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'Q{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'R{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'S{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'T{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'U{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_number_double'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'V{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_number'
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
            if not prev_competitor_distance == competitor[1]:
              prev_competitor_distance = competitor[1]
              prev_competitor_index += 1
              
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'C{current_row}'] = {
              'text': index + 1 - home_counter,
              'format': 'row_number_al'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'row_normal' if not current_row == 25 else 'last_row_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'G{current_row}'] = {
              'text': '-' if competitor[0]['raw_betreiber'] == '-' else competitor[0]['raw_betreiber'],
              'format': 'row_normal' if not current_row == 25 else 'last_row_normal'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'row_centered_link' if not current_row == 25 else 'last_row_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'L{current_row}'] = {
              'text': '-' if competitor[0]['year_of_construction'] == '-' else competitor[0]['year_of_construction'],
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'M{current_row}'] = {
              'text': competitor[0]['number_apts'],
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'N{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'O{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'P{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'Q{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'R{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'S{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'T{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'U{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages']['COMPETITOR ANALYSIS 1']['cell_content']['cells'][f'V{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }

            if not competitor[0]['year_of_construction'] == '-':
              list_years_of_construction_al.append(int(competitor[0]['year_of_construction']))
            if competitor[0]['type'] == 'gemeinnützig':
              none_profit_operator_al += 1
            elif competitor[0]['type'] == 'kommunal':
              public_operator_al += 1
            elif competitor[0]['type'] == 'privat':
              private_operator_al += 1
  
          current_row += 1
      
      else:
        # Nursing Home Pages
        current_row = 11
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
        page = 1
        sheet_name = f"COMPETITOR ANALYSIS {page}"
        market_study_pages.append(sheet_name)
        market_study_data['pages'][sheet_name] = {
          'settings': {
            'area': "A1:X28",
            'column_width': [
                2.09, 2.09, 2.64, 0.17, 25.36, 0.00, 24.45, 3.27, 3.27, 6.45, 8.18, 4.73, 3.27, 3.55, 5.82,
                5.82, 5.82, 5.82, 5.18, 6.00, 5.27, 4.91, 0.00, 3.91
            ],
            'row_height': [
                16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 95.50, 3.50, 19.00, 17.00, 17.00,
                17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 16.50,
                14.00, 8.00
            ],
            'columns_to_fill': [
                'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X'
            ],
            'landscape': True,
            'rows_to_fill': [8, 10, 25],
            'fill_format': {
                'base': {
                    '8': "underline",
                    '10': "underline",
                    '25': "underline"
                }
            }
          },
          'cell_content': {
              'textboxes': {
                  'A1': {
                      'text': "Capital Bay Group   |",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          }
                      }
                  },
                  'E1_A': {
                      'text': "Market Study",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9,
                              'bold': True
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          },
                          'x_offset': 46
                      }
                  },
                  'E1_B': {
                      'text': "CARE",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9,
                              'bold': True,
                              'color': "#C8B058"
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          },
                          'x_offset': 128
                      }
                  },
                  'V1': {
                      'text': "4 | 7",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9,
                              'bold': True
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          },
                          'align': {
                              'text': 'right'
                          },
                          'width': 65
                      }
                  }
              },
              'merge_cells': {
                  'C3:X4': {
                      'text': "Bad Rappenau",
                      'format': "place_heading_format"
                  },
                  'C5:X6': {
                      'text': "Competitor Analysis",
                      'format': "situation_heading_format"
                  }
              },
              'cells': {}
          }
        }
        market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C9:E9'] = {
          'text': "Nursing Homes",
          'format': 'nh_heading'
        }
        market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C26:M26'] = {
          'text': '¹The Facility does / does not comply with the respective federal state regulation. For more info see page "Good to Know"',
          'format': 'foot_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['G9'] = {
          'text': "Operator name",
          'format': "operator_heading"
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['H9'] = {
          'text': "Web",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['I9'] = {
          'text': "Top 30 Operator",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['J9'] = {
          'text': "Operator type",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['K9'] = {
          'text': "Asset status",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['L9'] = {
          'text': "Year of construction",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['M9'] = {
          'text': "Apartments (AL)",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['N9'] = {
          'text': "Legally compliant¹",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['O9'] = {
          'text': "Care beds",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['P9'] = {
          'text': "Single rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['Q9'] = {
          'text': "Double rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['R9'] = {
          'text': "Rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['S9'] = {
          'text': "Single room quota",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['T9'] = {
          'text': "Occupancy rates",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['U9'] = {
          'text': "Invest cost (p. day in €)",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['V9'] = {
          'text': "MDK grade (2019)",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C3:X4']['text'] = city

        for index, competitor in enumerate(data_comp_analysis_nh['data']):
          if index % 15 == 0 and not index == 0:
            competitor_analysis_pages.append(competitor_analysis_pages[-1] + 1)
            page += 1
            current_row = 11
            sheet_name = f"COMPETITOR ANALYSIS {page}"
            market_study_pages.append(sheet_name)
            market_study_data['pages'][sheet_name] = {
              'settings': {
                'area': "A1:X28",
                'column_width': [
                    2.09, 2.09, 2.64, 0.17, 25.36, 0.00, 24.45, 3.27, 3.27, 6.45, 8.18, 4.73, 3.27, 3.55, 5.82,
                    5.82, 5.82, 5.82, 5.18, 6.00, 5.27, 4.91, 0.00, 3.91
                ],
                'row_height': [
                    16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 95.50, 3.50, 19.00, 17.00, 17.00,
                    17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 16.50,
                    14.00, 8.00
                ],
                'columns_to_fill': [
                    'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                    'V', 'W', 'X'
                ],
                'landscape': True,
                'rows_to_fill': [8, 10, 25],
                'fill_format': {
                    'base': {
                        '8': "underline",
                        '10': "underline",
                        '25': "underline"
                    }
                }
              },
              'cell_content': {
                  'textboxes': {
                      'A1': {
                          'text': "Capital Bay Group   |",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              }
                          }
                      },
                      'E1_A': {
                          'text': "Market Study",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9,
                                  'bold': True
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              },
                              'x_offset': 46
                          }
                      },
                      'E1_B': {
                          'text': "CARE",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9,
                                  'bold': True,
                                  'color': "#C8B058"
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              },
                              'x_offset': 128
                          }
                      },
                      'V1': {
                          'text': "4 | 7",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9,
                                  'bold': True
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              },
                              'align': {
                                  'text': 'right'
                              },
                              'width': 65
                          }
                      }
                  },
                  'merge_cells': {
                      'C3:X4': {
                          'text': "Bad Rappenau",
                          'format': "place_heading_format"
                      },
                      'C5:X6': {
                          'text': "Competitor Analysis",
                          'format': "situation_heading_format"
                      }
                  },
                  'cells': {}
              }
            }
            market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C9:E9'] = {
              'text': "Nursing Homes",
              'format': 'nh_heading'
            }
            market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C26:M26'] = {
              'text': '¹The Facility does / does not comply with the respective federal state regulation. For more info see page "Good to Know"',
              'format': 'foot_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['G9'] = {
              'text': "Operator name",
              'format': "operator_heading"
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['H9'] = {
              'text': "Web",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['I9'] = {
              'text': "Top 30 Operator",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['J9'] = {
              'text': "Operator type",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['K9'] = {
              'text': "Asset status",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['L9'] = {
              'text': "Year of construction",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['M9'] = {
              'text': "Apartments (AL)",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['N9'] = {
              'text': "Legally compliant¹",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['O9'] = {
              'text': "Care beds",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['P9'] = {
              'text': "Single rooms",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['Q9'] = {
              'text': "Double rooms",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['R9'] = {
              'text': "Rooms",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['S9'] = {
              'text': "Single room quota",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['T9'] = {
              'text': "Occupancy rates",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['U9'] = {
              'text': "Invest cost (p. day in €)",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['V9'] = {
              'text': "MDK grade (2019)",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C3:X4']['text'] = city
          
          if 'home' in competitor:
            home_counter += 1
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'C{current_row}'] = {
              'text': '⌂',
              'format': 'home_icon'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'home_line_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'G{current_row}'] = {
              'text': competitor[0]['raw_betreiber'],
              'format': 'home_line_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'home_line_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'L{current_row}'] = {
              'text': competitor[0]['baujahr'],
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'M{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'N{current_row}'] = {
              'text': competitor[0]['legal'],
              'format': 'home_line_centered'
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
                single_room_quote = single_rooms / (single_rooms + double_rooms)
              else:
                rooms = single_rooms
                single_room_quote = 1
            else:
              if not double_rooms == '-':
                rooms = double_rooms
                single_room_quote = 0
              else:
                rooms = '-'
                single_room_quote = '-'
              
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'O{current_row}'] = {
              'text': beds,
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'P{current_row}'] = {
              'text': single_rooms,
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'Q{current_row}'] = {
              'text': double_rooms,
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'R{current_row}'] = {
              'text': rooms,
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'S{current_row}'] = {
              'text': single_room_quote,
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'T{current_row}'] = {
              'text': competitor[0]['occupancy'],
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'U{current_row}'] = {
              'text': '-' if competitor[0]['invest'] == '-' else float(competitor[0]['invest']),
              'format': 'home_line_centered_number_double'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'V{current_row}'] = {
              'text': '-' if competitor[0]['mdk_note'] == '-' else float(competitor[0]['mdk_note']),
              'format': 'home_line_centered_number'
            }

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
            else:
              home_invest = -1
            if not competitor[0]['mdk_note'] == '-':
              list_mdk_grade.append(float(competitor[0]['mdk_note']))
            if not competitor[0]['baujahr'] == '-':
              list_years_of_construction_nh.append(int(competitor[0]['baujahr']))
            if not competitor[0]['invest'] == '-' and not competitor[0]['baujahr'] == '-':
              invest_plot_data.append(['home', competitor[0]['invest'], competitor[0]['baujahr'], '⌂'])
          
          else:
            
            if not prev_competitor_distance == competitor[1]:
              prev_competitor_distance = competitor[1]
              prev_competitor_index += 1
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'C{current_row}'] = {
              'text': prev_competitor_index,
              'format': 'row_number'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'row_normal' if not current_row == 25 else 'last_row_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'G{current_row}'] = {
              'text': '-' if competitor[0]['raw_betreiber'] == '-' else competitor[0]['raw_betreiber'],
              'format': 'row_normal' if not current_row == 25 else 'last_row_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'row_centered_link' if not current_row == 25 else 'last_row_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['operator_type'] == "privat" else "non-profit" if competitor[0]['operator_type'] == "gemeinnützig" else "public",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'L{current_row}'] = {
              'text': '-' if competitor[0]['baujahr'] == '-' else competitor[0]['baujahr'],
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'M{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'N{current_row}'] = {
              'text': competitor[0]['legal'],
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
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
                beds = single_rooms + double_rooms * 2
                single_room_quote = single_rooms / (single_rooms + double_rooms)
              else:
                rooms = single_rooms
                beds = single_rooms
                single_room_quote = 1
            else:
              if not double_rooms == '-':
                rooms = double_rooms
                beds = double_rooms * 2
                single_room_quote = 0
              else:
                rooms = '-'
                beds = '-'
                single_room_quote = '-'
                
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'O{current_row}'] = {
              'text': beds,
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'P{current_row}'] = {
              'text': single_rooms,
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'Q{current_row}'] = {
              'text': double_rooms,
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'R{current_row}'] = {
              'text': rooms,
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'S{current_row}'] = {
              'text': single_room_quote,
              'format': 'row_centered_percentage' if not current_row == 25 else 'last_row_centered_percentage'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'T{current_row}'] = {
              'text': competitor[0]['occupancy'],
              'format': 'row_centered_percentage' if not current_row == 25 else 'last_row_centered_percentage'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'U{current_row}'] = {
              'text': '-' if competitor[0]['invest'] == '-' else float(competitor[0]['invest']),
              'format': 'row_centered_number_double' if not current_row == 25 else 'last_row_centered_number_double'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'V{current_row}'] = {
              'text': float(competitor[0]['mdk_note']) if not competitor[0]['mdk_note'] == '-' else competitor[0]['mdk_note'],
              'format': 'row_centered_number' if not current_row == 25 else 'last_row_centered_number'
            }
            
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
              invest_plot_data.append(['non-profit' if competitor[0]['operator_type'] == 'gemeinnützig' else 'private' if competitor[0]['operator_type'] == 'privat' else 'public', competitor[0]['invest'], competitor[0]['baujahr'], index - home_counter + 1])
            
          current_row += 1
        
        if len(list_single_room_quota) > 0:
          total_single_room_quota = anvil.server.call("get_median", list_single_room_quota)
        else:
          total_single_room_quota = 0
        if len(list_occupancy_rate) > 0:
          total_occupancy_rate = anvil.server.call("get_median", list_occupancy_rate)
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
          total_invest_cost = anvil.server.call("get_median", list_invest_cost)
        else:
          total_invest_cost = 0
        if len(list_mdk_grade) > 0:
          total_mdk_grade = anvil.server.call("get_median", list_mdk_grade)
        else:
          total_mdk_grade = 0
        
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'O{current_row}'] = {
          'text': total_beds,
          'format': 'overall_sum'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'P{current_row}'] = {
          'text': total_single_rooms,
          'format': 'overall_sum'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'Q{current_row}'] = {
          'text': total_double_rooms,
          'format': 'overall_sum'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'R{current_row}'] = {
          'text': total_rooms,
          'format': 'overall_sum'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'S{current_row}'] = {
          'text': total_single_room_quota,
          'format': 'overall_median_percentage'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'T{current_row}'] = {
          'text': total_occupancy_rate,
          'format': 'overall_median_percentage'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'U{current_row}'] = {
          'text': total_invest_cost,
          'format': 'overall_median'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells'][f'V{current_row}'] = {
          'text': total_mdk_grade,
          'format': 'overall_median'
        }
        
        current_row += 1

        # Assisted Living Pages
        current_row = 11
        home_counter = 0
        prev_competitor_distance = 0
        prev_competitor_index = 0
        competitor_analysis_pages.append(competitor_analysis_pages[-1] + 1)
        page += 1
        sheet_name = f"COMPETITOR ANALYSIS {page}"
        market_study_pages.append(sheet_name)
        market_study_data['pages'][sheet_name] = {
          'settings': {
            'area': "A1:X28",
            'column_width': [
                2.09, 2.09, 2.64, 0.17, 25.36, 0.00, 24.45, 3.27, 3.27, 6.45, 8.18, 4.73, 3.27, 3.55, 5.82,
                5.82, 5.82, 5.82, 5.18, 6.00, 5.27, 4.91, 0.00, 3.91
            ],
            'row_height': [
                16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 95.50, 3.50, 19.00, 17.00, 17.00,
                17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 16.50,
                14.00, 8.00
            ],
            'columns_to_fill': [
                'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X'
            ],
            'landscape': True,
            'rows_to_fill': [8, 10, 25],
            'fill_format': {
                'base': {
                    '8': "underline",
                    '10': "underline",
                    '25': "underline"
                }
            }
          },
          'cell_content': {
              'textboxes': {
                  'A1': {
                      'text': "Capital Bay Group   |",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          }
                      }
                  },
                  'E1_A': {
                      'text': "Market Study",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9,
                              'bold': True
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          },
                          'x_offset': 46
                      }
                  },
                  'E1_B': {
                      'text': "CARE",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9,
                              'bold': True,
                              'color': "#C8B058"
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          },
                          'x_offset': 128
                      }
                  },
                  'V1': {
                      'text': "4 | 7",
                      'settings': {
                          'font': {
                              'name': "Segoe UI",
                              'size': 9,
                              'bold': True
                          },
                          'line': {
                              'none': True
                          },
                          'fill': {
                              'none': True
                          },
                          'align': {
                              'text': 'right'
                          },
                          'width': 65
                      }
                  }
              },
              'merge_cells': {
                  'C3:X4': {
                      'text': "Bad Rappenau",
                      'format': "place_heading_format"
                  },
                  'C5:X6': {
                      'text': "Competitor Analysis",
                      'format': "situation_heading_format"
                  }
              },
              'cells': {}
          }
        }
        market_study_data['pages'][sheet_name]['cell_content']['merge_cells'][f'C9:E9'] = {
          'text': "Assisted Living",
          'format': 'al_heading'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['G9'] = {
          'text': "Operator name",
          'format': "operator_heading"
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['H9'] = {
          'text': "Web",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['I9'] = {
          'text': "Top 30 Operator",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['J9'] = {
          'text': "Operator type",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['K9'] = {
          'text': "Asset status",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['L9'] = {
          'text': "Year of construction",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['M9'] = {
          'text': "Apartments (AL)",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['N9'] = {
          'text': "Legally compliant¹",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['O9'] = {
          'text': "Care beds",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['P9'] = {
          'text': "Single rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['Q9'] = {
          'text': "Double rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['R9'] = {
          'text': "Rooms",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['S9'] = {
          'text': "Single room quota",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['T9'] = {
          'text': "Occupancy rates",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['U9'] = {
          'text': "Invest cost (p. day in €)",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['cells']['V9'] = {
          'text': "MDK grade (2019)",
          'format': 'rotated_text'
        }
        market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C3:X4']['text'] = city
        
        for index, competitor in enumerate(data_comp_analysis_al['data']):
          if index % 15 == 0 and not index == 0:
            competitor_analysis_pages.append(competitor_analysis_pages[-1] + 1)
            page += 1
            current_row = 11
            sheet_name = f"COMPETITOR ANALYSIS {page}"
            market_study_pages.append(sheet_name)
            market_study_data['pages'][sheet_name] = {
              'settings': {
                'area': "A1:X28",
                'column_width': [
                    2.09, 2.09, 2.64, 0.17, 25.36, 0.00, 24.45, 3.27, 3.27, 6.45, 8.18, 4.73, 3.27, 3.55, 5.82,
                    5.82, 5.82, 5.82, 5.18, 6.00, 5.27, 4.91, 0.00, 3.91
                ],
                'row_height': [
                    16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 95.50, 3.50, 19.00, 17.00, 17.00,
                    17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 16.50,
                    14.00, 8.00
                ],
                'columns_to_fill': [
                    'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                    'V', 'W', 'X'
                ],
                'landscape': True,
                'rows_to_fill': [8, 10, 25],
                'fill_format': {
                    'base': {
                        '8': "underline",
                        '10': "underline",
                        '25': "underline"
                    }
                }
              },
              'cell_content': {
                  'textboxes': {
                      'A1': {
                          'text': "Capital Bay Group   |",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              }
                          }
                      },
                      'E1_A': {
                          'text': "Market Study",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9,
                                  'bold': True
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              },
                              'x_offset': 46
                          }
                      },
                      'E1_B': {
                          'text': "CARE",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9,
                                  'bold': True,
                                  'color': "#C8B058"
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              },
                              'x_offset': 128
                          }
                      },
                      'V1': {
                          'text': "4 | 7",
                          'settings': {
                              'font': {
                                  'name': "Segoe UI",
                                  'size': 9,
                                  'bold': True
                              },
                              'line': {
                                  'none': True
                              },
                              'fill': {
                                  'none': True
                              },
                              'align': {
                                  'text': 'right'
                              },
                              'width': 65
                          }
                      }
                  },
                  'merge_cells': {
                      'C3:X4': {
                          'text': "Bad Rappenau",
                          'format': "place_heading_format"
                      },
                      'C5:X6': {
                          'text': "Competitor Analysis",
                          'format': "situation_heading_format"
                      }
                  },
                  'cells': {}
              }
            }
            market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C9:E9'] = {
              'text': "Assisted Living",
              'format': 'al_heading'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['G9'] = {
              'text': "Operator name",
              'format': "operator_heading"
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['H9'] = {
              'text': "Web",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['I9'] = {
              'text': "Top 30 Operator",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['J9'] = {
              'text': "Operator type",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['K9'] = {
              'text': "Asset status",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['L9'] = {
              'text': "Year of construction",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['M9'] = {
              'text': "Apartments (AL)",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['N9'] = {
              'text': "Legally compliant¹",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['O9'] = {
              'text': "Care beds",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['P9'] = {
              'text': "Single rooms",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['Q9'] = {
              'text': "Double rooms",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['R9'] = {
              'text': "Rooms",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['S9'] = {
              'text': "Single room quota",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['T9'] = {
              'text': "Occupancy rates",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['U9'] = {
              'text': "Invest cost (p. day in €)",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells']['V9'] = {
              'text': "MDK grade (2019)",
              'format': 'rotated_text'
            }
            market_study_data['pages'][sheet_name]['cell_content']['merge_cells']['C3:X4']['text'] = city
            
          home_counter = 0
          if 'home' in competitor:
            home_counter += 1
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'C{current_row}'] = {
              'text': '⌂',
              'format': 'home_icon'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'home_line_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'G{current_row}'] = {
              'text': competitor[0]['raw_betreiber'],
              'format': 'home_line_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'home_line_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'L{current_row}'] = {
              'text': competitor[0]['year_of_construction'],
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'M{current_row}'] = {
              'text': competitor[0]['number_apts'],
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'N{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'O{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'P{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'Q{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'R{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'S{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'T{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_percentage'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'U{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_number_double'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'V{current_row}'] = {
              'text': "-",
              'format': 'home_line_centered_number'
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
            if not prev_competitor_distance == competitor[1]:
              prev_competitor_distance = competitor[1]
              prev_competitor_index += 1
              
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'C{current_row}'] = {
              'text': index + 1 - home_counter,
              'format': 'row_number_al'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'E{current_row}'] = {
              'text': competitor[0]['raw_name'],
              'format': 'row_normal' if not current_row == 25 else 'last_row_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'G{current_row}'] = {
              'text': '-' if competitor[0]['raw_betreiber'] == '-' else competitor[0]['raw_betreiber'],
              'format': 'row_normal' if not current_row == 25 else 'last_row_normal'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'H{current_row}'] = {
              'text': competitor[0]['web'] if not "keine " in competitor[0]['web'] else "-",
              'format': 'row_centered_link' if not current_row == 25 else 'last_row_centered_link',
              # 'string': "↗"
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'I{current_row}'] = {
              'text': anvil.server.call("read_top_30", competitor[0]['raw_betreiber']),
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'J{current_row}'] = {
              'text': "private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'K{current_row}'] = {
              'text': "active" if competitor[0]['status'] == "aktiv" else "planning" if competitor[0]['status'] == "in Planung" else "construction",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'L{current_row}'] = {
              'text': '-' if competitor[0]['year_of_construction'] == '-' else competitor[0]['year_of_construction'],
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'M{current_row}'] = {
              'text': competitor[0]['number_apts'],
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'N{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'O{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'P{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'Q{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'R{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'S{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'T{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'U{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }
            market_study_data['pages'][sheet_name]['cell_content']['cells'][f'V{current_row}'] = {
              'text': "-",
              'format': 'row_centered' if not current_row == 25 else 'last_row_centered'
            }

            if not competitor[0]['year_of_construction'] == '-':
              list_years_of_construction_al.append(int(competitor[0]['year_of_construction']))
            if competitor[0]['type'] == 'gemeinnützig':
              none_profit_operator_al += 1
            elif competitor[0]['type'] == 'kommunal':
              public_operator_al += 1
            elif competitor[0]['type'] == 'privat':
              private_operator_al += 1
  
          current_row += 1
      
      # print(invest_costs_public)
      # print(invest_costs_non_profit)
      # print(invest_costs_private)
      
      operator_chart_path = anvil.server.call('chart_test_3', [none_profit_operator_al, public_operator_al, private_operator_al], [none_profit_operator_nh, public_operator_nh, private_operator_nh], unique_code)
      invest_cost_chart_path = anvil.server.call('chart_test_6', invest_plot_data, unique_code)
      purchasing_power_chart_path = anvil.server.call('chart_test_5', purchase_power, unique_code)
      invest_cost_chart_public_path = anvil.server.call('chart_test_4', invest_costs_public, invest_costs_public_home, unique_code, 'public')
      invest_cost_chart_non_profit_path = anvil.server.call('chart_test_4', invest_costs_non_profit, invest_costs_non_profit_home, unique_code, 'non_profit')
      invest_cost_chart_private_path = anvil.server.call('chart_test_4', invest_costs_private, invest_costs_private_home, unique_code, 'private')

      # print(invest_cost_chart_public_path)
      # print(invest_cost_chart_non_profit_path)
      # print(invest_cost_chart_private_path)
      
      max_pages = competitor_analysis_pages[-1] + 4 
      good_to_know_page = competitor_analysis_pages[-1] + 1
      regulations_page = good_to_know_page + 1
      methodic_page = regulations_page + 1
      contact_page = methodic_page + 1
      
      market_study_pages.append("GOOD TO KNOW")
      market_study_pages.append("REGULATIONS")
      market_study_pages.append("METHODIC")
      market_study_pages.append("CONTACT")
      
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['merge_cells']['C4:X5']['text'] = city
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['C12']['text'] = f"Viewing radius: {iso_time} minutes of {movement}"
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['Q12']['text'] = f"Viewing radius: {iso_time} minutes of {movement}"
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['O13']['text'] = len(data_comp_analysis_nh['data'])
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['O14']['text'] = len(data_comp_analysis_al['data'])
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['O15']['text'] = anvil.server.call('get_median', list_beds) if len(list_beds) > 0 else '-'
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['O16']['text'] = anvil.server.call('get_median', list_years_of_construction_nh) if len(list_years_of_construction_nh) > 0 else '-'
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['cells']['O17']['text'] = anvil.server.call('get_median', list_years_of_construction_al) if len(list_years_of_construction_al) > 0 else '-'
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['merge_cells']['Q47:X51']['text'] = f"The investment cost rates of the facilities within the catchment area range between €{minimum_invest_cost} and €{maximum_invest_cost}.  The median investment cost amount to €{'{:.2f}'.format(total_invest_cost)}. {f'The investment costs at the facility, that is subject to this study amounts to €{home_invest}.' if not home_invest == -1 else ''}"
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['images']['A16']['file'] = operator_chart_path
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['images']['P14']['file'] = invest_cost_chart_path
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['images']['A34']['file'] = purchasing_power_chart_path
      cells = [['P27', 'Q32:X32'], ['P34', 'Q39:X39'], ['P40', 'Q43:X43']]
      cell_index = 0
      if not invest_cost_chart_non_profit_path == 404:
        market_study_data['pages']['GOOD TO KNOW']['cell_content']['images'][cells[cell_index][0]] = {
          'file': invest_cost_chart_non_profit_path,
          'settings': {
              'x_scale': .6,
              'y_scale': .6,
              'x_offset': 20,
              'y_offset': 5
          }
        }
        market_study_data['pages']['GOOD TO KNOW']['cell_content']['merge_cells'][cells[cell_index][1]] = {
          'text': "Non Profit",
          'format': "smaller_heading_borderless_center"
        }
        cell_index += 1
      if not invest_cost_chart_public_path == 404:
        market_study_data['pages']['GOOD TO KNOW']['cell_content']['images'][cells[cell_index][0]] = {
          'file': invest_cost_chart_public_path,
          'settings': {
              'x_scale': .6,
              'y_scale': .6,
              'x_offset': 20,
              'y_offset': 5
          }
        }
        market_study_data['pages']['GOOD TO KNOW']['cell_content']['merge_cells'][cells[cell_index][1]] = {
          'text': "Public",
          'format': "smaller_heading_borderless_center"
        }
        cell_index += 1
      if not invest_cost_chart_private_path == 404:
        market_study_data['pages']['GOOD TO KNOW']['cell_content']['images'][cells[cell_index][0]] = {
          'file': invest_cost_chart_private_path,
          'settings': {
              'x_scale': .6,
              'y_scale': .6,
              'x_offset': 20,
              'y_offset': 5
          }
        }
        market_study_data['pages']['GOOD TO KNOW']['cell_content']['merge_cells'][cells[cell_index][1]] = {
          'text': "Private",
          'format': "smaller_heading_borderless_center"
        }
        cell_index += 1
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['C4:X5']['text'] = city
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['C12:X14']['text'] = f"This market study consideres {len(data_comp_analysis_nh['data'])} nursing homes within the vicinity of {iso_time} minutes {movement}. Thereof, {complied_regulations} facilities comply with the federal state regulations and {uncomplied_regulations} facilities that do not fullfill the federal requirements. Assuming that only 80% of the respective facilities need to comply with the below shown federal state regulations, the resulting loss of beds in the market until 2030 will amount to {loss_of_beds}."
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O15:X15']['text'] = regulations['federal_state']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O17:S17']['text'] = f"{int(regulations['New']['sr_quote_raw'] * 100)}%" if not type(regulations['New']['sr_quote_raw']) == str else regulations['New']['sr_quote_raw']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O18:S18']['text'] = regulations['New']['max_beds_raw']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O19:S19']['text'] = regulations['New']['min_room_size']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O20:S20']['text'] = regulations['New']['min_common_area_resident']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O21:S21']['text'] = regulations['New']['comment']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['O22:S22']['text'] = regulations['New']['legal_basis']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['T17:X17']['text'] = f"{int(regulations['Existing']['sr_quote_raw'] * 100)}%" if not type(regulations['Existing']['sr_quote_raw']) == str else regulations['Existing']['sr_quote_raw']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['T18:X18']['text'] = regulations['Existing']['max_beds_raw']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['T19:X19']['text'] = regulations['Existing']['min_room_size']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['T20:X20']['text'] = regulations['Existing']['min_common_area_resident']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['T21:X21']['text'] = regulations['Existing']['comment']
      market_study_data['pages']['REGULATIONS']['cell_content']['merge_cells']['T22:X22']['text'] = regulations['Existing']['legal_basis']

      market_study_data['pages']['SUMMARY']['cell_content']['textboxes']['V1']['text'] = f"{summary_page} | {max_pages}"
      market_study_data['pages']['LOCATION ANALYSIS']['cell_content']['textboxes']['R1']['text'] = f"{location_analysis_page} | {max_pages}"
      market_study_data['pages']['REGULATIONS']['cell_content']['textboxes']['W1']['text'] = f"{regulations_page} | {max_pages}"
      for page in competitor_analysis_pages:
        market_study_data['pages'][f'COMPETITOR ANALYSIS {page - 3}']['cell_content']['textboxes']['V1']['text'] = f"{page} | {max_pages}"
      market_study_data['pages']['GOOD TO KNOW']['cell_content']['textboxes']['X1']['text'] = f"{good_to_know_page} | {max_pages}"
      market_study_data['pages']['METHODIC']['cell_content']['textboxes']['Y1']['text'] = f"{methodic_page} | {max_pages}"
      market_study_data['pages']['CONTACT']['cell_content']['textboxes']['Y1']['text'] = f"{contact_page} | {max_pages}"
        
    ##### Analysis Addition to Market Study #####

      # #####Create Market Study as Excel and PDF#####

      Functions.manipulate_loading_overlay(self, True)
      anvil.js.call('update_loading_bar', 85, 'Creating Market Study as Excel and PDF')

      request_data = self.build_competitor_map_request(coords_nh, Variables.home_address_nh, coords_al, [])
      request_data = self.build_competitor_map_request(request_data['controlling_marker'], Variables.home_address_al, request_data['working_marker'], request_data['request'])
      request = self.build_home_marker_map_request(request_data['controlling_marker']['marker_coords']['lng'], request_data['controlling_marker']['marker_coords']['lat'], request_data['request'])
      anvil.server.call('create_iso_map', Variables.activeIso, Functions.create_bounding_box(self), unique_code)
      anvil.server.call('new_ms_test2', market_study_data, bbox, mapRequestData, unique_code, market_study_pages, request)
      
      # #####Downloading Files#####
      
      anvil.js.call('update_loading_bar', 100, 'Download Files')
        
      #Get PDF from Table and start Download
      table = app_tables.pictures.search()
      mapPDF = app_tables.pictures.search()[0]
      # mapExcel = app_tables.pictures.search()[0]
      anvil.media.download(mapPDF['pic'])
      # time.sleep(1)
      # anvil.media.download(mapExcel['pic'])
      Variables.unique_code = unique_code

      # #####Reset Loading Bar#####
      
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
  
  #Organize Data for Compettior Analysis
  def organize_ca_data(self, entries, topic, marker_coords):
    with anvil.server.no_loading_indicator:
      # Create Variables
      counter = 0
      data_comp_analysis = []
      coords = []
  
      if topic == 'nursing_homes':
        Variables.home_address_nh = []
      else:
        Variables.home_address_al = []

      # res = anvil.js.call('getDeletedMarker')
      for entry in entries:
        added = False
        if topic == "nursing_homes":
          lat_entry = "%.6f" % float(entry['coord_lat'])
          lng_entry = "%.6f" % float(entry['coord_lon'])
        else:
          lat_entry = "%.6f" % float(entry['coord_lat'])
          lng_entry = "%.6f" % float(entry['coord_lon'])
        for icon in Variables.activeIcons[topic]:
          if not added:
            lng_icon = "%.6f" % icon['_lngLat']['lng']
            lat_icon = "%.6f" % icon['_lngLat']['lat']
            if lng_entry == lng_icon and lat_entry == lat_icon:
                coords.append([lng_icon, lat_icon])
                counter += 1
                
                if topic == "nursing_homes":
                  if not entry['anz_vers_pat'] == "-":
                    anz_vers_pat = int(entry['anz_vers_pat'])
                  else:
                    anz_vers_pat = "-"
                    
                  if not entry['platz_voll_pfl'] == "-":
                    platz_voll_pfl = int(entry['platz_voll_pfl'])
                  else:
                    platz_voll_pfl = "-"
                    
                  if not entry['anz_vers_pat'] == "-" and not entry['platz_voll_pfl'] == "-":
                    occupancy_raw = anz_vers_pat / platz_voll_pfl
                    if occupancy_raw > 1:
                      occupancy_raw = 1
                  else:
                    occupancy = "-"
                    occupancy_raw = "-"
                    
                  if not entry['invest'] == "-":
                    if len(entry['invest']) == 4:
                      if entry['invest'].index(".") == 2:
                        invest = entry['invest'] + "0"
                      else:
                        invest = entry['invest']
                    else:
                      invest = entry['invest']
                  else:
                    invest = "-"
                      
                  data = {
                    "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_name": entry['name'],
                    "platz_voll_pfl": platz_voll_pfl,
                    "ez": entry['ez'],
                    "dz": entry['dz'],
                    "anz_vers_pat": anz_vers_pat,
                    "occupancy": occupancy_raw,
                    "baujahr": entry['baujahr'],
                    "status": entry['status'],
                    "betreiber": entry['betreiber'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_betreiber": entry['betreiber'],
                    "invest": invest,
                    "mdk_note": entry['mdk_note'],
                    "coords": [lng_icon, lat_icon],
                    "web": entry['webseite'],
                    "operator_type": entry['art']
                  }
                  data_comp_analysis.append(data)
                  added = True
                elif topic == "assisted_living":
                  data = {
                    "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_name": entry['name'],
                    "operator": entry['betreiber'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_betreiber": entry['betreiber'],
                    "type": entry['art'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_type": entry['art'],
                    "city": entry['ort'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_city": entry['ort'],
                    "status": entry['status'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                    "raw_status": entry['status'],
                    "number_apts": entry['anz_wohnungen'],
                    "coords": [lng_icon, lat_icon],
                    "web": entry['webseite'],
                    "type": entry['art'],
                    "year_of_construction": entry['baujahr']
                  }
                  data_comp_analysis.append(data)
                  added = True

      # Sort Coordinates by Distance
      sorted_coords = anvil.server.call("get_distance", marker_coords, data_comp_analysis)
      from .Market_Study_Existing_Home import Market_Study_Existing_Home
      for entry in sorted_coords:
        if entry[1] <= 0.01:
          res = alert(content=Market_Study_Existing_Home(entry=entry, topic=topic), dismissible=False, large=True, buttons=[], role='custom_alert')
          if res == 'Yes':
            if topic == 'nursing_homes':
              Variables.home_address_nh.append(entry)
            else:
              Variables.home_address_al.append(entry)
        
      if topic == 'nursing_homes':
        if len(Variables.home_address_nh) == 0:
          from .Market_Study_NH_Home import Market_Study_NH_Home
          from .Market_Study_NH_Home_Mobile import Market_Study_NH_Home_Mobile
          if self.mobile:
            Variables.home_address_nh = alert(content=Market_Study_NH_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
          else:
            Variables.home_address_nh = alert(content=Market_Study_NH_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
          if not Variables.home_address_nh == []:
            sorted_coords.insert(0, Variables.home_address_nh)
      else:
        if Variables.home_address_al == []:
          from .Market_Study_AL_Home import Market_Study_AL_Home
          from .Market_Study_AL_Home_Mobile import Market_Study_AL_Home_Mobile
          if self.mobile:
            Variables.home_address_al = alert(content=Market_Study_AL_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
          else:
            Variables.home_address_al = alert(content=Market_Study_AL_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
          if not Variables.home_address_al == []:
            sorted_coords.insert(0, Variables.home_address_al)

      # print(sorted_coords[:30])
      res_data = {'sorted_coords': sorted_coords[:30], 'marker_coords': marker_coords}
      
      return res_data


  def build_competitor_map_request(self, working_marker, home_marker, controlling_marker, request):
    request_static_map_raw = f"%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B"
    request_static_map = request_static_map_raw
    marker_number = 0
    last_coord_dist = 0

    for working_marker_index, working_marker_coordinate in enumerate(working_marker['sorted_coords']):
      if working_marker_coordinate in home_marker:
        working_marker['sorted_coords'][working_marker_index].append('home')
      elif not last_coord_dist == working_marker_coordinate[1]:
        marker_number += 1
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
                  icon = f'Assisted{marker_number}@0.6x.png'
                  controlling_marker['sorted_coords'][controlling_maker_index].append(True)
                  working_marker['sorted_coords'][working_marker_index].append(True)
                  break
        else:
          icon = f'Assisted{marker_number}@0.6x.png'
        url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/{icon}'
        encoded_url = url.replace("/", "%2F")
        if not (working_marker_index + 1) % 20 == 1:
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
  
  def build_req_string(self, res_data, topic):
    with anvil.server.no_loading_indicator:
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
        if complete_counter <= 25:
          if not last_coord_dist == coordinate[1]:
            counter += 1
            url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/Pin{index_coords}x075.png'
            # url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/TestPinx075.png'
            encoded_url = url.replace("/", "%2F")
            if complete_counter == len(res_data['sorted_coords']) - 1:
              if not coordinate[0]['coords'] == last_coords and not 'home' in coordinate:
                if not counter == 1:
                  request_static_map += f"%2C"
                request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D"
              counter = 0
              if not request_static_map == request_static_map_raw:
                request_static_map += f"%2C"
              url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/PinCBx075.png'
              encoded_url = url.replace("/", "%2F")
              request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
              request.append(request_static_map)
              request_static_map = request_static_map_raw
              index_coords -= 1
            elif counter == 10:
              if not 'home' in coordinate:
                if not coordinate[0]['coords'] == last_coords:
                  request_static_map += f"%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D%5D%7D"
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
                request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D"
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
        url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/PinCBx075.png'
        encoded_url = url.replace("/", "%2F")
        request_static_map = request_static_map_raw + f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
        request.append(request_static_map)
        request_static_map = request_static_map_raw
      
      return({"data": res_data['sorted_coords'], "request": request, "request2": Variables.activeIso})
  
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
      if mode == 'click':
        Functions.manipulate_loading_overlay(self, True)
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

      Functions.manipulate_loading_overlay(self, False)
      from .Name_Share_Link import Name_Share_Link
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
  
        Functions.manipulate_loading_overlay(self, False)
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
