# Import of different Modules
from ._anvil_designer import Map2_0Template
from anvil import *
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
from anvil.tables import app_tables
from anvil.js.window import mapboxgl, MapboxGeocoder, document
from .. import Variables, Layer, Images, ExcelFrames, Functions
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
import functools
import Market_Study_Functions

global Variables, Layer, Images, ExcelFrames

class Map2_0(Map2_0Template):

  def __init__(self, **properties):
    with anvil.server.no_loading_indicator:
      Functions.get_mapbox_token()
      
      if Variables.maintenance and not Variables.user_role == "admin":
        Functions.manipulate_loading_overlay(False)
        from .Maintenance import Maintenance
        alert(content=Maintenance(), dismissible=False, buttons=[], large=True)
      else:
        Functions.manipulate_loading_overlay(False)
        self.init_components(**properties)
        self.dom = anvil.js.get_dom_node(self.spacer_1)
        self.time_dropdown.items = [("5 minutes", "5"), ("10 minutes", "10"), ("15 minutes", "15"), ("20 minutes", "20"), ("30 minutes", "30"), ("60 minutes", "60"), ("5 minutes layers", "-1")]
        Variables.app_url = anvil.server.call_s('get_app_url')
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
      try:
        width, height = anvil.js.call('get_screen_width')
        print(Variables.user_role)
        if Variables.user_role == 'guest':
          marker_draggable = False
        #   self.button_icons.text = 'Cluster & Investment'
        else:
            self.dist_layer.visible = True
            self.poi_categories.visible = True
            self.button_overlay.visible = True
            self.hide_ms_marker.visible = True
            # self.competitor_btn.visible = True
            self.file_loader_upload.visible = True
            self.distance_circles.visible = True
            self.share.visible = True
            self.button_icons.visible = True
            marker_draggable = True
            if Variables.user_role == 'admin':
              self.admin_button.visible = True
              self.db_upload.visible = True
              self.mapbox_token.visible = True
  
        if width <= 998:
          self.mobile = True
          self.mobile_btn_grid.visible = True
          self.mobile_menu_open = False
        else:
          self.mobile = False
          if Variables.user_role == 'guest':
            container = document.getElementById('appGoesHere')
            logo = document.createElement('img')
            logo.src = f'{Variables.app_url}/_/theme/Logo.png'
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
        self.select_all_micro_living.tag.categorie = 'Micro Living'
        
        mapboxgl.accessToken = Variables.mapbox_token
        self.mapbox = mapboxgl.Map({'container': self.dom,
                                    'style': "mapbox://styles/mapbox/light-v11",
                                    'center': [13.4092, 52.5167],
                                    'zoom': 8})
  
        self.marker = mapboxgl.Marker({'draggable': marker_draggable, 'element': Functions.create_marker_div(), 'anchor': 'bottom'}).setLngLat([13.4092, 52.5167]).addTo(self.mapbox)
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
      except:
        pass

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
      Functions.manipulate_loading_overlay(True)
      # Check or uncheck various Check Boxes for different POI Categories
      if dict(event_args)['sender'].text == "Veterinary":
        Variables.last_bbox_vet, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
      elif dict(event_args)['sender'].text == "Social Facility":
        Variables.last_bbox_soc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
      elif dict(event_args)['sender'].text == "Pharmacy":
        Variables.last_bbox_pha, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
      elif dict(event_args)['sender'].text == "Hospital":
        Variables.last_bbox_hos, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
      elif dict(event_args)['sender'].text == "Clinic":
        Variables.last_bbox_cli, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
      elif dict(event_args)['sender'].text == "Dentist":
        Variables.last_bbox_den, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
      elif dict(event_args)['sender'].text == "Doctor":
        Variables.last_bbox_doc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)      
      elif dict(event_args)['sender'].text == "Nursing School":
        Variables.last_bbox_nsc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools) 
      elif dict(event_args)['sender'].text == "Supermarket":
        Variables.last_bbox_sma, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
      elif dict(event_args)['sender'].text == "Restaurant":
        Variables.last_bbox_res, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
      elif dict(event_args)['sender'].text == "Cafe":
        Variables.last_bbox_caf, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
      elif dict(event_args)['sender'].text == "University":
        Variables.last_bbox_uni, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
      elif dict(event_args)['sender'].text == "Bus Stop":
        Variables.last_bbox_bus, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
      elif dict(event_args)['sender'].text == "Tram Stop":
        Variables.last_bbox_tra, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
      elif dict(event_args)['sender'].text == "Nursing Home":
        Variables.last_bbox_nh, minimum_average_rent, maximum_average_rent = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
      elif dict(event_args)['sender'].text == "Assisted Living":
        Variables.last_bbox_al, minimum_average_rent, maximum_average_rent = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
      elif dict(event_args)['sender'].text == "Podiatrist":
        Variables.last_bbox_pdt, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_pdt.checked, Variables.last_bbox_pdt, "podiatrist", Variables.icon_podiatrist)
      elif dict(event_args)['sender'].text == "Hairdresser":
        Variables.last_bbox_hd, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_hd.checked, Variables.last_bbox_hd, "hairdresser", Variables.icon_hairdresser)
      elif event_args['sender'].text == "S-Bahn/U-Bahn":
        Variables.last_bbox_al, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_su.checked, Variables.last_bbox_su, "subway", f'{Variables.app_url}/_/theme/Pins/U_Bahn_Pin.png')
      elif event_args['sender'].text == "Airport":
        Variables.last_bbox_ap, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_ap.checked, Variables.last_bbox_ap, "aerodrome", f'{Variables.app_url}/_/theme/Pins/Flughafen_Pin.png')
      elif event_args['sender'].text == "Business Living":
        Variables.last_bbox_bl, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_bl.checked, Variables.last_bbox_bl, "business_living", f'{Variables.app_url}/_/theme/Pins/BusinessLiving@0.75x.png')
        self.slider_maximum.enabled = True
        self.slider_minimum.enabled = True
        if self.slider_minimum.text is None or minimum_average_rent < self.micro_living_rent_slider.min:
          # self.slider_minimum.text = minimum_average_rent
          self.micro_living_rent_slider.min = float(minimum_average_rent)
        if self.slider_maximum.text is None or maximum_average_rent > self.micro_living_rent_slider.max:
          # self.slider_maximum.text = maximum_average_rent
          self.micro_living_rent_slider.max = float(maximum_average_rent)
        self.micro_living_rent_slider.enabled = True
        # self.micro_living_rent_slider.values = float(minimum_average_rent), float(maximum_average_rent)
      elif event_args['sender'].text == "Co-living":
        Variables.last_bbox_cl, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cl.checked, Variables.last_bbox_cl, "co_living", f'{Variables.app_url}/_/theme/Pins/CoLiving@0.75x.png')
        self.slider_maximum.enabled = True
        self.slider_minimum.enabled = True
        if self.slider_minimum.text is None or float(minimum_average_rent) < self.micro_living_rent_slider.min:
          # self.slider_minimum.text = minimum_average_rent
          self.micro_living_rent_slider.min = float(minimum_average_rent)
        if self.slider_maximum.text is None or float(maximum_average_rent) > self.micro_living_rent_slider.max:
          # self.slider_maximum.text = maximum_average_rent
          self.micro_living_rent_slider.max = float(maximum_average_rent)
        self.micro_living_rent_slider.enabled = True
        # self.micro_living_rent_slider.values = float(minimum_average_rent), float(maximum_average_rent)
      elif event_args['sender'].text == "Serviced Living":
        Variables.last_bbox_sl, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_sl.checked, Variables.last_bbox_sl, "service_living", f'{Variables.app_url}/_/theme/Pins/ServiceLiving@0.75x.png')
        self.slider_maximum.enabled = True
        self.slider_minimum.enabled = True
        if self.slider_minimum.text is None or float(minimum_average_rent) < self.micro_living_rent_slider.min:
          # self.slider_minimum.text = minimum_average_rent
          self.micro_living_rent_slider.min = float(minimum_average_rent)
        if self.slider_maximum.text is None or float(maximum_average_rent) > self.micro_living_rent_slider.max:
          # self.slider_maximum.text = maximum_average_rent
          self.micro_living_rent_slider.max = float(maximum_average_rent)
        self.micro_living_rent_slider.enabled = True
        # self.micro_living_rent_slider.values = float(minimum_average_rent), float(maximum_average_rent)
      elif event_args['sender'].text == "Student Living":
        Variables.last_bbox_stl, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_stl.checked, Variables.last_bbox_stl, "student_living", f'{Variables.app_url}/_/theme/Pins/StudentLiving@0.75x.png')
        self.slider_maximum.enabled = True
        self.slider_minimum.enabled = True
        if self.slider_minimum.text is None or float(minimum_average_rent) < self.micro_living_rent_slider.min:
          # self.slider_minimum.text = minimum_average_rent
          self.micro_living_rent_slider.min = float(minimum_average_rent)
        if self.slider_maximum.text is None or float(maximum_average_rent) > self.micro_living_rent_slider.max:
          # self.slider_maximum.text = maximum_average_rent
          self.micro_living_rent_slider.max = float(maximum_average_rent)
        self.micro_living_rent_slider.enabled = True
        # self.micro_living_rent_slider.values = float(minimum_average_rent), float(maximum_average_rent)
      Functions.manipulate_loading_overlay(False)

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
        self.check_light.checked = False
        self.check_basic.checked = False
        self.mapbox.setStyle('mapbox://styles/mapbox/satellite-streets-v11')
      elif dict(event_args)['sender'].text == "Street Map":
        self.check_satellite.checked = False
        self.check_light.checked = False
        self.check_basic.checked = False
        self.mapbox.setStyle('mapbox://styles/mapbox/outdoors-v11')
      elif dict(event_args)['sender'].text == "Light Map":
        self.check_street.checked = False
        self.check_satellite.checked = False
        self.check_basic.checked = False
        self.mapbox.setStyle('mapbox://styles/mapbox/light-v11')
      elif dict(event_args)['sender'].text == "Basic Map":
        self.check_street.checked = False
        self.check_satellite.checked = False
        self.check_light.checked = False
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
        },
        'Micro Living': {
          'container': self.micro_living_grid,
          'icon_container': self.micro_living_btn
        },
        'Distance Circles': {
          'container': self.distance_circles_view,
          'icon_container': self.distance_circles
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
      Functions.manipulate_loading_overlay(True)
      date = datetime.datetime.now()
      # anvil.server.call('micmaccircle')
      # anvil.server.call('manipulate')
      # anvil.server.call('save_micro_living')

      self.mapbox.addSource("radius", self.createGeoJSONCircle([13.4092, 52.5167], 50));
      
      self.mapbox.addLayer({
        "id": "radius",
        "type": "fill",
        "source": "radius",
        "layout": {},
        "paint": {
            "fill-color": "rgba(0, 0, 0, 0)",
            "fill-outline-color": "blue",
            "fill-opacity": 0.6
        }
      })
      
      print('Ready')
      Functions.manipulate_loading_overlay(False)

  #######Noch bearbeiten#######[]

  def create_market_study(self, **event_args):
    with anvil.server.no_loading_indicator:
      if Variables.user_role == 'admin':
        print(datetime.datetime.now())

      Functions.manipulate_loading_overlay(True)
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
      request = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{marker_coords['lng']},{marker_coords['lat']}.json?access_token={Variables.mapbox_token}"
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
      Functions.manipulate_loading_overlay(False)
      analysis_text = alert(ChatGPT(generated_text=analysis_text), buttons=[], dismissible=False, large=True, role='custom_alert')
      Functions.manipulate_loading_overlay(True)
      
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
              inpatients_lk += int(el['anz_vers_pat']) if el['anz_vers_pat'] is not None else 0
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
      inpatients_fc = round(pat_rec_full_care_fc_30_v1 * (round(((inpatients * 100) / inpatients_lk), 1) / 100)) if not inpatients_lk == 0 else 0 
      inpatients_fc_v2 = round(pat_rec_full_care_fc_30_v2 * (round(((inpatients * 100) / inpatients_lk), 1) / 100)) if not inpatients_lk == 0 else 0
      inpatients_fc_35 = round(pat_rec_full_care_fc_35_v1 * (round(((inpatients * 100) / inpatients_lk), 1) / 100)) if not inpatients_lk == 0 else 0
      inpatients_fc_35_v2 = round(pat_rec_full_care_fc_35_v2 * (round(((inpatients * 100) / inpatients_lk), 1) / 100)) if not inpatients_lk == 0 else 0
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
              if not competitor[0]['mdk_note'] == '-' and competitor[0]['mdk_note'] is not None:
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
                  'txt': '{:,}'.format(beds) if not beds == '-' else beds,
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
                  'txt': '-' if competitor[0]['mdk_note'] == '-' else '-' if competitor[0]['mdk_note'] is None else '{:,}'.format(float(competitor[0]['mdk_note'])),
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

      from . import Market_Study_Skeleton
      market_study_data = Market_Study_Skeleton.market_study_skeleton({
        'street': street,
        'zipcode': zipcode,
        'city': city,
        'district': district,
        'federal_state': federal_state,
        'iso_time': iso_time,
        'iso_movement': iso_movement,
        'created_date': created_date,
        'purchase_power': purchase_power,
        'population_trend': population_trend,
        'beds_surplus_35_v2': beds_surplus_35_v2,
        'countie': countie[0],
        'population_city_2020': countie_data['dem_city']['bevoelkerung_ges'],
        'population_county_2020': countie_data['ex_dem_lk']['all_compl'],
        'people_u80': people_u80,
        'people_o80': people_o80,
        'new_care_rate_raw': new_care_rate_raw,
        'nursing_home_rate': nursing_home_rate,
        'inpatients_lk': inpatients_lk,
        'occupancy_lk': occupancy_lk,
        'beds_lk': beds_lk,
        'free_beds_lk': free_beds_lk,
        'nursing_homes_active': nursing_homes_active,
        'beds_active': beds_active,
        'nursing_homes_planned': nursing_homes_planned,
        'nursing_homes_construct': nursing_homes_construct,
        'beds_planned': beds_planned,
        'beds_construct': beds_construct,
        'beds_active': beds_active,
        'inpatients': inpatients,
        'population_fc_30': population_fc_30,
        'people_u80_fc': people_u80_fc,
        'people_o80_fc': people_o80_fc,
        'care_rate_30_v1_raw': care_rate_30_v1_raw,
        'pat_rec_full_care_fc_30_v1': pat_rec_full_care_fc_30_v1,
        'beds_30_v1': beds_30_v1,
        'free_beds_30_v1': free_beds_30_v1,
        'loss_of_beds': loss_of_beds,
        'beds_adjusted_30_v1': beds_adjusted_30_v1,
        'inpatients_fc': inpatients_fc,
        'beds_surplus': beds_surplus,
        'care_rate_30_v2_raw': care_rate_30_v2_raw,
        'pat_rec_full_care_fc_30_v2': pat_rec_full_care_fc_30_v2,
        'beds_30_v2': beds_30_v2,
        'free_beds_30_v2': free_beds_30_v2,
        'beds_adjusted_30_v2': beds_adjusted_30_v2,
        'inpatients_fc_v2': inpatients_fc_v2,
        'beds_surplus_v2': beds_surplus_v2,
        'population_fc_35': population_fc_35,
        'people_u80_fc_35': people_u80_fc_35,
        'people_o80_fc_35': people_o80_fc_35,
        'care_rate_35_v1_raw': care_rate_35_v1_raw,
        'pat_rec_full_care_fc_35_v1': pat_rec_full_care_fc_35_v1,
        'beds_35_v1': beds_35_v1,
        'free_beds_35_v1': free_beds_35_v1,
        'beds_adjusted_35_v1': beds_adjusted_35_v1,
        'inpatients_fc_35': inpatients_fc_35,
        'beds_surplus_35': beds_surplus_35,
        'care_rate_35_v2_raw': care_rate_35_v2_raw,
        'pat_rec_full_care_fc_35_v2': pat_rec_full_care_fc_35_v2,
        'beds_35_v2': beds_35_v2,
        'free_beds_35_v2': free_beds_35_v2,
        'beds_adjusted_35_v2': beds_adjusted_35_v2,
        'inpatients_fc_35_v2': inpatients_fc_35_v2,
        'analysis_text': analysis_text,
        'number_facilities_nh_value': len(data_comp_analysis_nh['data']),
        'number_facilities_al_value': len(data_comp_analysis_al['data']),
        'minimum_invest_cost': minimum_invest_cost,
        'maximum_invest_cost': maximum_invest_cost,
        'total_invest_cost': total_invest_cost,
        'home_invest': home_invest,
        'regulations': regulations,
        'complied_regulations': complied_regulations,
        'uncomplied_regulations': uncomplied_regulations,
        'share_url': share_url,
        'analysis_text': analysis_text
      })
      
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
      market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_value']['txt'] = str(int(good_to_know_median['years_of_construction_nh'])) if not good_to_know_median['years_of_construction_nh'] == '-' else good_to_know_median['years_of_construction_nh']
      market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_al_value']['txt'] = str(int(good_to_know_median['years_of_construction_al'])) if not good_to_know_median['years_of_construction_al'] == '-' else good_to_know_median['years_of_construction_al']
      
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
      Functions.manipulate_loading_overlay(False)
  
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
      Functions.manipulate_loading_overlay(True)
      anvil.js.call('update_loading_bar', 5, 'Reading Excel File')
      #Call Server-Function to safe the File  
      self.cluster_data = anvil.server.call('save_local_excel_file', file)
      if self.cluster_data == None:
        Functions.manipulate_loading_overlay(False)
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
          req_str += f'.json?access_token={Variables.mapbox_token}'
          coords = anvil.http.request(req_str,json=True)
          for entry in coords['features']:
            if asset['zip'] in entry['place_name']:
              coordinates = entry['geometry']['coordinates']
              break
          if not cluster_name in excel_markers.keys():
            excel_markers[cluster_name] = {'color': color, 'static': 'none', 'marker': []}
          el.style.backgroundImage = f'url({Variables.app_url}{excel_markers[cluster_name]["color"][2]})'
          new_list = self.set_excel_markers(excel_markers[cluster_name]['static'], coordinates, excel_markers[cluster_name]['marker'], el, asset)
          excel_markers[cluster_name]['marker'] = new_list
          if not invest_name in excel_markers.keys():
            excel_markers[invest_name] = {'pin': invests[invest_name], 'static': 'none', 'marker': []}
          inv_el.style.backgroundImage = f"url({Variables.app_url}{invests[invest_name]})"
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
        Functions.manipulate_loading_overlay(False)
        anvil.js.call('update_loading_bar', 0, '')

  # This Function is called when a DB Update should be done
  def db_upload_change(self, file, **event_args):
    try:
      splitted_file_name = file.name.split(' ')
      if 'Betreutes' in splitted_file_name:
        anvil.server.call('write_caredb_bw', file)
      elif 'Pflegeheime' in splitted_file_name:
        anvil.server.call('write_caredb_care', file)
      else:
        print('Uploaded incorrect File')
    finally:
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
      request_string += f"&polygons=true&access_token={Variables.mapbox_token}"
      
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
      
      layers = [
        {
          'id_fill': 'federal_states',
          'id_outline': 'outline_federal_states', 
          'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/1_sehr_hoch.geo.json',
          'line_width': .25
        }, 
        {
          'id_fill': 'administrative_districts',
          'id_outline': 'outline_administrative_districts', 
          'data': 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/3_regierungsbezirke/1_sehr_hoch.geo.json',
          'line_width': .25
        },
        {
          'id_fill': 'counties',
          'id_outline': 'outline_counties', 
          'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/landkreise.geojson',
          'line_width': .25
        },
        {
          'id_fill': 'municipalities',
          'id_outline': 'outline_municipalities', 
          'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/municipalities.geojson',
          'line_width': .25
        },
        {
          'id_fill': 'districts',
          'id_outline': 'outline_districts', 
          'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/bln_hh_mun_dist.geojson',
          'line_width': .25
        },
        {
          'id_fill': 'netherlands',
          'id_outline': 'outline_netherlands', 
          'data': 'https://raw.githubusercontent.com/CBKLehmann/Geodata/main/netherlands.geojson',
          'line_width': .25
        }
      ]
      
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
      minimum_average_rent = 0
      maximum_average_rent = 100
      
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
          bbox = [self.mapbox.getBounds()['_sw']['lat'], self.mapbox.getBounds()['_sw']['lng'],
                  self.mapbox.getBounds()['_ne']['lat'], self.mapbox.getBounds()['_ne']['lng']]

        # Check if Bounding Box is not the same as least Request
        if not bbox == last_bbox:
          # Check if new Bounding Box is overlapping old Bounding Box
          if bbox[0] < last_bbox[0] or bbox[1] < last_bbox[1] or bbox[2] > last_bbox[2] or bbox[3] > last_bbox[3]:
      
            minimum_average_rent, maximum_average_rent = Functions.create_marker(self, check_box, last_bbox, category, picture, bbox, marker_coords, mapboxgl)
            Variables.average_rents[category] = [minimum_average_rent, maximum_average_rent]
      
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

        elif category in Variables.micro_living_categories:
          if self.check_box_bl.checked:
            minimum_average_rent = Variables.average_rents['business_living'][0] if self.slider_minimum.text is None else Variables.average_rents['business_living'][0] if float(Variables.average_rents['business_living'][0]) < self.slider_minimum.text else self.slider_minimum.text
            maximum_average_rent = Variables.average_rents['business_living'][1] if self.slider_maximum.text is None else Variables.average_rents['business_living'][0] if float(Variables.average_rents['business_living'][1]) > self.slider_maximum.text else self.slider_maximum.text
          if self.check_box_cl.checked:
            minimum_average_rent = Variables.average_rents['co_living'][0] if self.slider_minimum.text is None else Variables.average_rents['co_living'][0] if float(Variables.average_rents['co_living'][0]) < self.slider_minimum.text else self.slider_minimum.text
            maximum_average_rent = Variables.average_rents['co_living'][1] if self.slider_maximum.text is None else Variables.average_rents['co_living'][0] if float(Variables.average_rents['co_living'][1]) > self.slider_maximum.text else self.slider_maximum.text
          if self.check_box_sl.checked:
            minimum_average_rent = Variables.average_rents['service_living'][0] if self.slider_minimum.text is None else Variables.average_rents['service_living'][0] if float(Variables.average_rents['service_living'][0]) < self.slider_minimum.text else self.slider_minimum.text
            maximum_average_rent = Variables.average_rents['service_living'][1] if self.slider_maximum.text is None else Variables.average_rents['service_living'][0] if float(Variables.average_rents['service_living'][1]) > self.slider_maximum.text else self.slider_maximum.text
          if self.check_box_stl.checked:
            minimum_average_rent = Variables.average_rents['student_living'][0] if self.slider_minimum.text is None else Variables.average_rents['student_living'][0] if float(Variables.average_rents['student_living'][0]) < self.slider_minimum.text else self.slider_minimum.text
            maximum_average_rent = Variables.average_rents['student_living'][1] if self.slider_maximum.text is None else Variables.average_rents['student_living'][0] if float(Variables.average_rents['student_living'][1]) > self.slider_maximum.text else self.slider_maximum.text
        
        # Loop through every Element in global Icon-Elements
        for el in Variables.icons[f'{category}']:
          
          # Remove Element from Map
          el.remove()
      
      # Send Value back to origin Function
      return last_bbox, minimum_average_rent, maximum_average_rent
      
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
        Variables.last_bbox_vet, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
        Variables.last_bbox_vet, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
      elif checkbox == "Social facility" and self.check_box_soc.checked == True:
        Variables.last_bbox_soc, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_soc, "social_facility", Variables.icon_social)  
        Variables.last_bbox_soc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
      elif checkbox == "Pharmacy" and self.check_box_pha.checked == True:
        Variables.last_bbox_pha, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
        Variables.last_bbox_pha, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
      elif checkbox == "Hospital" and self.check_box_hos.checked == True:
        Variables.last_bbox_hos, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
        Variables.last_bbox_hos, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
      elif checkbox == "Clinic" and self.check_box_cli.checked == True:
        Variables.last_bbox_cli, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
        Variables.last_bbox_cli, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
      elif checkbox == "Dentist" and self.check_box_den.checked == True:
        Variables.last_bbox_den, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_den, "dentist", Variables.icon_dentist) 
        Variables.last_bbox_den, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
      elif checkbox == "Doctors" and self.check_box_doc.checked == True:
        Variables.last_bbox_doc, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)
        Variables.last_bbox_doc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)
      elif checkbox == "Nursing School" and self.check_box_nsc.checked == True:
        Variables.last_bbox_nsc, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools)
        Variables.last_bbox_nsc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools)    
      elif checkbox == "Supermarket" and self.check_box_sma.checked == True:
        Variables.last_bbox_sma, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
        Variables.last_bbox_sma, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
      elif checkbox == "Restaurant" and self.check_box_res.checked == True:
        Variables.last_bbox_res, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant) 
        Variables.last_bbox_res, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
      elif checkbox == "Cafe" and self.check_box_cafe.checked == True:
        Variables.last_bbox_caf, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
        Variables.last_bbox_caf, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
      elif checkbox == "University" and self.check_box_uni.checked == True:
        Variables.last_bbox_uni, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_uni, "university", Variables.icon_university) 
        Variables.last_bbox_uni, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
      elif checkbox == "Bus Stop" and self.check_box_bus.checked == True:
        Variables.last_bbox_bus, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)
        Variables.last_bbox_bus, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
      elif checkbox == "Tram Stop" and self.check_box_tra.checked == True:
        Variables.last_bbox_tra, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
        Variables.last_bbox_tra, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
      elif checkbox == "Nursing Home" and self.pdb_data_cb.checked == True:
        Variables.last_bbox_nh, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
        Variables.last_bbox_nh, minimum_average_rent, maximum_average_rent = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
      elif checkbox == "Assisted Living" and self.pdb_data_al.checked == True:
        Variables.last_bbox_al, minimum_average_rent, maximum_average_rent = self.create_icons(False, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
        Variables.last_bbox_al, minimum_average_rent, maximum_average_rent = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)

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
      elif event_args['sender'].tag.categorie == 'Micro Living':
        for component in self.micro_living_check_boxes.get_components():
          if not component == event_args['sender']:
            component.checked = event_args['sender'].checked
            component.raise_event('change')

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
      Functions.manipulate_loading_overlay(True)
      from .Change_Cluster_Color import Change_Cluster_Color
      Functions.manipulate_loading_overlay(False)
      response = alert(content=Change_Cluster_Color(components=self.icon_grid.get_components(), mobile=self.mobile), dismissible=False, large=True, buttons=[], role='custom_alert')
      Functions.manipulate_loading_overlay(True)
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
        Functions.manipulate_loading_overlay(False)
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
        inv_el.style.backgroundImage = f"url({Variables.app_url}{invests[invest_name]})"
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
        Functions.manipulate_loading_overlay(True)
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
      Functions.manipulate_loading_overlay(False)
      name = alert(content=Name_Share_Link(searched_address=changed_address), buttons=[], dismissible=False, large=True, role='custom_alert')
      Functions.manipulate_loading_overlay(True)
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
  
        Functions.manipulate_loading_overlay(False)
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
    marker_data = alert(Custom_Marker(url=Variables.app_url), buttons=[], dismissible=False, large=True, role='custom_alert')
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
      Functions.manipulate_loading_overlay(True)
      anvil.js.call('update_loading_bar', 5, 'Reading Excel File')
      #Call Server-Function to safe the File  
      marker_coords = [self.marker['_lngLat']['lng'], self.marker['_lngLat']['lat']]
      comps = anvil.server.call('read_comp_file', file, marker_coords)
      if comps == None:
        Functions.manipulate_loading_overlay(False)
        anvil.js.call('update_loading_bar', 100, 'Error while processing Excel File')
        alert('Irgendwas ist schief gelaufen. Bitte Datei neu hochladen!')
        anvil.js.call('update_loading_bar', 0, '')
        self.file_loader_upload.clear()
      else:
        for marker in self.comp_marker:
          marker.remove()
        self.comp_marker = []
        Functions.manipulate_loading_overlay(False)
        anvil.js.call('update_loading_bar', 50, 'Waiting for Competitor Selection')
        from .Comp_Sort import Comp_Sort
        results = alert(Comp_Sort(data=comps, marker_coords=marker_coords), buttons=[], dismissible=False, large=True, role='custom_alert')
        Functions.manipulate_loading_overlay(True)
        anvil.js.call('update_loading_bar', 80, 'Creating Marker')
        self.create_comp_marker(results)
        self.competitors = results
        anvil.js.call('update_loading_bar', 100, 'Finishing Process')
        Functions.manipulate_loading_overlay(False)
        self.download_comps.visible = True
        anvil.js.call('update_loading_bar', 0, '')
      self.comp_loader.clear()

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
    
        el.style.backgroundImage = f"url({Variables.app_url}/_/theme/Pins/Comp{index+1}.png)"

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
        if not Variables.user_role == 'guest':
          details += "<div class='rmv_container'><button id='remove' class='btn btn-default'>Remove Marker</button></div>"

        anvil.js.call('addHoverEffect', newiconElement, popup, self.mapbox, newicon, result, 'Competitor', details, Variables.user_role)
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
    if Variables.user_role == 'guest':
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

  def micro_living_rent_slider_slide(self, handle, **event_args):
    if handle == 0:
      self.slider_minimum.text = self.micro_living_rent_slider.formatted_values[handle]
    else:
      self.slider_maximum.text = self.micro_living_rent_slider.formatted_values[handle]

  def slider_textbox_change(self, **event_args):
    self.micro_living_rent_slider.values = self.slider_minimum.text, self.slider_maximum.text

  def slider_textbox_pressed_enter(self, **event_args):
    pass

  def micro_living_rent_slider_change(self, handle, **event_args):
    pass

  def export_comparables_click(self, **event_args):
    ''' Investobjekt auf jeder Seite anzeigen '''
    Variables.unique_code = anvil.server.call("get_unique_code")
    checked_boxes = []
    columns = ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
    marker_coords = [self.marker['_lngLat']['lng'], self.marker['_lngLat']['lat']]
    for checkbox in self.micro_living_check_boxes.get_components():
      if checkbox.checked:
        if checkbox.text == "Business Living":
          checked_boxes.append(('business_living', 'Business Living'))
        elif checkbox.text == "Co-living":
          checked_boxes.append(('co_living', 'Co-living'))
        elif checkbox.text == "Serviced Living":
          checked_boxes.append(('service_living', 'Serviced Living'))
        elif checkbox.text == "Student Living":
          checked_boxes.append(('student_living', 'Student Living'))
    for category, page_name in checked_boxes:
      micro_living_comparables = copy.deepcopy(ExcelFrames.micro_living_comparables)
      sorted_entries = {}
      distances = {}
      page_entries = []
      page_order = []
      requests = []
      bounding_box = [1000000, 1000000, 0, 0]
      no_number_marker = 0
      no_number_map_marker = 0
      page_id = 0
      last_coord_dist = -1
      for entry in Variables.micro_living_entries[category]:
        if float(entry['longitude']) < bounding_box[0]:
          bounding_box[0] = float(entry['longitude'])
        if float(entry['longitude']) > bounding_box[2]:
          bounding_box[2] = float(entry['longitude'])
        if float(entry['latitude']) < bounding_box[1]:
          bounding_box[1] = float(entry['latitude'])
        if float(entry['latitude']) > bounding_box[3]:
          bounding_box[3] = float(entry['latitude'])
        el_coords = [entry['longitude'], entry['latitude']]
        distance = anvil.server.call('get_point_distance', marker_coords, el_coords)
        entry['distance'] = distance
      sorted_entries = sorted(Variables.micro_living_entries[category], key=lambda x: x['distance'])
      for index, entry in enumerate(sorted_entries):
        if index % 10 == 0:
          if not page_id == 0:
            request, no_number_map_marker = self.build_micro_living_competitor_map_request(page_entries, page_id, no_number_map_marker)
            micro_living_comparables_current_page['cell_content']['images']['B7']['file'] = f'tmp/map_image_{page_id}_{Variables.unique_code}.png'
            micro_living_comparables['pages'][f'Competitors De {page_id}'] = micro_living_comparables_current_page
            page_order.append(f'Competitors De {page_id}')  
            requests.append((request, f'map_image_{page_id}_{Variables.unique_code}'))
          if 'Ger' in event_args['sender'].text:
            micro_living_comparables_current_page = copy.deepcopy(ExcelFrames.micro_living_comparables_page_de)
          elif 'Eng' in event_args['sender'].text:
            micro_living_comparables_current_page = copy.deepcopy(ExcelFrames.micro_living_comparables_page_en)
          micro_living_comparables_current_page['cell_content']['merge_cells']['B3:K4']['text'] = entry['city']
          micro_living_comparables_current_page['cell_content']['merge_cells']['B5:K6']['text'] = page_name
          column_id = 0
          page_id += 1
          marker_number = 10 * page_id - 10
          page_entries = []

        page_entries.append(entry)
        
        if entry['all_in_rent_from'] is not None:
            all_in_rent_from = entry['all_in_rent_from']
            if entry['all_in_rent_up_to'] is not None:
              all_in_rent_up_to = entry['all_in_rent_up_to']
              average_rent_per_apartment = round((all_in_rent_from + all_in_rent_up_to) / 2, 0)
            else:
              all_in_rent_up_to = '-'
              average_rent_per_apartment = all_in_rent_up_to
        else:
          all_in_rent_from = '-'
          if entry['all_in_rent_up_to'] is not None:
            all_in_rent_up_to = entry['all_in_rent_up_to']
            average_rent_per_apartment = all_in_rent_up_to
          else:
            all_in_rent_up_to = '-'
            average_rent_per_apartment = '-'

        if entry['apartment_size_from'] is not None:
          apartment_size_from = entry['apartment_size_from']
          if entry['apartment_size_up_to'] is not None:
            apartment_size_up_to = entry['apartment_size_up_to']
            average_squaremeters_per_apartment = round((apartment_size_from + apartment_size_up_to) / 2, 2)
          else:
            apartment_size_up_to = '-'
            average_squaremeters_per_apartment = apartment_size_from
        else:
          apartment_size_from = '-'
          if entry['apartment_size_up_to'] is not None:
            apartment_size_up_to = entry['apartment_size_up_to']
            average_squaremeters_per_apartment = apartment_size_up_to
          else:
            apartment_size_up_to = '-'
            average_squaremeters_per_apartment = '-'

        if not average_rent_per_apartment == '-':
          if not average_squaremeters_per_apartment == '-':
            average_rent_per_squaremeter = round(average_rent_per_apartment / average_squaremeters_per_apartment, 2)
          else:
            average_rent_per_squaremeter = average_rent_per_apartment
        else:
          average_rent_per_squaremeter = '-'

        if not entry['distance'] == last_coord_dist:
          marker_number += 1
          icon = f'img/locator.png'
          no_number_marker += 1
          if not entry['distance'] == 0:
            if entry['is_360_operator']:
              icon = f'img/360_operator@0.5x.png'
            else:
              no_number_marker -= 1
              icon = f'img/micro_living_{marker_number - no_number_marker}@0.5x.png'

        if not icon == f'img/locator.png':
          micro_living_comparables_current_page['cell_content']['images'][f'{columns[column_id]}29'] = {
            'file': icon,
            'settings': {
                'y_offset': 0,
                'x_offset': 42,
                'y_scale': .45,
                'x_scale': .45
            }
          }
        else:
          micro_living_comparables_current_page['cell_content']['images'][f'{columns[column_id]}29'] = {
            'file': icon,
            'settings': {
                'y_offset': 0,
                'x_offset': 42
            }
          }
        
        if entry['distance'] == 0:
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}31'] = {
            'text': entry['operator'],
            'format': 'bold_investment_fs8_underline'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}32'] = {
            'text': f"{entry['street']}, {entry['postcode']} {entry['city']}",
            'format': 'bold_investment_fs8_wrap_vcenter'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}33'] = {
            'text': entry['number_of_apartments'] if entry['number_of_apartments'] is not None else '-',
            'format': 'regular_investment_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}34'] = {
            'text': all_in_rent_from,
            'format': 'regular_investment_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}35'] = {
            'text': all_in_rent_up_to,
            'format': 'regular_investment_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}36'] = {
            'text': average_rent_per_apartment,
            'format': 'regular_investment_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}37'] = {
            'text': apartment_size_from,
            'format': 'regular_investment_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}38'] = {
            'text': apartment_size_up_to,
            'format': 'regular_investment_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}39'] = {
            'text': average_squaremeters_per_apartment,
            'format': 'regular_investment_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}40'] = {
            'text': average_rent_per_squaremeter,
            'format': 'regular_investment_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}41'] = {
            'text': 'ü' if entry['furnishing'] else '-',
            'format': 'wingdings_investment' if entry['furnishing'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}42'] = {
            'text': 'ü' if entry['kitchen'] else '-',
            'format': 'wingdings_investment' if entry['kitchen'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}43'] = {
            'text': 'ü' if entry['balcony'] else '-',
            'format': 'wingdings_investment' if entry['balcony'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}44'] = {
            'text': 'ü' if entry['bath'] else '-',
            'format': 'wingdings_investment' if entry['bath'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}45'] = {
            'text': 'ü' if entry['community_spaces'] else '-',
            'format': 'wingdings_investment' if entry['community_spaces'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}46'] = {
            'text': 'ü' if entry['services'] else '-',
            'format': 'wingdings_investment' if entry['services'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}47'] = {
            'text': 'ü' if entry['gym'] else '-',
            'format': 'wingdings_investment' if entry['gym'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}48'] = {
            'text': 'ü' if entry['media_lounge'] else '-',
            'format': 'wingdings_investment' if entry['media_lounge'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}49'] = {
            'text': 'ü' if entry['study_lounge'] else '-',
            'format': 'wingdings_investment' if entry['study_lounge'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}50'] = {
            'text': 'ü' if entry['laundry_room'] else '-',
            'format': 'wingdings_investment' if entry['laundry_room'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}51'] = {
            'text': 'ü' if entry['rooms_for_events'] else '-',
            'format': 'wingdings_investment' if entry['rooms_for_events'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}52'] = {
            'text': 'ü' if entry['bar'] else '-',
            'format': 'wingdings_investment' if entry['bar'] else 'regular_investment'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}53'] = {
            'text': 'ü' if entry['collaborative_cooking'] else '-',
            'format': 'wingdings_investment' if entry['collaborative_cooking'] else 'regular_investment'
          }

          column_id += 1
        else:
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}31'] = {
            'text': entry['operator'],
            'format': 'bold_fs8_underline'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}32'] = {
            'text': f"{entry['street']}, {entry['postcode']} {entry['city']}",
            'format': 'bold_fs8_wrap_vcenter'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}33'] = {
            'text': entry['number_of_apartments'] if entry['number_of_apartments'] is not None else '-',
            'format': 'regular_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}34'] = {
            'text': all_in_rent_from,
            'format': 'regular_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}35'] = {
            'text': all_in_rent_up_to,
            'format': 'regular_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}36'] = {
            'text': average_rent_per_apartment,
            'format': 'regular_number'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}37'] = {
            'text': apartment_size_from,
            'format': 'regular_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}38'] = {
            'text': apartment_size_up_to,
            'format': 'regular_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}39'] = {
            'text': average_squaremeters_per_apartment,
            'format': 'regular_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}40'] = {
            'text': average_rent_per_squaremeter,
            'format': 'regular_number_with_two_komma'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}41'] = {
            'text': 'ü' if entry['furnishing'] else '-',
            'format': 'wingdings' if entry['furnishing'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}42'] = {
            'text': 'ü' if entry['kitchen'] else '-',
            'format': 'wingdings' if entry['kitchen'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}43'] = {
            'text': 'ü' if entry['balcony'] else '-',
            'format': 'wingdings' if entry['balcony'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}44'] = {
            'text': 'ü' if entry['bath'] else '-',
            'format': 'wingdings' if entry['bath'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}45'] = {
            'text': 'ü' if entry['community_spaces'] else '-',
            'format': 'wingdings' if entry['community_spaces'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}46'] = {
            'text': 'ü' if entry['services'] else '-',
            'format': 'wingdings' if entry['services'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}47'] = {
            'text': 'ü' if entry['gym'] else '-',
            'format': 'wingdings' if entry['gym'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}48'] = {
            'text': 'ü' if entry['media_lounge'] else '-',
            'format': 'wingdings' if entry['media_lounge'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}49'] = {
            'text': 'ü' if entry['study_lounge'] else '-',
            'format': 'wingdings' if entry['study_lounge'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}50'] = {
            'text': 'ü' if entry['laundry_room'] else '-',
            'format': 'wingdings' if entry['laundry_room'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}51'] = {
            'text': 'ü' if entry['rooms_for_events'] else '-',
            'format': 'wingdings' if entry['rooms_for_events'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}52'] = {
            'text': 'ü' if entry['bar'] else '-',
            'format': 'wingdings' if entry['bar'] else 'regular'
          }
          micro_living_comparables_current_page['cell_content']['cells'][f'{columns[column_id]}53'] = {
            'text': 'ü' if entry['collaborative_cooking'] else '-',
            'format': 'wingdings' if entry['collaborative_cooking'] else 'regular'
          }

          column_id += 1

        last_coord_dist = entry['distance']
      
      request, no_number_map_marker = self.build_micro_living_competitor_map_request(page_entries, page_id, no_number_map_marker)
      requests.append((request, f'map_image_{page_id}_{Variables.unique_code}'))
      micro_living_comparables_current_page['cell_content']['images']['B7']['file'] = f'tmp/map_image_{page_id}_{Variables.unique_code}.png'
      micro_living_comparables['pages'][f'Competitors De {page_id}'] = micro_living_comparables_current_page
      page_order.append(f'Competitors De {page_id}')
      anvil.server.call('excel_test', micro_living_comparables, page_order, requests, bounding_box, Variables.unique_code)

      micro_living = app_tables.pictures.search()[0]
      anvil.media.download(micro_living['pic'])
  
  def build_micro_living_competitor_map_request(self, competitors, page_id, no_number_map_marker):
    request_static_map_raw = f"%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B"
    request_static_map = request_static_map_raw
    marker_number = 10 * page_id - 10
    last_coord_dist = -1

    for competitor_index, competitor in enumerate(competitors):
      if not competitor['distance'] == last_coord_dist:
        icon = f'locator.png'
        no_number_map_marker += 1
        marker_number += 1
        if not competitor['distance'] == 0:
          if competitor['is_360_operator']:
            icon = f'360_operator@0.5x.png'
          else:
            no_number_map_marker -= 1
            icon = f'micro_living_{marker_number - no_number_map_marker}@0.5x.png'
      competitor['icon'] = icon
      url = f'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/{icon}'
      encoded_url = url.replace("/", "%2F")
      if not (competitor_index + 1) % 10 == 1 and not request_static_map[-1] == "B":
        request_static_map += f"%2C"
      request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{competitor['longitude']},{competitor['latitude']}%5D%7D%7D"
      last_coord_dist = competitor['distance']
    request_static_map += "%5D%7D"

    return request_static_map, no_number_map_marker

  def mapbox_token_pressed_enter(self, **event_args):
    Variables.mapbox_token = self.mapbox_token
    self.form_show()

  def createGeoJSONCircle (self, center, radiusInKm, points = 64):
    coords = {
        "latitude": center[1],
        "longitude": center[0]
    };

    km = radiusInKm

    ret = [];
    distanceX = km/(111.320*math.cos(coords["latitude"]*math.pi/180))
    distanceY = km/110.574

    theta = None
    x = None
    y = None
    i = 0
    while i < points:
      theta = (i/points)*(2*math.pi)
      x = distanceX*math.cos(theta)
      y = distanceY*math.sin(theta)
      
      ret.append([coords["longitude"]+x, coords["latitude"]+y])
      i += 1

    ret.append(ret[0])

    return {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ret]
                }
            }]
        }
    }

  def add_circle_click(self, **event_args):
    uni_code = anvil.server.call('get_unique_code')
    Variables.added_circles.append(uni_code)
    self.mapbox.addSource(f"radius_{uni_code}", self.createGeoJSONCircle([13.4092, 52.5167], 50));
    self.mapbox.addLayer({
      "id": f"radius_{uni_code}",
      "type": "fill",
      "source": f"radius_{uni_code}",
      "layout": {},
      "paint": {
          "fill-color": "rgba(0, 0, 0, 0)",
          "fill-outline-color": "blue",
          "fill-opacity": 0.6
      }
    })

    import 

    new_circle = TextBox(type="number")
    self.active_circles.add_component(new_circle)