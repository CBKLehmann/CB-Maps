import anvil.server
from anvil.tables import app_tables
from .. import Variables, Functions, Mapbox_Variables
from anvil import alert
import json, copy
from . import Market_Study_Variables
from ..Market_Study_Language import Market_Study_Language
from ..ChatGPT import ChatGPT
from .. import Nursing_Homes_Competitor_Skeleton
from .. import Assisted_Living_Competitor_Skeleton
from .. import Market_Study_Skeleton
from .Market_Study_Existing_Home import Market_Study_Existing_Home
from .Market_Study_NH_Home import Market_Study_NH_Home
from .Market_Study_NH_Home_Mobile import Market_Study_NH_Home_Mobile
from .Market_Study_AL_Home import Market_Study_AL_Home
from .Market_Study_AL_Home_Mobile import Market_Study_AL_Home_Mobile

def generate_market_studies(application):
    with anvil.server.no_loading_indicator:
        Functions.manipulate_loading_overlay(True)
        anvil.js.call('update_loading_bar', 10, 'Generating basic Information')
        Market_Study_Variables.reset_values()
        Market_Study_Variables.created_date = Functions.get_current_date_as_string()
        Market_Study_Variables.share_url = application.create_share_map('market_study')
        Variables.unique_code = anvil.server.call("get_unique_code")
    
        anvil.js.call('update_loading_bar', 25, 'Getting map related information')
        Market_Study_Variables.street = anvil.js.call('getSearchedAddress').split(",")[0]
        Market_Study_Variables.marker_coords = dict(Mapbox_Variables.location_marker['_lngLat'])
        Market_Study_Variables.purchase_power = anvil.server.call('get_purchasing_power', location=Market_Study_Variables.marker_coords)
        Market_Study_Variables.iso = dict(Mapbox_Variables.map.getSource('iso'))
        Market_Study_Variables.iso_time = application.time_dropdown.selected_value
        if Market_Study_Variables.iso_time == "-1":
            Market_Study_Variables.iso_time = "20"
        Market_Study_Variables.iso_movement = application.profile_dropdown.selected_value.lower()
        for point in Market_Study_Variables.iso['_data']['features'][0]['geometry']['coordinates'][0]:
            if point[0] < Market_Study_Variables.bounding_box[1] or Market_Study_Variables.bounding_box[1] == 0:
                Market_Study_Variables.bounding_box[1] = point[0]
            if point[0] > Market_Study_Variables.bounding_box[3] or Market_Study_Variables.bounding_box[3] == 0:
                Market_Study_Variables.bounding_box[3] = point[0]
            if point[1] < Market_Study_Variables.bounding_box[0] or Market_Study_Variables.bounding_box[0] == 0:
                Market_Study_Variables.bounding_box[0] = point[1]
            if point[1] > Market_Study_Variables.bounding_box[2] or Market_Study_Variables.bounding_box[2] == 0:
                Market_Study_Variables.bounding_box[2] = point[1]
    
        anvil.js.call('update_loading_bar', 40, 'Organizing Marker Data')
        Market_Study_Variables.coords_nh = organize_ca_data(Variables.nursing_homes_entries, 'nursing_homes', Market_Study_Variables.marker_coords, application, Functions)
        Market_Study_Variables.coords_al = organize_ca_data(Variables.assisted_living_entries, 'assisted_living', Market_Study_Variables.marker_coords, application, Functions)
        Market_Study_Variables.data_comp_analysis_nh = build_req_string(Market_Study_Variables.coords_nh, 'nursing_homes')
        Market_Study_Variables.data_comp_analysis_al = build_req_string(Market_Study_Variables.coords_al, 'assisted_living')
    
        anvil.js.call('update_loading_bar', 50, 'Calculating Market Study Data')
        for care_entry in Market_Study_Variables.data_comp_analysis_nh['data']:
            beds_amount = 0
        if not care_entry[0]['anz_vers_pat'] == '-':
            Market_Study_Variables.inpatients += int(care_entry[0]['anz_vers_pat'])
        if care_entry[0]['status'] == "aktiv":
            Market_Study_Variables.nursing_homes_active += 1
            if not care_entry[0]['platz_voll_pfl'] == "-":
                Market_Study_Variables.beds_active += int(care_entry[0]['platz_voll_pfl'])
                beds_amount = int(care_entry[0]['platz_voll_pfl'])
                Market_Study_Variables.beds.append(beds_amount)
        elif care_entry[0]['status'] == "in Planung":
            Market_Study_Variables.nursing_homes_planned += 1
            if not care_entry[0]['platz_voll_pfl'] == "-":
                Market_Study_Variables.beds_planned += int(care_entry[0]['platz_voll_pfl'])
        elif care_entry[0]['status'] == "im Bau":
            Market_Study_Variables.nursing_homes_construct += 1
            if not care_entry[0]['platz_voll_pfl'] == "-":
                Market_Study_Variables.beds_construct += int(care_entry[0]['platz_voll_pfl'])
        if not care_entry[0]['invest'] == "-":
            Market_Study_Variables.invest_cost.append(float(care_entry[0]['invest']))
        if not care_entry[0]['betreiber'] == "-":
            if care_entry[0]['type'] == "privat":
                if care_entry[0]['betreiber'] not in Market_Study_Variables.operator_private:
                    Market_Study_Variables.operator_private.append(care_entry[0]['betreiber'])
            elif care_entry[0]['type'] == "gemeinnützig":
                if care_entry[0]['betreiber'] not in Market_Study_Variables.operator_nonProfit:
                    Market_Study_Variables.operator_nonProfit.append(care_entry[0]['betreiber'])
            elif care_entry[0]['type'] == "kommunal":
                if care_entry[0]['betreiber'] not in Market_Study_Variables.operator_public:
                    Market_Study_Variables.operator_public.append(care_entry[0]['betreiber'])
            if care_entry[0]['betreiber'] not in Market_Study_Variables.operator:
                Market_Study_Variables.operator.append(care_entry[0]['betreiber'])
    
        location_request = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{Market_Study_Variables.marker_coords['lng']},{Market_Study_Variables.marker_coords['lat']}.json?access_token={Mapbox_Variables.token}"
        location_response = anvil.http.request(location_request, json=True)
        marker_context = location_response['features'][0]['context']
        for info in marker_context:
            if "postcode" in info['id']:
                Market_Study_Variables.zipcode = info['text']
            elif "locality" in info['id']:
                Market_Study_Variables.district = info['text']
            elif "place" in info['id']:
                Market_Study_Variables.city = info['text']
            elif "region" in info['id']:
                Market_Study_Variables.federal_state = info['text']
        if Market_Study_Variables.federal_state == "n.a.":
            Market_Study_Variables.federal_state = Market_Study_Variables.city
        if Market_Study_Variables.district == "n.a.":
            Market_Study_Variables.district = Market_Study_Variables.city
    
        Market_Study_Variables.countie_data = anvil.server.call("get_demographic_district_data", Market_Study_Variables.marker_coords)
        Market_Study_Variables.countie = Market_Study_Variables.countie_data['ex_dem_lk']['name'].split(',')
        Market_Study_Variables.people_u80 = int(Market_Study_Variables.countie_data['dem_fc_lk']['g_65tou70_2020_abs']) + int(Market_Study_Variables.countie_data['dem_fc_lk']['g_70tou80_2020_abs'])
        Market_Study_Variables.people_o80 = int(Market_Study_Variables.countie_data['dem_fc_lk']['g_80plus_2020_abs'])
        Market_Study_Variables.people_u80_fc = int(Market_Study_Variables.countie_data['dem_fc_lk']['g_65tou70_2030_abs']) + int(Market_Study_Variables.countie_data['dem_fc_lk']['g_70tou80_2030_abs'])
        Market_Study_Variables.people_o80_fc = int(Market_Study_Variables.countie_data['dem_fc_lk']['g_80plus_2030_abs'])
        Market_Study_Variables.people_u80_fc_35 = int(Market_Study_Variables.countie_data['dem_fc_lk']['g_65tou70_2035_abs']) + int(Market_Study_Variables.countie_data['dem_fc_lk']['g_70tou80_2035_abs'])
        Market_Study_Variables.people_o80_fc_35 = int(Market_Study_Variables.countie_data['dem_fc_lk']['g_80plus_2035_abs'])
        Market_Study_Variables.change_u80 = float("{:.2f}".format(((Market_Study_Variables.people_u80_fc * 100) / Market_Study_Variables.people_u80) - 100))
        Market_Study_Variables.change_o80 = float("{:.2f}".format(((Market_Study_Variables.people_o80_fc * 100) / Market_Study_Variables.people_o80) - 100))
        Market_Study_Variables.population_trend = "{:.1f}".format((Market_Study_Variables.people_u80_fc_35 + Market_Study_Variables.people_o80_fc_35) * 100 / (Market_Study_Variables.people_u80 + Market_Study_Variables.people_o80) - 100)
        Market_Study_Variables.nursing_home_rate = round(float(Market_Study_Variables.countie_data['pfleg_stat_lk']['heimquote2019']) * 100, 1)
        for key in Market_Study_Variables.keys:
            Market_Study_Variables.population_fc_30 += int(Market_Study_Variables.countie_data['dem_fc_lk'][f'{key}_2030_abs'])
            Market_Study_Variables.population_fc_35 += int(Market_Study_Variables.countie_data['dem_fc_lk'][f'{key}_2035_abs'])
    
        care_data_district = anvil.server.call("get_care_district_data", Market_Study_Variables.countie_data['ex_dem_lk']['key'])
        for el in care_data_district:
            Market_Study_Variables.inpatients_lk += int(el['number_of_patients_cared_for']) if el['number_of_patients_cared_for'] is not None else 0
            if el['number_of_places_fulltime_care'] is not None:
                Market_Study_Variables.beds_lk += int(el['number_of_places_fulltime_care'])
            Market_Study_Variables.occupancy_lk = round((Market_Study_Variables.inpatients_lk * 100) / Market_Study_Variables.beds_lk, 1)
            Market_Study_Variables.free_beds_lk = Market_Study_Variables.beds_lk - Market_Study_Variables.inpatients_lk
    
        Market_Study_Variables.new_r_care_rate_raw = float("{:.3f}".format(Market_Study_Variables.inpatients_lk / (Market_Study_Variables.people_u80 + Market_Study_Variables.people_o80)))
        Market_Study_Variables.new_care_rate_raw = round((Market_Study_Variables.inpatients_lk * 100 / round((Market_Study_Variables.nursing_home_rate * Market_Study_Variables.countie_data['ex_dem_lk']['all_compl']) + 1)) * 100, 1)
        Market_Study_Variables.pat_rec_full_care_fc_30_v1 = round(Market_Study_Variables.new_r_care_rate_raw * (Market_Study_Variables.people_u80_fc + Market_Study_Variables.people_o80_fc))
        Market_Study_Variables.care_rate_30_v1_raw = round((Market_Study_Variables.pat_rec_full_care_fc_30_v1 * 100 / (Market_Study_Variables.population_fc_30 * Market_Study_Variables.nursing_home_rate)) * 100, 1)
        Market_Study_Variables.pat_rec_full_care_fc_30_v2 = round((Market_Study_Variables.new_r_care_rate_raw + 0.003) * (Market_Study_Variables.people_u80_fc + Market_Study_Variables.people_o80_fc))
        Market_Study_Variables.care_rate_30_v2_raw = round((Market_Study_Variables.pat_rec_full_care_fc_30_v2 * 100 / (Market_Study_Variables.population_fc_30 * Market_Study_Variables.nursing_home_rate)) * 100, 1)
        Market_Study_Variables.pat_rec_full_care_fc_35_v1 = round(Market_Study_Variables.new_r_care_rate_raw * (Market_Study_Variables.people_u80_fc_35 + Market_Study_Variables.people_o80_fc_35))
        Market_Study_Variables.care_rate_35_v1_raw = round((Market_Study_Variables.pat_rec_full_care_fc_35_v1 * 100 / (Market_Study_Variables.population_fc_35 * Market_Study_Variables.nursing_home_rate)) * 100, 1)
        Market_Study_Variables.pat_rec_full_care_fc_35_v2 = round((Market_Study_Variables.new_r_care_rate_raw + 0.003) * (Market_Study_Variables.people_u80_fc_35 + Market_Study_Variables.people_o80_fc_35))
        Market_Study_Variables.care_rate_35_v2_raw = round((Market_Study_Variables.pat_rec_full_care_fc_35_v2 * 100 / (Market_Study_Variables.population_fc_35 * Market_Study_Variables.nursing_home_rate)) * 100, 1)
        Market_Study_Variables.inpatients_fc = round(Market_Study_Variables.pat_rec_full_care_fc_30_v1 * (round(((Market_Study_Variables.inpatients * 100) / Market_Study_Variables.inpatients_lk), 1) / 100)) if not Market_Study_Variables.inpatients_lk == 0 else 0
        Market_Study_Variables.inpatients_fc_v2 = round(Market_Study_Variables.pat_rec_full_care_fc_30_v2 * (round(((Market_Study_Variables.inpatients * 100) / Market_Study_Variables.inpatients_lk), 1) / 100)) if not Market_Study_Variables.inpatients_lk == 0 else 0
        Market_Study_Variables.inpatients_fc_35 = round(Market_Study_Variables.pat_rec_full_care_fc_35_v1 * (round(((Market_Study_Variables.inpatients * 100) / Market_Study_Variables.inpatients_lk), 1) / 100)) if not Market_Study_Variables.inpatients_lk == 0 else 0
        Market_Study_Variables.inpatients_fc_35_v2 = round(Market_Study_Variables.pat_rec_full_care_fc_35_v2 * (round(((Market_Study_Variables.inpatients * 100) / Market_Study_Variables.inpatients_lk), 1) / 100)) if not Market_Study_Variables.inpatients_lk == 0 else 0
        Market_Study_Variables.beds_30_v1 = round((Market_Study_Variables.pat_rec_full_care_fc_30_v1 / 0.95))
        Market_Study_Variables.beds_30_v2 = round((Market_Study_Variables.pat_rec_full_care_fc_30_v2 / 0.95))
        Market_Study_Variables.beds_35_v1 = round((Market_Study_Variables.pat_rec_full_care_fc_35_v1 / 0.95))
        Market_Study_Variables.beds_35_v2 = round((Market_Study_Variables.pat_rec_full_care_fc_35_v2 / 0.95))
        Market_Study_Variables.free_beds_30_v1 = Market_Study_Variables.beds_30_v1 - Market_Study_Variables.pat_rec_full_care_fc_30_v1
        Market_Study_Variables.free_beds_30_v2 = Market_Study_Variables.beds_30_v2 - Market_Study_Variables.pat_rec_full_care_fc_30_v2
        Market_Study_Variables.free_beds_35_v1 = Market_Study_Variables.beds_35_v1 - Market_Study_Variables.pat_rec_full_care_fc_35_v1
        Market_Study_Variables.free_beds_35_v2 = Market_Study_Variables.beds_35_v2 - Market_Study_Variables.pat_rec_full_care_fc_35_v2
    
        Market_Study_Variables.regulations = anvil.server.call('read_regulations', Market_Study_Variables.federal_state, "english")
        for index, competitor in enumerate(Market_Study_Variables.data_comp_analysis_nh['data']):
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
                if facility_rooms > 0:
                    facility_single_room_quote = facility_single_rooms / facility_rooms
                else:
                    facility_single_room_quote = 0
                facility_bed_amount = facility_single_rooms + facility_double_rooms * 2
                if not Market_Study_Variables.regulations['Existing']['sr_quote'] == '/':
                    facility_single_room_quote_future = float(Market_Study_Variables.regulations['Existing']['sr_quote'])
                else:
                    facility_single_room_quote_future = 0
                if not Market_Study_Variables.regulations['Existing']['max_beds'] == '/':
                    facility_max_beds_future = float(Market_Study_Variables.regulations['Existing']['max_beds'])
                else:
                    facility_max_beds_future = 999999
                if facility_single_room_quote < facility_single_room_quote_future or facility_bed_amount > facility_max_beds_future:
                    Market_Study_Variables.data_comp_analysis_nh['data'][index][0]['legal'] = "No"
                else:
                    Market_Study_Variables.data_comp_analysis_nh['data'][index][0]['legal'] = "Yes"
                if facility_single_room_quote < facility_single_room_quote_future:
                    facility_single_rooms_future = int(round(facility_rooms * facility_single_room_quote_future, 0))
                    facility_double_rooms_future = int(round(facility_rooms - facility_single_rooms_future, 0))
                    facility_bed_amount_future = int(
                        round(facility_single_rooms_future + facility_double_rooms_future * 2, 0))
                else:
                    facility_bed_amount_future = facility_bed_amount
                if facility_bed_amount_future > facility_max_beds_future:
                    facility_bed_amount_future = facility_max_beds_future
                Market_Study_Variables.facilities_bed_amount += facility_bed_amount
                Market_Study_Variables.facilities_bed_amount_future += facility_bed_amount_future
            else:
                Market_Study_Variables.data_comp_analysis_nh['data'][index][0]['legal'] = "-"
    
        Market_Study_Variables.loss_of_beds = Market_Study_Variables.facilities_bed_amount_future - Market_Study_Variables.facilities_bed_amount
        Market_Study_Variables.beds_adjusted_30_v1 = Market_Study_Variables.beds_active + Market_Study_Variables.beds_planned + Market_Study_Variables.beds_construct + Market_Study_Variables.loss_of_beds
        Market_Study_Variables.beds_adjusted_30_v2 = Market_Study_Variables.beds_active + Market_Study_Variables.beds_planned + Market_Study_Variables.beds_construct + Market_Study_Variables.loss_of_beds
        Market_Study_Variables.beds_adjusted_35_v1 = Market_Study_Variables.beds_active + Market_Study_Variables.beds_planned + Market_Study_Variables.beds_construct + Market_Study_Variables.loss_of_beds
        Market_Study_Variables.beds_adjusted_35_v2 = Market_Study_Variables.beds_active + Market_Study_Variables.beds_planned + Market_Study_Variables.beds_construct + Market_Study_Variables.loss_of_beds
        Market_Study_Variables.beds_surplus_35 = Market_Study_Variables.beds_adjusted_35_v1 - Market_Study_Variables.inpatients_fc_35
        Market_Study_Variables.beds_surplus_35_v2 = Market_Study_Variables.beds_adjusted_35_v2 - Market_Study_Variables.inpatients_fc_35_v2
        Market_Study_Variables.beds_surplus = Market_Study_Variables.beds_adjusted_30_v1 - Market_Study_Variables.inpatients_fc
        Market_Study_Variables.beds_surplus_v2 = Market_Study_Variables.beds_adjusted_30_v2 - Market_Study_Variables.inpatients_fc_v2
    
        anvil.js.call('update_loading_bar', 80, 'Generating Market Studies')
        Functions.manipulate_loading_overlay(False)
        versions = alert(Market_Study_Language(), buttons=[], dismissible=False, large=True, role='custom_alert')
        Functions.manipulate_loading_overlay(True)
        for version_index, version in enumerate(versions):
            anvil.js.call('update_loading_bar', 80 + 5 + 10 * (version_index - 1), f'Generating {version} Market Study')
            Market_Study_Variables.regulations = anvil.server.call('read_regulations', Market_Study_Variables.federal_state, version)
            generate_nursing_home_pages(version)
            generate_assisted_living_pages(version)
            create_market_study(application, version, version_index)
        anvil.js.call('update_loading_bar', 0, '')
        Functions.manipulate_loading_overlay(False)

