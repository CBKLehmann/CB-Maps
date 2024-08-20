from ._anvil_designer import Map2_0Template
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
from anvil.tables import app_tables
from anvil.js.window import document
from anvil_extras.storage import local_storage
from .. import Variables, Layer, Images, ExcelFrames, Functions
from .Handle_Local_Storage import load_local_storage_settings
from . import Mapbox_Functions, Mapbox_Variables
from .Market_Study_Functions import generate_market_studies
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

  ''' Code angepasst '''
  def __init__(self, **properties):
    with anvil.server.no_loading_indicator:
      self.init_components(**properties)
      self.dom = anvil.js.get_dom_node(self.spacer_1)
      self.time_dropdown.items = [("5 minutes", "5"), ("10 minutes", "10"), ("15 minutes", "15"), ("20 minutes", "20"), ("30 minutes", "30"), ("60 minutes", "60"), ("5 minutes layers", "-1")]
      Variables.app_url = anvil.server.call_s('get_app_url')
      self.last_menu_height = '30%'
      self.competitors = []
      self.custom_marker = []
      self.comp_marker = []
      self.last_popup = None
      self.last_target = None
      self.active_container = None
      self.prev_called = None
      self.local_loading = False
      html = document.getElementsByClassName('anvil-root-container')[0]
      html.style.cursor = 'default'

  ''' Code angepasst '''
  def form_show(self, **event_args):
    with anvil.server.no_loading_indicator:
      ''' App-related Functions '''
      self.set_device_settings()
      self.set_display_settings()
      self.add_component_tags()
      document.addEventListener('click', functools.partial(self.remove_details, None))

      ''' Map-related Functions '''
      Mapbox_Functions.initialise_mapbox(self.dom, self.marker_draggable)
      self.add_map_listeners()

  ''' Code angepasst '''
  def set_device_settings(self):
    width, height = anvil.js.call('get_screen_width')
    self.mobile = False
    
    if width <= 998:
      self.mobile = True
      self.mobile_btn_grid.visible = True
      self.mobile_menu_open = False
      
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

  ''' Code angepasst '''
  def set_display_settings(self):
    if Variables.user_role == 'guest':
      self.marker_draggable = False
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
        self.reset_map.visible = True
        self.Summary.visible = True
        self.marker_draggable = True
        if Variables.user_role == 'admin':
          self.admin_button.visible = True
          self.db_upload.visible = True
          self.mapbox_token.visible = True

  ''' Code angepasst '''
  def add_component_tags(self):
    self.select_all_hc.tag.categorie = 'Healthcare'
    self.select_all_opnv.tag.categorie = 'ÖPNV'
    self.select_all_edu.tag.categorie = 'Student Living'
    self.select_all_food.tag.categorie = 'Food & Drinks'
    self.select_all_micro_living.tag.categorie = 'Micro Living'

  ''' Code angepasst '''
  def add_map_listeners(self):
    Mapbox_Variables.geocoder.on("result", self.move_marker)
    Mapbox_Variables.location_marker.on("dragend", self.marker_dragged)
    Mapbox_Variables.map.on("mousemove", "federal_states", self.change_hover_state)
    Mapbox_Variables.map.on("mouseleave", "federal_states", self.change_hover_state)
    Mapbox_Variables.map.on("mousemove", "administrative_districts", self.change_hover_state)
    Mapbox_Variables.map.on("mouseleave", "administrative_districts", self.change_hover_state)
    Mapbox_Variables.map.on("mousemove", "counties", self.change_hover_state)
    Mapbox_Variables.map.on("mouseleave", "counties", self.change_hover_state)
    Mapbox_Variables.map.on("mousemove", "municipalities", self.change_hover_state)
    Mapbox_Variables.map.on("mouseleave", "municipalities", self.change_hover_state)
    Mapbox_Variables.map.on("mousemove", "districts", self.change_hover_state)
    Mapbox_Variables.map.on("mouseleave", "districts", self.change_hover_state)
    Mapbox_Variables.map.on("mousemove", 'netherlands', self.change_hover_state)
    Mapbox_Variables.map.on("mouseleave", 'netherlands', self.change_hover_state)
    Mapbox_Variables.map.on("click", "federal_states", self.popup)
    Mapbox_Variables.map.on("click", "administrative_districts", self.popup)
    Mapbox_Variables.map.on("click", "counties", self.popup)
    Mapbox_Variables.map.on("click", "municipalities", self.popup)
    Mapbox_Variables.map.on("click", "districts", self.popup)
    Mapbox_Variables.map.on("style.load", self.handle_style_change)
    Mapbox_Variables.map.on("load", self.handle_map_load)
    Mapbox_Variables.map.on("contextmenu", self.map_right_click)
    Mapbox_Variables.map.on("click", self.map_right_click)

  def handle_map_load(self, event):
    if Variables.user_role == 'guest':
      self.load_hash()
      Functions.manipulate_loading_overlay(False)
    else:
      self.local_loading = True
      self.local_keys = local_storage.keys()
      self.load_local_storage_map_style()
  
  def load_hash(self):
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
          Mapbox_Variables.location_marker.setLngLat([data['marker_lng'], data['marker_lat']])
          Mapbox_Variables.map.flyTo({"center": [data['marker_lng'], data['marker_lat']], "zoom": data['zoom']})
        else:
          Mapbox_Variables.map.flyTo({"center": [data['center']['lng'], data['center']['lat']], "zoom": data['zoom']})
          Mapbox_Variables.location_marker.remove()
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

  def load_local_storage_map_style(self):
    if 'map_style' in self.local_keys:
      for component in self.style_grid.get_components():
        if component.text == local_storage['map_style']:
          component.checked = True
          component.raise_event('change')
    else:
      self.load_local_storage_settings()

  def load_local_storage_settings(self):
    Functions.manipulate_loading_overlay(True)
    if 'marker' in self.local_keys:
        Mapbox_Variables.map.flyTo({'center': local_storage['marker'], 'essential': True})
        self.move_marker_and_update_dependencies(local_storage['marker'])
    if 'active_marker' in self.local_keys:
      self.hide_ms_marker.checked = local_storage['active_marker']
      self.hide_ms_marker.raise_event('change')
    if 'active_distance_layer' in self.local_keys:
      self.iso_layer_active.checked = local_storage['active_distance_layer']
      self.iso_layer_active.raise_event('change')
    if 'time_dropdown' in self.local_keys:
      self.time_dropdown.selected_value = local_storage['time_dropdown']
    if 'profile_dropdown' in self.local_keys:
      self.profile_dropdown.selected_value = local_storage['profile_dropdown']
      self.profile_dropdown.raise_event('change')
    if 'distance_circles' in self.local_keys:
      for key in local_storage['distance_circles']:
        self.add_circle_click(local_storage['distance_circles'][key]['visible'], local_storage['distance_circles'][key]['distance'], key, True)
    else:
      self.add_circle_click(visible=False)
    if 'map_overlay' in self.local_keys:
      for component in self.layer_categories.get_components():
        if component.text.replace(" ", "_").lower() == local_storage['map_overlay']:
          component.checked = True
          component.raise_event('change')
    if 'healthcare' in self.local_keys:
      if not "0" in local_storage['healthcare']:
        self.select_all_hc.checked = True
        self.select_all_hc.raise_event('change')
      else:
        for index, component in enumerate(self.poi_categories_healthcare_container.get_components()):
          if not component.text == "Select All":
            if local_storage['healthcare'][index - 1] == "1":
              component.checked = True
              component.raise_event('change')
    else:
      healthcare_settings = ""
      for component in self.poi_categories_healthcare_container.get_components():
        if not component.text == "Select All":
          healthcare_settings += "0"
      local_storage['healthcare'] = healthcare_settings
    if 'student_living' in self.local_keys:
      if not "0" in local_storage['student_living']:
        self.select_all_edu.checked = True
        self.select_all_edu.raise_event('change')
      else:
        for index, component in enumerate(self.education_grid.get_components()):
          if not component.text == "Select All":
            if local_storage['student_living'][index - 1] == "1":
              component.checked = True
              component.raise_event('change')
    else:
      student_living_settings = ""
      for component in self.education_grid.get_components():
        if not component.text == "Select All":
          student_living_settings += "0"
      local_storage['student_living'] = student_living_settings
    if 'micro_living' in self.local_keys:
      if not "0" in local_storage['micro_living']:
        self.select_all_micro_living.checked = True
        self.select_all_micro_living.raise_event('change')
      else:
        for index, component in enumerate(self.micro_living_check_boxes.get_components()):
          if not component.text == "Select All":
            if local_storage['micro_living'][index - 1] == "1":
              component.checked = True
              component.raise_event('change')
    else:
      micro_living_settings = ""
      for component in self.micro_living_check_boxes.get_components():
        if not component.text == "Select All":
          micro_living_settings += "0"
      local_storage['micro_living'] = micro_living_settings
    if 'food_drinks' in self.local_keys:
      if not "0" in local_storage['food_drinks']:
        self.select_all_food.checked = True
        self.select_all_food.raise_event('change')
      else:
        for index, component in enumerate(self.food_drinks_grid.get_components()):
          if not component.text == "Select All":
            if local_storage['food_drinks'][index - 1] == "1":
              component.checked = True
              component.raise_event('change')
    else:
      food_drinks_settings = ""
      for component in self.food_drinks_grid.get_components():
        if not component.text == "Select All":
          food_drinks_settings += "0"
      local_storage['food_drinks'] = food_drinks_settings
    if 'public_transport' in self.local_keys:
      if not "0" in local_storage['public_transport']:
        self.select_all_opnv.checked = True
        self.select_all_opnv.raise_event('change')
      else:
        for index, component in enumerate(self.opnv_container.get_components()):
          if not component.text == "Select All":
            if local_storage['public_transport'][index - 1] == "1":
              component.checked = True
              component.raise_event('change')
    else:
      public_transport_settings = ""
      for component in self.opnv_container.get_components():
        if not component.text == "Select All":
          public_transport_settings += "0"
      local_storage['public_transport'] = public_transport_settings
    if 'removed_marker' in self.local_keys:
      for key in local_storage['removed_marker'].keys():
        for marker in local_storage['removed_marker'][key]:
          self.remove_marker(key, marker, None, True)
    if 'custom_marker' in self.local_keys:
      for marker in local_storage['custom_marker']:
        self.create_custom_marker(marker, marker['coordinates'])
    if 'cluster_data' in self.local_keys:
      self.handle_teaser_data(True)
    self.local_loading = False
    Functions.manipulate_loading_overlay(False)

  def check_box_marker_icons_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      # Show or Hide Marker-Icon-Types
      if event_args['sender'] in self.icon_grid.get_components():
        new_active = local_storage['cluster_active']
        new_active[event_args['sender'].tooltip] = event_args['sender'].checked
        local_storage['cluster_active'] = new_active
      elif event_args['sender'] in self.invest_grid.get_components():
        active_index = self.invest_grid.get_components().index(event_args['sender'])
        new_active = local_storage['invest_active']
        new_active[event_args['sender'].tooltip] = event_args['sender'].checked
        local_storage['invest_active'] = new_active
      Functions.show_hide_marker(self, event_args['sender'].checked, event_args['sender'].tooltip)

  def button_marker_icons_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      # Show or Hide all Marker Icons
  
      if event_args['sender'] == self.cluster_all:
        all_marker = self.icon_grid.get_components()
        key = 'cluster_active'
      else:
        all_marker = self.invest_grid.get_components()
        key = 'invest_active'
      
      new_local_storage = local_storage[key]
        
      for marker in all_marker:
        if not type(marker) is Label:
          if not marker.checked == event_args['sender'].checked:
            new_local_storage[marker.tooltip] = event_args['sender'].checked
            Functions.show_hide_marker(self, event_args['sender'].checked, marker.tooltip)
            marker.checked = event_args['sender'].checked

      local_storage[key] = new_local_storage
     
  def check_box_overlays_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      layer_name = event_args['sender'].text.replace(" ", "_").lower()
      local_storage['map_overlay'] = layer_name if event_args['sender'].checked else None
      outline_name = "outline_" + layer_name
      visibility = Mapbox_Variables.map.getLayoutProperty(layer_name, "visibility")
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
      
      Functions.change_active_Layer([layer_name, outline_name], inactive_layers, new_visibility, inactive_checkboxes)

  def check_box_poi_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(True)
      index = event_args['sender'].parent.get_components().index(event_args['sender']) - 1
      if dict(event_args)['sender'].text == "Veterinary":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_vet, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_vet.checked, Variables.last_bbox_vet, "veterinary", Variables.icon_veterinary)
      elif dict(event_args)['sender'].text == "Social Facility":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_soc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_soc.checked, Variables.last_bbox_soc, "social_facility", Variables.icon_social)   
      elif dict(event_args)['sender'].text == "Pharmacy":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_pha, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_pha.checked, Variables.last_bbox_pha, "pharmacy", Variables.icon_pharmacy)
      elif dict(event_args)['sender'].text == "Hospital":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_hos, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_hos.checked, Variables.last_bbox_hos, "hospital", Variables.icon_hospital)
      elif dict(event_args)['sender'].text == "Clinic":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_cli, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cli.checked, Variables.last_bbox_cli, "clinic", Variables.icon_clinics)
      elif dict(event_args)['sender'].text == "Dentist":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_den, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_den.checked, Variables.last_bbox_den, "dentist", Variables.icon_dentist)  
      elif dict(event_args)['sender'].text == "Doctor":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_doc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_doc.checked, Variables.last_bbox_doc, "doctors", Variables.icon_doctors)      
      elif dict(event_args)['sender'].text == "Nursing School":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_nsc, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_nsc.checked, Variables.last_bbox_nsc, "nursing-schools", Variables.icon_nursing_schools) 
      elif dict(event_args)['sender'].text == "Supermarket":
        settings = local_storage['food_drinks'][:index] + "1" + local_storage['food_drinks'][index + 1:]
        local_storage['food_drinks'] = settings
        Variables.last_bbox_sma, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_sma.checked, Variables.last_bbox_sma, "supermarket", Variables.icon_supermarket)  
      elif dict(event_args)['sender'].text == "Restaurant":
        settings = local_storage['food_drinks'][:index] + "1" + local_storage['food_drinks'][index + 1:]
        local_storage['food_drinks'] = settings
        Variables.last_bbox_res, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_res.checked, Variables.last_bbox_res, "restaurant", Variables.icon_restaurant)  
      elif dict(event_args)['sender'].text == "Cafe":
        settings = local_storage['food_drinks'][:index] + "1" + local_storage['food_drinks'][index + 1:]
        local_storage['food_drinks'] = settings
        Variables.last_bbox_caf, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_cafe.checked, Variables.last_bbox_caf, "cafe", Variables.icon_cafe)
      elif dict(event_args)['sender'].text == "University":
        settings = local_storage['student_living'][:index] + "1" + local_storage['student_living'][index + 1:]
        local_storage['student_living'] = settings
        Variables.last_bbox_uni, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_uni.checked, Variables.last_bbox_uni, "university", Variables.icon_university)  
      elif dict(event_args)['sender'].text == "Bus Stop":
        settings = local_storage['public_transport'][:index] + "1" + local_storage['public_transport'][index + 1:]
        local_storage['public_transport'] = settings
        Variables.last_bbox_bus, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_bus.checked, Variables.last_bbox_bus, "bus_stop", Variables.icon_bus)  
      elif dict(event_args)['sender'].text == "Tram Stop":
        settings = local_storage['public_transport'][:index] + "1" + local_storage['public_transport'][index + 1:]
        local_storage['public_transport'] = settings
        Variables.last_bbox_tra, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_tra.checked, Variables.last_bbox_tra, "tram_stop", Variables.icon_tram)
      elif dict(event_args)['sender'].text == "Nursing Home":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_nh, minimum_average_rent, maximum_average_rent = self.create_icons(self.pdb_data_cb.checked, Variables.last_bbox_nh, "nursing_homes", Variables.icon_nursing_homes)
      elif dict(event_args)['sender'].text == "Assisted Living":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_al, minimum_average_rent, maximum_average_rent = self.create_icons(self.pdb_data_al.checked, Variables.last_bbox_al, "assisted_living", Variables.icon_assisted_living)
      elif dict(event_args)['sender'].text == "Podiatrist":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_pdt, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_pdt.checked, Variables.last_bbox_pdt, "podiatrist", Variables.icon_podiatrist)
      elif dict(event_args)['sender'].text == "Hairdresser":
        settings = local_storage['healthcare'][:index] + "1" + local_storage['healthcare'][index + 1:]
        local_storage['healthcare'] = settings
        Variables.last_bbox_hd, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_hd.checked, Variables.last_bbox_hd, "hairdresser", Variables.icon_hairdresser)
      elif event_args['sender'].text == "S-Bahn":
        settings = local_storage['public_transport'][:index] + "1" + local_storage['public_transport'][index + 1:]
        local_storage['public_transport'] = settings
        Variables.last_bbox_al, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_su.checked, Variables.last_bbox_su, "subway", f'{Variables.app_url}/_/theme/Pins/U_Bahn_Pin.png')
      elif event_args['sender'].text == "Airport":
        settings = local_storage['public_transport'][:index] + "1" + local_storage['public_transport'][index + 1:]
        local_storage['public_transport'] = settings
        Variables.last_bbox_ap, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_ap.checked, Variables.last_bbox_ap, "aerodrome", f'{Variables.app_url}/_/theme/Pins/Flughafen_Pin.png')
      elif event_args['sender'].text == "Business Living":
        settings = local_storage['micro_living'][:index] + "1" + local_storage['micro_living'][index + 1:]
        local_storage['micro_living'] = settings
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
        settings = local_storage['micro_living'][:index] + "1" + local_storage['micro_living'][index + 1:]
        local_storage['micro_living'] = settings
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
        settings = local_storage['micro_living'][:index] + "1" + local_storage['micro_living'][index + 1:]
        local_storage['micro_living'] = settings
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
        settings = local_storage['micro_living'][:index] + "1" + local_storage['micro_living'][index + 1:]
        local_storage['micro_living'] = settings
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
      elif event_args['sender'].text == "Motorway":
        settings = local_storage['public_transport'][:index] + "1" + local_storage['public_transport'][index + 1:]
        local_storage['public_transport'] = settings
        Variables.last_bbox_mw, minimum_average_rent, maximum_average_rent = self.create_icons(self.check_box_mw.checked, Variables.last_bbox_mw, "motorway", f'{Variables.app_url}/_/theme/Pins/Flughafen_Pin.png')
      Functions.manipulate_loading_overlay(False)

  def checkbox_poi_x_hfcig_change(self, **event_args):
    #This method is called when the Check Box for POI based on HFCIG is checked or unchecked
    with anvil.server.no_loading_indicator:
      if self.checkbox_poi_x_hfcig.checked == True:
        bbox = Functions.create_bounding_box(self)
      else:  
        bbox = [(dict(Mapbox_Variables.map.getBounds()['_sw']))['lat'], (dict(Mapbox_Variables.map.getBounds()['_sw']))['lng'], (dict(Mapbox_Variables.map.getBounds()['_ne']))['lat'], (dict(Mapbox_Variables.map.getBounds()['_ne']))['lng']]
      
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
      local_storage['map_style'] = event_args['sender'].text
      if event_args['sender'].text == "Satellite Map":
        self.check_street.checked = False
        self.check_light.checked = False
        self.check_basic.checked = False
        Mapbox_Variables.map.setStyle('mapbox://styles/mapbox/satellite-streets-v11')
      elif event_args['sender'].text == "Street Map":
        self.check_satellite.checked = False
        self.check_light.checked = False
        self.check_basic.checked = False
        Mapbox_Variables.map.setStyle('mapbox://styles/mapbox/outdoors-v11')
      elif event_args['sender'].text == "Light Map":
        self.check_street.checked = False
        self.check_satellite.checked = False
        self.check_basic.checked = False
        Mapbox_Variables.map.setStyle('mapbox://styles/mapbox/light-v11')
      elif event_args['sender'].text == "Basic Map":
        self.check_street.checked = False
        self.check_satellite.checked = False
        self.check_light.checked = False
        Mapbox_Variables.map.setStyle('mapbox://styles/shinykampfkeule/cldkfk8qu000001thivb3l1jn')

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

      Mapbox_Variables.map.addSource("radius", self.createGeoJSONCircle([13.4092, 52.5167], 50));
      
      Mapbox_Variables.map.addLayer({
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

  def create_market_study_clicked(self, **event_args):
    print(datetime.datetime.now())
    generate_market_studies(self)
    print(datetime.datetime.now())

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
      local_storage['profile_dropdown'] = self.profile_dropdown.selected_value
      local_storage['time_dropdown'] = self.time_dropdown.selected_value
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)

      Functions.refresh_icons(self)

  #####  Dropdown Functions #####
  ###############################
  #####  Upload Functions   #####

  #This method is called when a new file is loaded into the FileLoader
  def cb_teaser_upload(self, file, **event_args):  
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(True)
      anvil.js.call('update_loading_bar', 5, 'Reading Excel File')

      if not file.name.split('.')[-1] in ["xlsm", "xlsx"]:
        Functions.show_error_alert({
            'alert_title': "Incorrect file format type uploaded",
            'alert_message': "It looks like an incorrect file format was uploaded. Please ensure that only Excel files are uploaded for processing",
            'alert_try_again': False
          })
        self.file_loader_upload.clear()
        return

      local_storage['cluster_data'] = anvil.server.call('cb_teaser_processing', file)
      if local_storage['cluster_data']['code'] == 400:
        Functions.show_error_alert({
          'alert_title': "Error while processing Excel File",
          'alert_message': "It appears that the data set is incorrect. Make sure you have uploaded the correct file.",
          'alert_try_again': False
        })
        self.file_loader_upload.clear()
        return

      self.handle_teaser_data()
  
  def handle_teaser_data(self, local_load = False):
    with anvil.server.no_loading_indicator:
      ''' Hide UI Elements while Processing and trigger Events '''
      self.cluster_btn.visible = False
      self.invest_class_btn.visible = False
      self.cluster_all.visible = False
      self.i_class_all.visible = False
      self.icon_grid.visible = False
      self.invest_grid.visible = False
      self.change_cluster_color.visible = False
      self.invest_class_btn.raise_event('click')
      self.cluster_btn.raise_event('click')
      if self.mobile:
        self.mobile_hide_click()

      ''' Delete all current Markers '''
      for key in Variables.marker.keys():
        for marker in Variables.marker[key]['marker']:
          marker.remove()
      Variables.marker = {}
      self.icon_grid.clear()
      self.invest_grid.clear()

      ''' Initialise needed Variables '''
      anvil.js.call('update_loading_bar', 15, 'Creating Markers and Clusters')
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
      self.icon_grid.row_spacing = 0
      counter = 0
      cluster_active = {}
      invest_active = {}
      if 'cluster_active' in local_storage.keys() and local_load:
        cluster_active = local_storage['cluster_active']
      if 'invest_active' in local_storage.keys() and local_load:
        invest_active = local_storage['invest_active']

      ''' Process Cluster Data '''
      for asset in local_storage['cluster_data']['content']:
  
        ''' Create HTML Element for Icon '''
        el = document.createElement('div')
        el.className = f'{asset["address"]}'
        el.style.width = '40px'
        el.style.height = '40px'
        el.style.backgroundSize = '100%'
        el.style.backgroundrepeat = 'no-repeat'
        el.style.zIndex = '250'

        ''' Create HTML Element for Invest Class Icon '''
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
          if 'cluster_color' in local_storage.keys() and local_load:
            color = local_storage['cluster_color'][cluster_name]
          else:
            counter += 1
            color = colors[counter]
          if not local_load:
            cluster_active[cluster_name] = True
          text = f"{cluster_name[:11]}..." if len(cluster_name) > 11 else cluster_name
          checkbox = CheckBox(checked=cluster_active[cluster_name], text=text, spacing_above='none', spacing_below='none', font='Roboto+Flex', font_size=13, role='switch-rounded', tooltip=cluster_name)
          checkbox.add_event_handler('change', self.check_box_marker_icons_change)
          icon = Label(icon='fa:circle', foreground=color[1], spacing_above='none', spacing_below='none', icon_align='top')
          cluster_components[cluster_name] = [checkbox, icon]
          added_clusters.append(cluster_name)
        
        if invest_name not in added_invest_classes:
          if not local_load:
            invest_active[invest_name] = False
          text = f"{invest_name[:11]}..." if len(invest_name) > 11 else invest_name
          checkbox = CheckBox(checked=invest_active[invest_name], text=text, spacing_above='none', spacing_below='none', font='Roboto+Flex', font_size=13, role='switch-rounded', tooltip=invest_name)
          checkbox.add_event_handler('change', self.check_box_marker_icons_change)
          invest_components[invest_name] = checkbox
          added_invest_classes.append(invest_name)
        
        # #Get Coordinates of provided Adress for Marker
        req_str = self.build_request_string(asset)
        req_str += f'.json?access_token={Mapbox_Variables.token}'
        coords = anvil.http.request(req_str,json=True)
        print(req_str)
        print(coords)
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

      if not local_load:
        local_storage['cluster_active'] = cluster_active
        local_storage['invest_active'] = invest_active

      ''' Update UI Elements'''
      anvil.js.call('update_loading_bar', 60, 'Adding Menu Items')
      for key in sorted(cluster_components):
        self.icon_grid.add_component(cluster_components[key][0], row=key, col_xs=1, width_xs=8)
        self.icon_grid.add_component(cluster_components[key][1], row=key, col_xs=9, width_xs=1)
        sorted_keys = ['Super Core', 'Core/ Core+', 'Value Add', 'Opportunistic', 'Development', 'Workout', 'Unclassified']

      for key in sorted(invest_components.keys(), key=lambda x: sorted_keys.index(x)):
        self.invest_grid.add_component(invest_components[key], row=key, col_xs=1, width_xs=8)

      ''' Update global Marker List '''
      Variables.marker.update(excel_markers)

      ''' Set Custom Colors for Markers '''
      if not local_load:
        anvil.js.call('update_loading_bar', 80, 'Waiting for individual Cluster Colors')
        self.change_cluster_color_click()
        anvil.js.call('remove_span')

      ''' Update created Markers on Map '''
      anvil.js.call('update_loading_bar', 95, 'Loading created Markers')
      for checkbox in self.invest_grid.get_components():
        if not local_storage['invest_active'][checkbox.tooltip]:
          checkbox.raise_event('change')
      for checkbox in self.icon_grid.get_components():
        if not checkbox.tooltip == "" and not local_storage['cluster_active'][checkbox.tooltip]:
          checkbox.raise_event('change')

      ''' Show UI Elements and trigger Events '''
      self.cluster_btn.visible = True
      self.invest_class_btn.visible = True
      self.cluster_all.visible = True
      self.i_class_all.visible = True
      self.icon_grid.visible = True
      self.invest_grid.visible = True
      self.change_cluster_color.visible = True
      self.invest_class_btn.raise_event('click')
      self.cluster_btn.raise_event('click')

      ''' Finish and Clean Up '''
      anvil.js.call('update_loading_bar', 100, 'Finishing Process')
      self.file_loader_upload.clear()
      Functions.manipulate_loading_overlay(False)
      anvil.js.call('update_loading_bar', 0, '')

  # This Function is called when a DB Update should be done
  def db_upload_change(self, file, **event_args):
    try:
      if 'Betreutes' in file.name:
        anvil.server.call('update_assisted_living_facilities_db', file)
      elif 'Pflegeheime' in file.name:
        anvil.server.call('update_nursing_home_facilities', file)
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
      self.move_marker_and_update_dependencies(result['result']['geometry']['coordinates'])
  
  #This method is called when the draggable Marker was moved
  def marker_dragged(self, drag):
    with anvil.server.no_loading_indicator:
      self.move_marker_and_update_dependencies(["{:.6f}".format(Mapbox_Variables.location_marker['_lngLat']['lng']),"{:.6f}".format(Mapbox_Variables.location_marker['_lngLat']['lat'])])
    
  #This method is called when the draggable Marker was moved or when the Geocoder was used
  def get_iso(self, profile, contours_minutes):
    with anvil.server.no_loading_indicator:
      #Check if isoLayer is already constructed
      if not Mapbox_Variables.map.getSource('iso'):
        
        #Construct Mapsource for isoLayer
        Mapbox_Variables.map.addSource('iso', {'type': 'geojson',
                                      'data': {'type': 'FeatureCollection',
                                              'features': []}
                                    })
        
        #Construct and add isoLayer
        Mapbox_Variables.map.addLayer({'id': 'isoLayer',
                              'type': 'fill',
                              'source': 'iso',
                              'layout': {'visibility': 'visible'},
                              'paint': {
                              'fill-color': '#0A2232',
                              'fill-opacity': 0.15,
                              'fill-outline-color': '#06151F'
                              },
                            })
      
      #Get iso-coordinates based of the marker-coordinates
      lnglat = Mapbox_Variables.location_marker.getLngLat()
      request_string = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{lnglat.lng},{lnglat.lat}?"
      
      #Check which iso-mode is currently active
      if contours_minutes == "-1":
        
        #Build request_string
        request_string = request_string + f"contours_minutes=5,10,15,20"
        
      else:
        
        #Build request_string
        request_string = request_string + f"contours_minutes={contours_minutes}"
      
      #Build request_string
      request_string += f"&polygons=true&access_token={Mapbox_Variables.token}"
      
      #Get Data from request
      Variables.activeIso = anvil.http.request(request_string,json=True)

      if Mapbox_Variables.map.getSource('iso') is not None:
        #Attach Data to iso-source
        Mapbox_Variables.map.getSource('iso').setData(Variables.activeIso)
      
  #This method is called when the User clicked a Part of a Map-Layer
  def popup(self, click):
    with anvil.server.no_loading_indicator:
      #Check which Layer is active
      if click.features[0].layer.source == 'federal_states':
        
        #Create Popup and add it to the Map
        bl_name = click.features[0].properties.name
        bl_id = click.features[0].id
        clicked_lngLat = dict(click.lngLat)
        popup = Mapbox_Functions.mapboxgl.Popup({'className': 'markerPopup'}).setLngLat(clicked_lngLat).setHTML(f"<p class='popup_distance'><b>Bundesland:</b> {bl_name}</p>").addTo(Mapbox_Variables.map)
      
      #Check which Layer is active
      elif click.features[0].layer.source == 'administrative_districts':
        
        #Create Popup and add it to the Map
        bl_name = click.features[0].properties.NAME_1
        rb_name = click.features[0].properties.NAME_2
        clicked_lngLat = dict(click.lngLat)
        popup = Mapbox_Functions.mapboxgl.Popup({'className': 'markerPopup'}).setLngLat(clicked_lngLat).setHTML(f"<p class='popup_distance'><b>Bundesland:</b> {bl_name}</p><p class='popup_distance'><b>Regierungsbezirk:</b> {rb_name}</p>").addTo(Mapbox_Variables.map)
      
      #Check which Layer is active
      elif click.features[0].layer.source == 'counties':
        
        #Create Popup and add it to the Map
        bl_name = click.features[0].properties.lan_name
        lk_name = click.features[0].properties.krs_name
        clicked_lngLat = dict(click.lngLat)
        popup = Mapbox_Functions.mapboxgl.Popup({'className': 'markerPopup'}).setLngLat(clicked_lngLat).setHTML(f"<p class='popup_distance'><b>Bundesland:</b> {bl_name}</p><p class='popup_distance'><b>Landkreis:</b> {lk_name}</p>").addTo(Mapbox_Variables.map)
    
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
        popup = Mapbox_Functions.mapboxgl.Popup().setLngLat(clicked_lngLat).setHTML(f'<b>Bezirk:</b> {dt_name}').addTo(Mapbox_Variables.map)

  #This method is called when the User clicked on a Point of Interest on the Map   #Eventuell nicht mehr benötigt
  def poi(self, click):
    with anvil.server.no_loading_indicator:
      #Get and Set Variables
      info = dict(Mapbox_Variables.map.style)
      
      #Check current Map-Style
      if (info['stylesheet']['metadata']['mapbox:origin'] == 'outdoors-v11'):
      
        #Get all Layers on the Map
        layers = Mapbox_Variables.map.getStyle().layers
    
        #Get all Features (Point of Interest) of selected Layers on clicked Point
        features = Mapbox_Variables.map.queryRenderedFeatures(click.point, {'layers': ['poi-label', 'transit-label', 'landuse', 'national-park']})
        
        #Check if no POI was clicked and no Layer is active
        if not features == [] and Variables.activeLayer == None and hasattr(features[0].properties, 'name') == True:
        
          #Create Popup on clicked Point with Information about the Point of Interest
          popup = Mapbox_Functions.mapboxgl.Popup().setLngLat(click.lngLat).setHTML('Name: ' + features[0].properties.name).addTo(Mapbox_Variables.map)
      
      #Check current Map-Style
      elif Variables.activeLayer == None:
        
        #Send Notification to User
        Notification('Point of Interests are only available on the Outdoor-Map !', style='info').show()
  
  #This method is called when the Map is loading or changing his Style
  def place_layer(self):
    with anvil.server.no_loading_indicator:
      #Add 3D-Layer to the Map
      Mapbox_Variables.map.addLayer({
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
        Mapbox_Variables.map.addLayer({
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
        Mapbox_Variables.map.addLayer({
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
        Mapbox_Variables.map.setLayoutProperty(Variables.activeLayer, 'visibility', 'visible')
        Mapbox_Variables.map.setLayoutProperty(f'outline_{Variables.activeLayer}', 'visibility', 'visible')
  
  #This method is called from the check_box_change-Functions to place Icons on Map  
  def create_icons(self, check_box, last_bbox, category, picture):
    with anvil.server.no_loading_indicator:
      minimum_average_rent = 0
      maximum_average_rent = 100
      
      # Check if Checkbox is checked
      if check_box == True:

        marker_coords = [Mapbox_Variables.location_marker['_lngLat']['lng'], Mapbox_Variables.location_marker['_lngLat']['lat']]
        
        # Check if Checkbox for Iso-Layer' is checked
        if self.checkbox_poi_x_hfcig.checked == True:
    
          # Get Data of Iso-Layer
          iso = dict(Mapbox_Variables.map.getSource('iso'))
    
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
          bbox = [Mapbox_Variables.map.getBounds()['_sw']['lat'], Mapbox_Variables.map.getBounds()['_sw']['lng'],
                  Mapbox_Variables.map.getBounds()['_ne']['lat'], Mapbox_Variables.map.getBounds()['_ne']['lng']]
          
        # Check if Bounding Box is not the same as least Request
        if not bbox == last_bbox:
          # Check if new Bounding Box is overlapping old Bounding Box
          if bbox[0] < last_bbox[0] or bbox[1] < last_bbox[1] or bbox[2] > last_bbox[2] or bbox[3] > last_bbox[3]:
      
            minimum_average_rent, maximum_average_rent = Functions.create_marker(self, check_box, last_bbox, category, picture, bbox, marker_coords, Mapbox_Functions.mapboxgl)
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
                el.addTo(Mapbox_Variables.map)
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
            el.addTo(Mapbox_Variables.map)
    
          # Change last Category
          Variables.last_cat = f'{category}'
      
      # Do if Checkbox is unchecked
      else:

        if category == "subway":
          for id in self.opnv_layer:
            Mapbox_Variables.map.setLayoutProperty(id, 'visibility', 'none')

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
      popup = Mapbox_Functions.mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
        f"<p class='popup_type'><b>{asset['address']}</b></p>"
        f"<p class='popup_type'>{asset['zip']} {asset['city']}<p>"
        f"<p class='popup_type'>{asset['federal_state']}</p>"
        f"<p class='popup_type'>Cluster: {asset['cluster']}<p>"
        f"<p class='popup_type'>Invest Class: {asset['invest_class']}<p>"
        f"<p class='popup_type'>Acqisition Date: {date}<p>"
      )
      marker_cat = Mapbox_Functions.mapboxgl.Marker({'draggable': False, 'element': el, 'anchor': 'bottom'}).setPopup(popup)
      marker_el = marker_cat.getElement()

      anvil.js.call('addHoverEffect', marker_el, popup, Mapbox_Variables.map, marker_cat, asset, asset['cluster'], "Hahahahahahahahahahahahahahahaha", self.mobile)
      
      # Add Marker to the Map
      newmarker = marker_cat.setLngLat(coords).addTo(Mapbox_Variables.map)
  
      # Add Marker Marker-Array
      marker_list.append(newmarker)
      return(marker_list)
    
  #This method is called when the Mouse is moved inside or out of an active Layer
  def change_hover_state(self, mouse):
    with anvil.server.no_loading_indicator:
      # Check if Layer is already hovered
      if Variables.hoveredStateId != None:
    
        # Change hover-State to False and set global-variable 'hoveredStateId' to None
        Mapbox_Variables.map.setFeatureState({'source': Variables.activeLayer, 'id': Variables.hoveredStateId}, {'hover': False})
        
        Variables.hoveredStateId = None
      
      #Check if Mouse is moved inside Layer or out of Layer
      if hasattr(mouse, 'features'):
        
        # Check if Mouse was moved inside active Map-Layer
        if len(mouse.features) > 0:
        
          # Change global hoveredStateID to new active Layer-id
          Variables.hoveredStateId = mouse.features[0].id
      
          # Change hover-State to True
          Mapbox_Variables.map.setFeatureState({'source': Variables.activeLayer, 'id': Variables.hoveredStateId}, {'hover': True})
  
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
        print(working_marker_coordinate)
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
        if marker_number == len(working_marker['sorted_coords']) - 1 or (marker_number + 1) % 20 == 0:
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
      local_storage['active_distance_layer'] = event_args['sender'].checked
      if event_args['sender'].checked:
        Mapbox_Variables.map.setLayoutProperty('isoLayer', 'visibility', 'visible')
      else:
        Mapbox_Variables.map.setLayoutProperty('isoLayer', 'visibility', 'none')
      pass

  def hide_ms_marker_change(self, **event_args):
    with anvil.server.no_loading_indicator:
      """This method is called when this checkbox is checked or unchecked"""
      local_storage['active_marker'] = event_args['sender'].checked
      if event_args['sender'].checked:
        Mapbox_Variables.location_marker.addTo(Mapbox_Variables.map)
      else:
        Mapbox_Variables.location_marker.remove()
      pass

  def change_cluster_color_click(self, **event_args):
    """This method is called when the button is clicked"""
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(True)
      from .Change_Cluster_Color import Change_Cluster_Color
      Functions.manipulate_loading_overlay(False)
      response = alert(content=Change_Cluster_Color(components=self.icon_grid.get_components(), mobile=self.mobile), dismissible=False, large=True, buttons=[], role='custom_alert')
      local_storage['cluster_color'] = response
      Functions.manipulate_loading_overlay(True)
      for key in Variables.marker:
        if key in response:
          Variables.marker[key]['color'] = response[key]
          for marker in Variables.marker[key]['marker']:
            anvil.js.call('changeBackground', marker['_element'], f"{Variables.app_url}{Variables.marker[key]['color'][2]}")
      for component in self.icon_grid.get_components():
        if type(component) == CheckBox:
          key = component.tooltip
        elif type(component) == Label:
          component.foreground = Variables.marker[key]["color"][1]
      if len(event_args.keys()) > 0:
        Functions.manipulate_loading_overlay(False)
  
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
        # popup = Mapbox_Functions.mapboxgl.Popup({'closeOnClick': False, 'offset': 25})
        # popup.setHTML(data[0][markercount]['Informationen'])
        # popup_static = Mapbox_Functions.mapboxgl.Popup({'closeOnClick': False, 'offset': 5, 'className': 'static-popup', 'closeButton': False, 'anchor': 'top'}).setText(data[0][markercount]['Informationen']).setLngLat(coords['features'][0]['geometry']['coordinates'])
        # popup_static.addTo(Mapbox_Variables.map)
        
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
        'data': local_storage['cluster_data'] if 'cluster_data' in local_storage.keys() else {},
        'settings': Variables.marker
      }

      from .Name_Share_Link import Name_Share_Link
      Functions.manipulate_loading_overlay(False)
      name = alert(content=Name_Share_Link(searched_address=changed_address), buttons=[], dismissible=False, large=True, role='custom_alert')
      Functions.manipulate_loading_overlay(True)
      self.url = anvil.server.call('get_app_url') + f'#?name={name}'
      center = Mapbox_Variables.map.getCenter()
      
      dataset = {
        'marker_lng': Mapbox_Variables.location_marker['_lngLat']['lng'],
        'marker_lat': Mapbox_Variables.location_marker['_lngLat']['lat'],
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
        'zoom': Mapbox_Variables.map.getZoom(),
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
    if self.local_loading:
      self.load_local_storage_settings()
    else:
      self.place_layer()
      self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    Functions.manipulate_loading_overlay(False) 

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

  def create_custom_marker(self, marker_data, coords = None):
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
    
    popup = Mapbox_Functions.mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
      f"<p class='popup_name'><b>{marker_data['name']}</b></p>"
      f"<p class='popup_type'>{marker_data['text']}</p>"
    )

    if marker_data['address'] is None:
      if coords == None:
        coords = self.clicked_coords
        marker_data['coordinates'] = coords
    else:
      coords = marker_data['address']['geometry']['coordinates']
    newicon = Mapbox_Functions.mapboxgl.Marker(el, {'anchor': 'bottom'}).setLngLat(coords).setOffset([0, 0]).addTo(Mapbox_Variables.map).setPopup(popup)

    popup = document.getElementById('mapPopup')
    if popup:
      popup.remove()

    if 'custom_marker' in local_storage.keys():
      new_custom_marker = local_storage['custom_marker']
      new_custom_marker.append(marker_data)
    else:
      local_storage['custom_marker'] = [marker_data]

  def copy_to_clipboard(self, **event_args):
    anvil.js.window.navigator.clipboard.writeText(self.url)

  def comp_loader_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    with anvil.server.no_loading_indicator:
      Functions.manipulate_loading_overlay(True)
      anvil.js.call('update_loading_bar', 5, 'Reading Excel File')
      #Call Server-Function to safe the File  
      marker_coords = [Mapbox_Variables.location_marker['_lngLat']['lng'], Mapbox_Variables.location_marker['_lngLat']['lat']]
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

        popup = Mapbox_Functions.mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
          f"<p class='popup_name'><b>{result['operator']}</b></p>"
          f"<p class='popup_type'>{result['address']}</p>"
          f"<p class='popup_type'>{result['zip']} {result['city']}, {result['federal_state']}</p>"
          f"<p class='popup_type'>{result['distance']} km</p>"
        )
    
        newicon = Mapbox_Functions.mapboxgl.Marker(el, {'anchor': 'bottom'}).setLngLat(result['coords']).setOffset([0, 0]).addTo(Mapbox_Variables.map).setPopup(popup)
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

        anvil.js.call('addHoverEffect', newiconElement, popup, Mapbox_Variables.map, newicon, result, 'Competitor', details, Variables.user_role)
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
      popup.addTo(Mapbox_Variables.map)
      pop = document.getElementsByClassName('mapboxgl-popup-content')[0]
      pop.addEventListener('mouseenter', functools.partial(self.readd_popup, popup))
      pop.addEventListener('mouseleave', functools.partial(self.remove_popup, popup))
      pop.addEventListener('click', functools.partial(self.show_details, category, marker_details, icon_element, dict(popup['_lngLat'])))

  def readd_popup(self, popup, event):
    if not popup == self.last_popup:
      popup.remove()
      popup.addTo(Mapbox_Variables.map)
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

  def remove_marker(self, category, marker_coords, event, local_storage_entry = False):
    from anvil_extras.storage import local_storage
    for index, marker in enumerate(Variables.activeIcons[category]):
      if marker['_lngLat']['lng'] == marker_coords['lng'] and marker['_lngLat']['lat'] == marker_coords['lat']:
        deleted_icon = Variables.activeIcons[category].pop(index)
        if local_storage_entry:
          if not category in Variables.removed_markers.keys():
            Variables.removed_markers[category] = [dict(marker['_lngLat'])]
          else:
            Variables.removed_markers[category].append(dict(marker['_lngLat']))
          if not 'removed_marker' in local_storage.keys():
            local_storage['removed_marker'] = {
              category: [marker_coords]
            }
          else:
            new_removed_marker = local_storage['removed_marker']
            if not category in new_removed_marker.keys():
              new_removed_marker[category] = [marker_coords]
            else:
              new_removed_marker[category].append(marker_coords)
            local_storage['removed_marker'] = new_removed_marker
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
    marker_coords = [Mapbox_Variables.location_marker['_lngLat']['lng'], Mapbox_Variables.location_marker['_lngLat']['lat']]
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
    Mapbox_Variables.token = Mapbox_Variables.map_token
    self.form_show()

  def add_circle_click(self, visible = True, distance = 5, uni_code = None, local_storage_entry = False, **event_args):
    layers = []
    if uni_code is None:
      uni_code = anvil.server.call('get_unique_code')
    Variables.added_circles.append(uni_code)
    if not local_storage_entry:
      if visible:
        if not 'distance_circles' in local_storage.keys():
          local_storage['distance_circles'] = {}
        new_storage = local_storage['distance_circles']
        new_storage[uni_code] = {
          'distance': 5,
          'visible': visible
        }
        local_storage['distance_circles'] = new_storage
      else:
        local_storage['distance_circles'] = {
          uni_code: {
            'distance': 5,
            'visible': visible
          }
        }
    Mapbox_Variables.map.addSource(
      f"source_{uni_code}", 
      Functions.createGeoJSONCircle([Mapbox_Variables.location_marker['_lngLat']['lng'], Mapbox_Variables.location_marker['_lngLat']['lat']], distance)
    )
    Mapbox_Variables.map.addLayer({
      "id": f"radius_{uni_code}",
      "type": "line",
      "source": f"source_{uni_code}",
      "layout": {},
      "paint": {
        "line-color": "#1B2939",
        "line-opacity": 0.25,
        "line-width": 2,
        "line-dasharray": [2, 1]
      }
    })
    Mapbox_Variables.map.addLayer({
      "id": f"symbol_{uni_code}",
      "type": "symbol",
      "source": f"source_{uni_code}",
      "layout": {
        "symbol-placement": "line",
        "text-field": '{title}',
        "text-size": 13,
        "text-anchor": "bottom"
      },
      "paint": {
        "text-color": "#1B2939",
        "text-opacity": .4,
        "text-halo-color": "#FFFFFF",
        "text-halo-width": 3,
        "text-halo-blur": 1
      }
    })
    layers.append(f"radius_{uni_code}")
    layers.append(f"symbol_{uni_code}")
    
    from .Active_Circle import Active_Circle

    new_circle = Active_Circle(uni_code, Mapbox_Variables.map, Mapbox_Variables.location_marker, layers, visible, distance)
    self.active_circles.add_component(new_circle)

  def move_marker_and_update_dependencies(self, coords):
    local_storage['marker'] = coords
    Mapbox_Variables.location_marker.setLngLat(coords)
    self.get_iso(self.profile_dropdown.selected_value.lower(), self.time_dropdown.selected_value)
    for circle in self.active_circles.get_components():
      circle.update_circle()
    Functions.refresh_icons(self)

  def reset_map_click(self, **event_args):
    local_storage.clear()
    local_storage.clear()
    local_storage['keep_user'] = True
    anvil.js.call('refresh_page')