def generate_nursing_home_pages(version):
  with anvil.server.no_loading_indicator:
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
    mdk_grade_letters = ['A', 'B', 'C', 'D']
    
    for index, competitor in enumerate(Market_Study_Variables.data_comp_analysis_nh['data']):
      if index % 9 == 0:
        if index > 0:
          Market_Study_Variables.competitor_pages[f'competitor_analysis_{Market_Study_Variables.page}'] = current_competitor_page
          Market_Study_Variables.page += 1
          Market_Study_Variables.current_competitor_analysis_page += 1
        current_competitor_page = copy.deepcopy(Nursing_Homes_Competitor_Skeleton.nursing_homes_competitor_skeleton_en if version == "english" else Nursing_Homes_Competitor_Skeleton.nursing_homes_competitor_skeleton_de)
        current_competitor_page['page_number'] = Market_Study_Variables.current_competitor_analysis_page
        current_competitor_page['text']['heading_city']['txt'] = Market_Study_Variables.city
        current_competitor_page['image']['location_map']['path'] = f"tmp/map_image_{Variables.unique_code}.png"
        current_page_height = 177
  
      top_30_operator = anvil.server.call("read_top_30", competitor[0]['raw_betreiber'])
      operator_type = competitor[0]['type']
      status = competitor[0]['status']
      legal = competitor[0]['legal']
      if version == "german":
        top_30_operator = "Nein" if top_30_operator == "No" else "Ja"
        legal = "Nein" if legal == "No" else "Ja"
        if operator_type == "gemeinnützig":
          operator_type_size = 7
        else:
          operator_type_size = 8
      elif version == "english":
        operator_type = "private" if operator_type == "privat" else "non-profit" if operator_type == "gemeinnützig" else "public"
        operator_type_size = 8
        status = "active" if status == "aktiv" else "planning" if status == "in Planung" else "construction"
    
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
          'color': [0, 176, 240] if "keine " not in competitor[0]['web'] else [0, 0, 0],
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
          'link': competitor[0]['web'] if "keine " not in competitor[0]['web'] else ""
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
          'txt': top_30_operator,
          'align': 'center',
          'fill': True,
        }
        current_competitor_page['cell'][f'home_{home_counter}_operator_type'] = {
          'color': [0, 0, 0],
          'fill_color': [244, 239, 220],
          'font': 'segoeui',
          'size': operator_type_size,
          'x': 77,
          'y': current_page_height,
          'w': 12,
          'h': 6,
          'txt': operator_type,
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
          'txt': status,
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
          'txt': competitor[0]['baujahr'] if competitor[0]['baujahr'] is not None else '-',
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
          'txt': legal,
          'align': 'center',
          'fill': True,
        }
  
        if not competitor[0]['legal'] == '-':
          if competitor[0]['legal'] == 'Yes':
            Market_Study_Variables.complied_regulations += 1
          else:
            Market_Study_Variables.uncomplied_regulations += 1
        if competitor[0]['type'] == 'privat':
          Market_Study_Variables.private_operator_nh += 1
          if not competitor[0]['invest'] == '-':
            Market_Study_Variables.invest_costs_private.append(float(competitor[0]['invest']))
            Market_Study_Variables.invest_costs_private_home = float(competitor[0]['invest'])
        elif competitor[0]['type'] == 'kommunal':
          Market_Study_Variables.public_operator_nh += 1
          if not competitor[0]['invest'] == '-':
            Market_Study_Variables.invest_costs_public.append(float(competitor[0]['invest']))
            Market_Study_Variables.invest_costs_public_home = float(competitor[0]['invest'])
        elif competitor[0]['type'] == 'gemeinnützig':
          Market_Study_Variables.none_profit_operator_nh += 1
          if not competitor[0]['invest'] == '-':
            Market_Study_Variables.invest_costs_non_profit.append(float(competitor[0]['invest']))
            Market_Study_Variables.invest_costs_non_profit_home = float(competitor[0]['invest'])
        if not competitor[0]['ez'] == '-' and competitor[0]['ez'] is not None:
          single_rooms = int(competitor[0]['ez'])
        else:
          single_rooms = '-'
        if not competitor[0]['dz'] == '-' and competitor[0]['dz'] is not None:
          double_rooms = int(competitor[0]['dz'])
        else:
          double_rooms = '-'
        if not competitor[0]['platz_voll_pfl'] == '-' and competitor[0]['platz_voll_pfl'] is not None:
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
          Market_Study_Variables.list_beds.append(beds)
        if not single_rooms == '-':
          total_single_rooms += single_rooms
        if not double_rooms == '-':
          total_double_rooms += double_rooms
        if not rooms == '-':
          total_rooms += rooms
        if not single_room_quote == '-':
          list_single_room_quota.append(single_room_quote)
        if not competitor[0]['occupancy'] == '-' and not competitor[0]['occupancy'] == 'N.A.':
          list_occupancy_rate.append(competitor[0]['occupancy'])
        if not competitor[0]['invest'] == '-' and not competitor[0]['invest'] == 'N.A.':
          list_invest_cost.append(float(competitor[0]['invest']))
          Market_Study_Variables.home_invest = float(competitor[0]['invest'])
        if not competitor[0]['mdk_note'] == '-' and not competitor[0]['mdk_note'] == 'N.A.':
          list_mdk_grade.append(mdk_grade_letters.index(competitor[0]['mdk_note']) + 1)
        if not competitor[0]['baujahr'] == '-' and not competitor[0]['baujahr'] == 'N.A.':
          Market_Study_Variables.list_years_of_construction_nh.append(int(competitor[0]['baujahr']))
        if not competitor[0]['invest'] == '-' and not competitor[0]['invest'] == 'N.A.' and not competitor[0]['baujahr'] == '-' and not competitor[0]['baujahr'] == 'N.A.':
          Market_Study_Variables.invest_plot_data.append(['home', competitor[0]['invest'], competitor[0]['baujahr'], '⌂'])
  
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
          'txt': '{:,}'.format(double_rooms) if not double_rooms == '-' else double_rooms,
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
          'txt': '{:,}'.format(rooms) if not rooms == '-' else rooms,
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
          'txt': '{:,}%'.format(single_room_quote) if not single_room_quote == '-' else single_room_quote,
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
          'txt': '{:,}%'.format(round(competitor[0]['occupancy'] * 100, 1)) if not competitor[0]['occupancy'] == '-' else '-',
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
            'txt': '-' if competitor[0]['mdk_note'] == 'N.A.' else '-' if competitor[0]['mdk_note'] is None else competitor[0]['mdk_note'],
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
          'color': [0, 176, 240] if competitor[0]['web'] is not None and "keine " not in competitor[0]['web'] else [0, 0, 0],
          'font': 'segoeui',
          'size': 8,
          'x': 17,
          'y': current_page_height,
          'w': 50,
          'h': 6,
          'txt': competitor[0]['raw_name'] if len(competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
          'align': 'left',
          'link': competitor[0]['web'] if competitor[0]['web'] is not None and "keine " not in competitor[0]['web'] else ""
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
          'txt': top_30_operator,
          'align': 'center',
        }
        current_competitor_page['cell'][f'competitor_{table_position}_type'] = {
          'color': [0, 0, 0],
          'font': 'segoeui',
          'size': operator_type_size,
          'x': 77,
          'y': current_page_height,
          'w': 12,
          'h': 6,
          'txt': operator_type,
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
          'txt': status,
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
          'txt': competitor[0]['baujahr'] if competitor[0]['baujahr'] is not None else '-',
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
          'txt': legal,
          'align': 'center',
        }
  
        if competitor[0]['legal'] is not None:
          if competitor[0]['legal'] == 'Yes':
            Market_Study_Variables.complied_regulations += 1
          else:
            Market_Study_Variables.uncomplied_regulations += 1
        if competitor[0]['type'] == 'privat':
          Market_Study_Variables.private_operator_nh += 1
          if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-':
            Market_Study_Variables.invest_costs_private.append(float(competitor[0]['invest']))
        elif competitor[0]['type'] == 'kommunal':
          Market_Study_Variables.public_operator_nh += 1
          if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-':
            Market_Study_Variables.invest_costs_public.append(float(competitor[0]['invest']))
        elif competitor[0]['type'] == 'gemeinnützig':
          Market_Study_Variables.none_profit_operator_nh += 1
          if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-':
            Market_Study_Variables.invest_costs_non_profit.append(float(competitor[0]['invest']))
        if competitor[0]['ez'] is not None:
          single_rooms = int(competitor[0]['ez'])
        else:
          single_rooms = '-'
        if competitor[0]['dz'] is not None:
          double_rooms = int(competitor[0]['dz'])
        else:
          double_rooms = '-'
        if competitor[0]['platz_voll_pfl'] is not None:
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
          Market_Study_Variables.list_beds.append(beds)
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
        if not competitor[0]['mdk_note'] == 'N.A.' and competitor[0]['mdk_note'] is not None:
          list_mdk_grade.append(mdk_grade_letters.index(competitor[0]['mdk_note']) + 1)
        if competitor[0]['baujahr'] is not None:
          Market_Study_Variables.list_years_of_construction_nh.append(int(competitor[0]['baujahr']))
        if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-' and competitor[0]['baujahr'] is not None and not competitor[0]['baujahr'] == '-':
          Market_Study_Variables.invest_plot_data.append(["private" if competitor[0]['type'] == "privat" else "non-profit" if competitor[0]['type'] == "gemeinnützig" else "public", competitor[0]['invest'], competitor[0]['baujahr'], prev_competitor_index])
  
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
          'txt': '{:,}%'.format(round(competitor[0]['occupancy'] * 100, 1)) if not competitor[0]['occupancy'] == '-' else competitor[0]['occupancy'],
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
          'txt': '-' if competitor[0]['mdk_note'] == 'N.A.' else '-' if competitor[0]['mdk_note'] is None else competitor[0]['mdk_note'],
          'align': 'center',
        }
  
      current_page_height += 12

      if index == len(Market_Study_Variables.data_comp_analysis_nh['data']) - 1:
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
        if len(list_occupancy_rate) > 0:
          total_occupancy_rate = median_dictionary['occupancy_rate']
        if len(list_invest_cost) > 0:
          Market_Study_Variables.minimum_invest_cost = min(list_invest_cost)
        if len(list_invest_cost) > 0:
          Market_Study_Variables.maximum_invest_cost = max(list_invest_cost)
        if len(list_invest_cost) > 0:
          Market_Study_Variables.total_invest_cost = median_dictionary['invest_cost']
        if len(list_mdk_grade) > 0:
          total_mdk_grade = median_dictionary['mdk_grade']
  
        current_competitor_page['cell']['competitor_sum_beds'] = {
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
        current_competitor_page['cell']['competitor_sum_single_rooms'] = {
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
        current_competitor_page['cell']['competitor_sum_double_rooms'] = {
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
        current_competitor_page['cell']['competitor_sum_rooms'] = {
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
        current_competitor_page['cell']['competitor_median_single_room_quota'] = {
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
        current_competitor_page['cell']['competitor_median_occupancy'] = {
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
        current_competitor_page['cell']['competitor_median_invest'] = {
          'color': [0, 0, 0],
          'font': 'seguisb',
          'size': 8,
          'x': 183,
          'y': 285,
          'w': 10,
          'h': 6,
          'txt': 'x̃ {:,}'.format(round(Market_Study_Variables.total_invest_cost, 2)),
          'align': 'center',
        }
        current_competitor_page['cell']['competitor_median_quality'] = {
          'color': [0, 0, 0],
          'font': 'seguisb',
          'size': 8,
          'x': 193,
          'y': 285,
          'w': 10,
          'h': 6,
          'txt': mdk_grade_letters[int(total_mdk_grade) - 1],
          'align': 'center',
        }
      
        Market_Study_Variables.competitor_pages[f'competitor_analysis_{Market_Study_Variables.page}'] = current_competitor_page

def generate_assisted_living_pages(version):
  with anvil.server.no_loading_indicator:
    home_counter = 0
    prev_competitor_distance = 0
    prev_competitor_index = 0
  
    for index, competitor in enumerate(Market_Study_Variables.data_comp_analysis_al['data']):
      if index % 9 == 0:
        if index > 0:
          Market_Study_Variables.competitor_pages[f'competitor_analysis_{Market_Study_Variables.page}'] = current_competitor_page
          Market_Study_Variables.page += 1
          Market_Study_Variables.current_competitor_analysis_page += 1
        current_competitor_page = copy.deepcopy(Assisted_Living_Competitor_Skeleton.assisted_living_competitor_skeleton_en if version == "english" else Assisted_Living_Competitor_Skeleton.assisted_living_competitor_skeleton_de)
        current_competitor_page['page_number'] = Market_Study_Variables.current_competitor_analysis_page
        current_competitor_page['text']['heading_city']['txt'] = Market_Study_Variables.city
        current_competitor_page['image']['location_map']['path'] = f"tmp/map_image_{Variables.unique_code}.png"
        current_page_height = 177
  
      top_30_operator = anvil.server.call("read_top_30", competitor[0]['raw_betreiber'])
      operator_type = competitor[0]['raw_type']
      status = competitor[0]['status']
      if version == "german":
        top_30_operator = "Nein" if top_30_operator == "No" else "Ja"
        if operator_type == "gemeinnützig":
          operator_type_size = 7
        else:
          operator_type_size = 8
      elif version == "english":
        operator_type = "private" if operator_type == "privat" else "non-profit" if operator_type == "gemeinnützig" else "public"
        operator_type_size = 8
        status = "active" if status == "aktiv" else "planning" if status == "in Planung" else "construction"
    
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
          'color': [0, 176, 240] if "keine " not in competitor[0]['web'] else [0, 0, 0],
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
          'link': competitor[0]['web'] if "keine " not in competitor[0]['web'] else ""
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
          'txt': top_30_operator,
          'align': 'center',
          'fill': True,
        }
        current_competitor_page['cell'][f'home_{home_counter}_operator_type'] = {
          'color': [0, 0, 0],
          'fill_color': [244, 239, 220],
          'font': 'segoeui',
          'size': operator_type_size,
          'x': 77,
          'y': current_page_height,
          'w': 12,
          'h': 6,
          'txt': operator_type,
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
          'txt': status,
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
          'txt': competitor[0]['year_of_construction'] if competitor[0]['year_of_construction'] is not None else '-',
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
          Market_Study_Variables.list_years_of_construction_al.append(int(competitor[0]['year_of_construction']))
        if competitor[0]['type'] == 'gemeinnützig':
          Market_Study_Variables.none_profit_operator_al += 1
        elif competitor[0]['type'] == 'kommunal':
          Market_Study_Variables.public_operator_al += 1
        elif competitor[0]['type'] == 'privat':
          Market_Study_Variables.private_operator_al += 1
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
          'color': [0, 176, 240] if competitor[0]['web'] is not None and "keine " not in competitor[0]['web'] else [0, 0, 0],
          'font': 'segoeui',
          'size': 8,
          'x': 17,
          'y': current_page_height,
          'w': 50,
          'h': 6,
          'txt': competitor[0]['raw_name'] if len(competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
          'align': 'left',
          'link': competitor[0]['web'] if competitor[0]['web'] is not None and "keine " not in competitor[0]['web'] else ""
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
          'txt': top_30_operator,
          'align': 'center',
        }
        current_competitor_page['cell'][f'competitor_{table_position}_operator_type'] = {
          'color': [0, 0, 0],
          'font': 'segoeui',
          'size': operator_type_size,
          'x': 77,
          'y': current_page_height,
          'w': 12,
          'h': 6,
          'txt': operator_type,
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
          'txt': status,
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
          'txt': competitor[0]['year_of_construction'] if competitor[0]['year_of_construction'] is not None else '-',
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
          'txt': '{:,}'.format(int(competitor[0]['number_apts'])) if competitor[0]['number_apts'] is not None else '-',
          'align': 'center',
        }
  
        if competitor[0]['year_of_construction'] is not None:
          Market_Study_Variables.list_years_of_construction_al.append(int(competitor[0]['year_of_construction']))
        if competitor[0]['type'] == 'gemeinnützig':
          Market_Study_Variables.none_profit_operator_al += 1
        elif competitor[0]['type'] == 'kommunal':
          Market_Study_Variables.public_operator_al += 1
        elif competitor[0]['type'] == 'privat':
          Market_Study_Variables.private_operator_al += 1
  
      current_page_height += 12
  
      if index == len(Market_Study_Variables.data_comp_analysis_al['data']) - 1:
        Market_Study_Variables.competitor_pages[f'competitor_analysis_{Market_Study_Variables.page}'] = current_competitor_page

def create_market_study(self, version, version_index):
  Market_Study_Variables.analysis_text_response = anvil.server.call('openai_test', Market_Study_Variables.city, version)
  Functions.manipulate_loading_overlay(False)
  Market_Study_Variables.final_analysis_text = alert(ChatGPT(generated_text=Market_Study_Variables.analysis_text_response), buttons=[], dismissible=False, large=True, role='custom_alert')
  Functions.manipulate_loading_overlay(True)

  if version == "german":
    if Market_Study_Variables.iso_movement == "walking":
      Market_Study_Variables.iso_string = f"{Market_Study_Variables.iso_time} Minuten zu Fuß"
    elif Market_Study_Variables.iso_movement == "cycling":
      Market_Study_Variables.iso_string = f"{Market_Study_Variables.iso_time} Minuten fahren - Fahrrad"
    elif Market_Study_Variables.iso_movement == "driving":
      Market_Study_Variables.iso_string = f"{Market_Study_Variables.iso_time} Minuten fahren - Auto"
    market_study_data = Market_Study_Skeleton.market_study_skeleton_de({
      'street': Market_Study_Variables.street,
      'zipcode': Market_Study_Variables.zipcode,
      'city': Market_Study_Variables.city,
      'district': Market_Study_Variables.district,
      'federal_state': Market_Study_Variables.federal_state,
      'iso_string': Market_Study_Variables.iso_string,
      'created_date': Market_Study_Variables.created_date,
      'purchase_power': Market_Study_Variables.purchase_power,
      'population_trend': Market_Study_Variables.population_trend,
      'beds_surplus_35_v2': Market_Study_Variables.beds_surplus_35_v2,
      'countie': Market_Study_Variables.countie[0],
      'population_city_2020': Market_Study_Variables.countie_data['dem_city']['bevoelkerung_ges'],
      'population_county_2020': Market_Study_Variables.countie_data['ex_dem_lk']['all_compl'],
      'people_u80': Market_Study_Variables.people_u80,
      'people_o80': Market_Study_Variables.people_o80,
      'new_care_rate_raw': Market_Study_Variables.new_care_rate_raw,
      'nursing_home_rate': Market_Study_Variables.nursing_home_rate,
      'inpatients_lk': Market_Study_Variables.inpatients_lk,
      'occupancy_lk': Market_Study_Variables.occupancy_lk,
      'beds_lk': Market_Study_Variables.beds_lk,
      'free_beds_lk': Market_Study_Variables.free_beds_lk,
      'nursing_homes_active': Market_Study_Variables.nursing_homes_active,
      'beds_active': Market_Study_Variables.beds_active,
      'nursing_homes_planned': Market_Study_Variables.nursing_homes_planned,
      'nursing_homes_construct': Market_Study_Variables.nursing_homes_construct,
      'beds_planned': Market_Study_Variables.beds_planned,
      'beds_construct': Market_Study_Variables.beds_construct,
      'inpatients': Market_Study_Variables.inpatients,
      'population_fc_30': Market_Study_Variables.population_fc_30,
      'people_u80_fc': Market_Study_Variables.people_u80_fc,
      'people_o80_fc': Market_Study_Variables.people_o80_fc,
      'care_rate_30_v1_raw': Market_Study_Variables.care_rate_30_v1_raw,
      'pat_rec_full_care_fc_30_v1': Market_Study_Variables.pat_rec_full_care_fc_30_v1,
      'beds_30_v1': Market_Study_Variables.beds_30_v1,
      'free_beds_30_v1': Market_Study_Variables.free_beds_30_v1,
      'loss_of_beds': Market_Study_Variables.loss_of_beds,
      'beds_adjusted_30_v1': Market_Study_Variables.beds_adjusted_30_v1,
      'inpatients_fc': Market_Study_Variables.inpatients_fc,
      'beds_surplus': Market_Study_Variables.beds_surplus,
      'care_rate_30_v2_raw': Market_Study_Variables.care_rate_30_v2_raw,
      'pat_rec_full_care_fc_30_v2': Market_Study_Variables.pat_rec_full_care_fc_30_v2,
      'beds_30_v2': Market_Study_Variables.beds_30_v2,
      'free_beds_30_v2': Market_Study_Variables.free_beds_30_v2,
      'beds_adjusted_30_v2': Market_Study_Variables.beds_adjusted_30_v2,
      'inpatients_fc_v2': Market_Study_Variables.inpatients_fc_v2,
      'beds_surplus_v2': Market_Study_Variables.beds_surplus_v2,
      'population_fc_35': Market_Study_Variables.population_fc_35,
      'people_u80_fc_35': Market_Study_Variables.people_u80_fc_35,
      'people_o80_fc_35': Market_Study_Variables.people_o80_fc_35,
      'care_rate_35_v1_raw': Market_Study_Variables.care_rate_35_v1_raw,
      'pat_rec_full_care_fc_35_v1': Market_Study_Variables.pat_rec_full_care_fc_35_v1,
      'beds_35_v1': Market_Study_Variables.beds_35_v1,
      'free_beds_35_v1': Market_Study_Variables.free_beds_35_v1,
      'beds_adjusted_35_v1': Market_Study_Variables.beds_adjusted_35_v1,
      'inpatients_fc_35': Market_Study_Variables.inpatients_fc_35,
      'beds_surplus_35': Market_Study_Variables.beds_surplus_35,
      'care_rate_35_v2_raw': Market_Study_Variables.care_rate_35_v2_raw,
      'pat_rec_full_care_fc_35_v2': Market_Study_Variables.pat_rec_full_care_fc_35_v2,
      'beds_35_v2': Market_Study_Variables.beds_35_v2,
      'free_beds_35_v2': Market_Study_Variables.free_beds_35_v2,
      'beds_adjusted_35_v2': Market_Study_Variables.beds_adjusted_35_v2,
      'inpatients_fc_35_v2': Market_Study_Variables.inpatients_fc_35_v2,
      'analysis_text': Market_Study_Variables.final_analysis_text,
      'number_facilities_nh_value': len(Market_Study_Variables.data_comp_analysis_nh['data']),
      'number_facilities_al_value': len(Market_Study_Variables.data_comp_analysis_al['data']),
      'minimum_invest_cost': Market_Study_Variables.minimum_invest_cost,
      'maximum_invest_cost': Market_Study_Variables.maximum_invest_cost,
      'total_invest_cost': Market_Study_Variables.total_invest_cost,
      'home_invest': Market_Study_Variables.home_invest,
      'regulations': Market_Study_Variables.regulations,
      'complied_regulations': Market_Study_Variables.complied_regulations,
      'uncomplied_regulations': Market_Study_Variables.uncomplied_regulations,
      'share_url': Market_Study_Variables.share_url,
    })
  elif version == "english":
    Market_Study_Variables.iso_string = f"{Market_Study_Variables.iso_time} minutes {Market_Study_Variables.iso_movement}"
    market_study_data = Market_Study_Skeleton.market_study_skeleton_en({
      'street': Market_Study_Variables.street,
      'zipcode': Market_Study_Variables.zipcode,
      'city': Market_Study_Variables.city,
      'district': Market_Study_Variables.district,
      'federal_state': Market_Study_Variables.federal_state,
      'iso_string': Market_Study_Variables.iso_string,
      'created_date': Market_Study_Variables.created_date,
      'purchase_power': Market_Study_Variables.purchase_power,
      'population_trend': Market_Study_Variables.population_trend,
      'beds_surplus_35_v2': Market_Study_Variables.beds_surplus_35_v2,
      'countie': Market_Study_Variables.countie[0],
      'population_city_2020': Market_Study_Variables.countie_data['dem_city']['bevoelkerung_ges'],
      'population_county_2020': Market_Study_Variables.countie_data['ex_dem_lk']['all_compl'],
      'people_u80': Market_Study_Variables.people_u80,
      'people_o80': Market_Study_Variables.people_o80,
      'new_care_rate_raw': Market_Study_Variables.new_care_rate_raw,
      'nursing_home_rate': Market_Study_Variables.nursing_home_rate,
      'inpatients_lk': Market_Study_Variables.inpatients_lk,
      'occupancy_lk': Market_Study_Variables.occupancy_lk,
      'beds_lk': Market_Study_Variables.beds_lk,
      'free_beds_lk': Market_Study_Variables.free_beds_lk,
      'nursing_homes_active': Market_Study_Variables.nursing_homes_active,
      'beds_active': Market_Study_Variables.beds_active,
      'nursing_homes_planned': Market_Study_Variables.nursing_homes_planned,
      'nursing_homes_construct': Market_Study_Variables.nursing_homes_construct,
      'beds_planned': Market_Study_Variables.beds_planned,
      'beds_construct': Market_Study_Variables.beds_construct,
      'inpatients': Market_Study_Variables.inpatients,
      'population_fc_30': Market_Study_Variables.population_fc_30,
      'people_u80_fc': Market_Study_Variables.people_u80_fc,
      'people_o80_fc': Market_Study_Variables.people_o80_fc,
      'care_rate_30_v1_raw': Market_Study_Variables.care_rate_30_v1_raw,
      'pat_rec_full_care_fc_30_v1': Market_Study_Variables.pat_rec_full_care_fc_30_v1,
      'beds_30_v1': Market_Study_Variables.beds_30_v1,
      'free_beds_30_v1': Market_Study_Variables.free_beds_30_v1,
      'loss_of_beds': Market_Study_Variables.loss_of_beds,
      'beds_adjusted_30_v1': Market_Study_Variables.beds_adjusted_30_v1,
      'inpatients_fc': Market_Study_Variables.inpatients_fc,
      'beds_surplus': Market_Study_Variables.beds_surplus,
      'care_rate_30_v2_raw': Market_Study_Variables.care_rate_30_v2_raw,
      'pat_rec_full_care_fc_30_v2': Market_Study_Variables.pat_rec_full_care_fc_30_v2,
      'beds_30_v2': Market_Study_Variables.beds_30_v2,
      'free_beds_30_v2': Market_Study_Variables.free_beds_30_v2,
      'beds_adjusted_30_v2': Market_Study_Variables.beds_adjusted_30_v2,
      'inpatients_fc_v2': Market_Study_Variables.inpatients_fc_v2,
      'beds_surplus_v2': Market_Study_Variables.beds_surplus_v2,
      'population_fc_35': Market_Study_Variables.population_fc_35,
      'people_u80_fc_35': Market_Study_Variables.people_u80_fc_35,
      'people_o80_fc_35': Market_Study_Variables.people_o80_fc_35,
      'care_rate_35_v1_raw': Market_Study_Variables.care_rate_35_v1_raw,
      'pat_rec_full_care_fc_35_v1': Market_Study_Variables.pat_rec_full_care_fc_35_v1,
      'beds_35_v1': Market_Study_Variables.beds_35_v1,
      'free_beds_35_v1': Market_Study_Variables.free_beds_35_v1,
      'beds_adjusted_35_v1': Market_Study_Variables.beds_adjusted_35_v1,
      'inpatients_fc_35': Market_Study_Variables.inpatients_fc_35,
      'beds_surplus_35': Market_Study_Variables.beds_surplus_35,
      'care_rate_35_v2_raw': Market_Study_Variables.care_rate_35_v2_raw,
      'pat_rec_full_care_fc_35_v2': Market_Study_Variables.pat_rec_full_care_fc_35_v2,
      'beds_35_v2': Market_Study_Variables.beds_35_v2,
      'free_beds_35_v2': Market_Study_Variables.free_beds_35_v2,
      'beds_adjusted_35_v2': Market_Study_Variables.beds_adjusted_35_v2,
      'inpatients_fc_35_v2': Market_Study_Variables.inpatients_fc_35_v2,
      'analysis_text': Market_Study_Variables.final_analysis_text,
      'number_facilities_nh_value': len(Market_Study_Variables.data_comp_analysis_nh['data']),
      'number_facilities_al_value': len(Market_Study_Variables.data_comp_analysis_al['data']),
      'minimum_invest_cost': Market_Study_Variables.minimum_invest_cost,
      'maximum_invest_cost': Market_Study_Variables.maximum_invest_cost,
      'total_invest_cost': Market_Study_Variables.total_invest_cost,
      'home_invest': Market_Study_Variables.home_invest,
      'regulations': Market_Study_Variables.regulations,
      'complied_regulations': Market_Study_Variables.complied_regulations,
      'uncomplied_regulations': Market_Study_Variables.uncomplied_regulations,
      'share_url': Market_Study_Variables.share_url,
    })

  max_pages = 3
  for page in Market_Study_Variables.competitor_pages:
      market_study_data['pages'][page] = Market_Study_Variables.competitor_pages[page]
      Market_Study_Variables.market_study_pages.append(page)
      max_pages += 1

  max_pages += 4
  Market_Study_Variables.market_study_pages.append('good_to_know')
  Market_Study_Variables.market_study_pages.append('regulations')
  Market_Study_Variables.market_study_pages.append('methodic')
  Market_Study_Variables.market_study_pages.append('contact')
  market_study_data['number_of_pages'] = max_pages
  market_study_data['pages']['good_to_know']['page_number'] = max_pages - 3
  market_study_data['pages']['regulations']['page_number'] = max_pages - 2
  market_study_data['pages']['methodic']['page_number'] = max_pages - 1
  market_study_data['pages']['contact']['page_number'] = max_pages
  
  good_to_know_median = anvil.server.call(
      'get_multiple_median',
      {
          'beds': Market_Study_Variables.list_beds,
          'years_of_construction_nh': Market_Study_Variables.list_years_of_construction_nh,
          'years_of_construction_al': Market_Study_Variables.list_years_of_construction_al
      }
  )
  
  market_study_data['pages']['good_to_know']['cell']['median_beds_value']['txt'] = str(good_to_know_median['beds'])
  market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_value']['txt'] = str(int(good_to_know_median['years_of_construction_nh'])) if not good_to_know_median['years_of_construction_nh'] == '-' else good_to_know_median['years_of_construction_nh']
  market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_al_value']['txt'] = str(int(good_to_know_median['years_of_construction_al'])) if not good_to_know_median['years_of_construction_al'] == '-' else good_to_know_median['years_of_construction_al']

  competitor_map_request_data = self.build_competitor_map_request(
      Market_Study_Variables.coords_nh,
      Variables.home_address_nh,
      Market_Study_Variables.coords_al,
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
          'nursing_home_data': [Market_Study_Variables.none_profit_operator_nh, Market_Study_Variables.public_operator_nh, Market_Study_Variables.private_operator_nh],
          'assisted_living_data': [Market_Study_Variables.none_profit_operator_al, Market_Study_Variables.public_operator_al, Market_Study_Variables.private_operator_al]
      },
      'invest_cost_overall': Market_Study_Variables.invest_plot_data,
      'purchasing_power': Market_Study_Variables.purchase_power,
      'invest_cost_public': {
          'data': Market_Study_Variables.invest_costs_public,
          'home': Market_Study_Variables.invest_costs_public_home
      },
      'invest_cost_non_profit': {
          'data': Market_Study_Variables.invest_costs_non_profit,
          'home': Market_Study_Variables.invest_costs_non_profit_home
      },
      'invest_cost_private': {
          'data': Market_Study_Variables.invest_costs_private,
          'home': Market_Study_Variables.invest_costs_private_home
      },
  }

  anvil.server.call(
      'generate_market_study_pdf',
      market_study_data,  # Dictionary of Data to fill Market Study PDF
      Market_Study_Variables.bounding_box,  # Bounding Box of the Map
      Variables.unique_code,  # Unique creation Code for current Market Study
      Market_Study_Variables.market_study_pages,  # Ordered List of Pages inside Market Study
      competitor_map_request,  # Request Data for Competitor Map
      Variables.activeIso,  # Data of current Iso Layer
      Market_Study_Variables.marker_coords,  # Coordinates of Map Marker
      chart_data,  # Data to create all needed charts
      version  # Language Version of Market Study
  )

  anvil.js.call('update_loading_bar', 80 + 10 * version_index, 'Download Market Study')
  market_study = app_tables.pictures.search()[0]
  anvil.media.download(market_study['pic'])

def organize_ca_data(entries, topic, marker_coords, self, Functions):
  with anvil.server.no_loading_indicator:
    # Create Variables
    counter = 0
    data_comp_analysis = []
    coords = []

    if topic == 'nursing_homes':
      Variables.home_address_nh = []
    else:
      Variables.home_address_al = []

    for entry in entries:
      added = False
      if topic == "nursing_homes":
        lat_entry = "%.6f" % float(entry['latitude'])
        lng_entry = "%.6f" % float(entry['longitude'])
      else:
        lat_entry = "%.6f" % float(entry['latitude'])
        lng_entry = "%.6f" % float(entry['longitude'])
      for icon in Variables.activeIcons[topic]:
        if not added:
          lng_icon = "%.6f" % icon['_lngLat']['lng']
          lat_icon = "%.6f" % icon['_lngLat']['lat']
          if lng_entry == lng_icon and lat_entry == lat_icon:
              coords.append([lng_icon, lat_icon])
              counter += 1
              
              if topic == "nursing_homes":
                anz_vers_pat = int(entry['number_of_patients_cared_for']) if entry['number_of_patients_cared_for'] is not None else "-"
                platz_voll_pfl = int(entry['number_of_places_fulltime_care']) if entry['number_of_places_fulltime_care'] is not None else "-"
                  
                if not anz_vers_pat == "-" and not platz_voll_pfl == "-":
                  occupancy_raw = anz_vers_pat / platz_voll_pfl
                  if occupancy_raw > 1:
                    occupancy_raw = 1
                else:
                  occupancy_raw = "-"
                  
                if entry['invest'] is not None:
                  if len(entry['invest']) == 4:
                    if entry['invest'].index(".") == 2:
                      invest = entry['invest'] + "0"
                    else:
                      invest = entry['invest']
                  else:
                    invest = entry['invest']
                else:
                  invest = "-"

                mdk_report = json.loads(entry['mdk_report'])
                mdk_blacklist = ['report_date', 'data_date', 'result_ventilation', 'result_vegetative_state', 'result_palliative_concept', 'result_palliativ_outsourcing', 'result_palliativ_last_wishes', 'result_palliativ_authority_known', 'result_palliativ_inform_relatives']
                mdk_letters = ['A', 'B', 'C', 'D']
                mdk_grade = 0
                mdk_count = 0
                for key in mdk_report:
                  if key not in mdk_blacklist and mdk_report[key] is not None:
                    mdk_grade += int(mdk_report[key])
                    mdk_count += 1
                if not mdk_count == 0:
                  mdk_grade = int(mdk_grade / mdk_count) - 1
                  mdk_letter_grade = mdk_letters[mdk_grade]
                else:
                  mdk_letter_grade = 'N.A.'
                
                data = {
                  "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_name": entry['name'],
                  "platz_voll_pfl": platz_voll_pfl,
                  "ez": entry['single_rooms'],
                  "dz": entry['double_rooms'],
                  "anz_vers_pat": anz_vers_pat,
                  "occupancy": occupancy_raw,
                  "baujahr": entry['year_of_construction'],
                  "status": entry['status'],
                  "betreiber": entry['operator'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_betreiber": entry['operator'],
                  "invest": invest,
                  "mdk_note": mdk_letter_grade,
                  "coords": [lng_icon, lat_icon],
                  "web": entry['domain'],
                  "type": entry['type']
                }
                data_comp_analysis.append(data)
                added = True
              elif topic == "assisted_living":
                data = {
                  "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_name": entry['name'],
                  "operator": entry['operator'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_betreiber": entry['operator'],
                  "type": entry['type'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_type": entry['type'],
                  "city": entry['city'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_city": entry['city'],
                  "status": entry['status'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                  "raw_status": entry['status'],
                  "number_apts": entry['apartments'],
                  "coords": [lng_icon, lat_icon],
                  "web": entry['domain'],
                  "year_of_construction": entry['year_of_construction']
                }
                data_comp_analysis.append(data)
                added = True

    # Sort Coordinates by Distance
    sorted_coords = anvil.server.call("get_distance", marker_coords, data_comp_analysis)
    from .Market_Study_Existing_Home import Market_Study_Existing_Home
    for entry in sorted_coords:
      if entry[1] <= 0.01:
        Functions.manipulate_loading_overlay(False)
        res = alert(content=Market_Study_Existing_Home(entry=entry, topic=topic), dismissible=False, large=True, buttons=[], role='custom_alert')
        Functions.manipulate_loading_overlay(True)
        if res == 'Yes':
          if topic == 'nursing_homes':
            Variables.home_address_nh.append(entry)
          else:
            Variables.home_address_al.append(entry)
      
    if topic == 'nursing_homes':
      if len(Variables.home_address_nh) == 0:
        from .Market_Study_NH_Home import Market_Study_NH_Home
        from .Market_Study_NH_Home_Mobile import Market_Study_NH_Home_Mobile
        Functions.manipulate_loading_overlay(False)
        if self.mobile:
          Variables.home_address_nh = alert(content=Market_Study_NH_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        else:
          Variables.home_address_nh = alert(content=Market_Study_NH_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        Functions.manipulate_loading_overlay(True)
        if not Variables.home_address_nh == []:
          sorted_coords.insert(0, Variables.home_address_nh)
    else:
      if Variables.home_address_al == []:
        from .Market_Study_AL_Home import Market_Study_AL_Home
        from .Market_Study_AL_Home_Mobile import Market_Study_AL_Home_Mobile
        Functions.manipulate_loading_overlay(False)
        if self.mobile:
          Variables.home_address_al = alert(content=Market_Study_AL_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        else:
          Variables.home_address_al = alert(content=Market_Study_AL_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        Functions.manipulate_loading_overlay(True)
        if not Variables.home_address_al == []:
          sorted_coords.insert(0, Variables.home_address_al)

    res_data = {'sorted_coords': sorted_coords[:30], 'marker_coords': marker_coords}
    
    return res_data

def build_req_string(res_data, topic):
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
      request_static_map_raw = "%7B%22type%22%3A%22FeatureCollection%22%2C%22features%22%3A%5B"
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
          if 'home' not in coordinate:
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
              if not coordinate[0]['coords'] == last_coords and 'home' not in coordinate:
                if not counter == 1:
                  request_static_map += "%2C"
                request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D"
              counter = 0
              if not request_static_map == request_static_map_raw:
                request_static_map += "%2C"
              url = 'https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/PinCBx075.png'
              encoded_url = url.replace("/", "%2F")
              request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
              request.append(request_static_map)
              request_static_map = request_static_map_raw
              index_coords -= 1
            elif counter == 10:
              if 'home' not in coordinate:
                if not coordinate[0]['coords'] == last_coords:
                  request_static_map += f"%2C%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D%5D%7D"
                  counter = 0
                  request.append(request_static_map)
                  request_static_map = request_static_map_raw
              index_coords -= 1
            elif 'home' not in coordinate:
              if not coordinate[0]['coords'] == last_coords:
                if not counter == 1:
                  request_static_map += "%2C"
                request_static_map += f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{coordinate[0]['coords'][0]},{coordinate[0]['coords'][1]}%5D%7D%7D"
              index_coords -= 1
            else:
              request_static_map += "%5D%7D"
              counter = 0
              request.append(request_static_map)
              request_static_map = request_static_map_raw
              break
          last_coord_dist = coordinate[1]
            
          complete_counter += 1
          last_coords = coordinate[0]['coords']
      
      if request == []:
        url = "https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/PinCBx075.png"
        encoded_url = url.replace("/", "%2F")
        request_static_map = request_static_map_raw + f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
        request.append(request_static_map)
        request_static_map = request_static_map_raw
      
      return({"data": res_data['sorted_coords'], "request": request, "request2": Variables.activeIso})