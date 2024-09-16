import anvil.server
from anvil.tables import app_tables
from .. import Variables, Functions, Mapbox_Variables
from anvil import alert
import json, copy
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
        anvil.js.call('update_loading_bar', 10, 'Initialising Data')
        market_study_dictionary = {
            'created_date': Functions.get_current_date_as_string(),
            'share_url': application.create_share_map('market_study'),
            'unique_code': anvil.server.call("get_unique_code"),
            'marker_coords': dict(Mapbox_Variables.location_marker['_lngLat']),
            'iso': [[key, value] for key, value in dict(Mapbox_Variables.map.getSource('iso')['_data']['features'][0]['geometry']['coordinates'][0]).items()],
            'iso_time': application.time_dropdown.selected_value if not application.time_dropdown.selected_value == "-1" else "20",
            'iso_movement': application.profile_dropdown.selected_value.lower(),
            'inpatients': 0,
            'nursing_homes_active': 0,
            'beds_active': 0,
            'nursing_homes_planned': 0,
            'beds_planned': 0,
            'nursing_homes_construct': 0,
            'beds_construct': 0,
            'invest_cost': [],
            'operator_private': [],
            'operator_non_profit': [],
            'operator_public': [],
            'operator': [],
            'population_fc_30': 0,
            'population_fc_35': 0,
            'inpatients_lk': 0,
            'beds_lk': 0,
            'facilities_bed_amount': 0,
            'facilities_bed_amount_future': 0,
            'home_counter': 0,
            'total_beds': 0,
            'total_single_rooms': 0,
            'total_double_rooms': 0,
            'total_rooms': 0,
            'list_single_room_quota': [],
            'list_occupancy_rate': [],
            'list_invest_cost': [],
            'list_mdk_grade': [],
            'prev_competitor_distance': 0,
            'prev_competitor_index': 0,
            'beds_building_lk': 0,
            'beds_planning_lk': 0
        }

        market_study_dictionary['bounding_box'] = get_bounding_box(market_study_dictionary['iso'])
        market_study_dictionary['coords_nh'] = organize_ca_data(
            entries=Variables.nursing_homes_entries,
            topic='nursing_homes',
            marker_coords=market_study_dictionary['marker_coords'],
            application=application
        )
        market_study_dictionary['coords_al'] = organize_ca_data(
            entries=Variables.assisted_living_entries,
            topic='assisted_living',
            marker_coords=market_study_dictionary['marker_coords'],
            application=application
        )

        ''' Diese beiden Funktionsaufrufe inklusive der Funktion selbst sind vollkommen unnötig und werden nirgendswo benutzt. Ich habs aber noch nicht gelöscht weil ich keinen Bock hatte die Variablenbenutzung zu ändern. Schönen Gruß von Vergangenheits-Kevin (est. 30.05.2024) '''
        market_study_dictionary['data_comp_analysis_nh'] = build_req_string(
            res_data=market_study_dictionary['coords_nh'],
            topic='nursing_homes'
        )
        market_study_dictionary['data_comp_analysis_al'] = build_req_string(
            res_data=market_study_dictionary['coords_al'],
            topic='assisted_living'
        )
        ''' Hier endet der Code-Müll (Vorerst, wer weiß was Ur-Vergangenheits-Kevin noch so angestellt hat.) '''

        anvil.js.call('update_loading_bar', 25, 'Requesting Location Information')
        market_study_dictionary['purchase_power'] = anvil.server.call('get_purchasing_power', location=market_study_dictionary['marker_coords'])
        
        location_request = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{market_study_dictionary['marker_coords']['lng']},{market_study_dictionary['marker_coords']['lat']}.json?access_token={Mapbox_Variables.token}"
        location_response = anvil.http.request(location_request, json=True)

        market_study_dictionary['marker_context'] = location_response['features'][0]['context']
        market_study_dictionary['street'] = f"{location_response['features'][0]['text']} {location_response['features'][0]['address'] if 'address' in location_response['features'][0] else ''}"
        market_study_dictionary['federal_state'] = "n.a."
        market_study_dictionary['district'] = "n.a."
        for info in market_study_dictionary['marker_context']:
            if "postcode" in info['id']:
                market_study_dictionary['zipcode'] = info['text']
            elif "district" in info['id']:
                market_study_dictionary['district'] = info['text']
            elif "place" in info['id']:
                market_study_dictionary['city'] = info['text']
            elif "region" in info['id']:
                market_study_dictionary['federal_state'] = info['text']
        if market_study_dictionary['federal_state'] == "n.a.":
            market_study_dictionary['federal_state'] = market_study_dictionary['city']
        if market_study_dictionary['district'] == "n.a.":
            market_study_dictionary['district'] = market_study_dictionary['city']
        
        ##### Temporary Fix #####
        if market_study_dictionary['city'] == "Fürstenwalde":
            countie_data_city = "Fürstenwalde/Spree"
        else:
            countie_data_city = market_study_dictionary['city']
        ##### Temporary Fix #####

        market_study_dictionary['countie_data'] = anvil.server.call(
            "get_demographic_district_data",
            city=countie_data_city
        )
        market_study_dictionary['care_data_district'] = anvil.server.call("get_care_district_data", dist_key=market_study_dictionary['countie_data']['ex_dem_lk']['key'])
        market_study_dictionary['regulations'] = anvil.server.call('read_regulations', federal_state=market_study_dictionary['federal_state'], version="english")

        anvil.js.call('update_loading_bar', 30, 'Calculating Market Study Data')
        for care_entry in market_study_dictionary['data_comp_analysis_nh']['data']:
            market_study_dictionary['inpatients'] += int(care_entry[0]['anz_vers_pat']) if not care_entry[0]['anz_vers_pat'] == '-' else 0
            if care_entry[0]['status'] == "aktiv":
                market_study_dictionary['nursing_homes_active'] += 1
                market_study_dictionary['beds_active'] += int(care_entry[0]['platz_voll_pfl']) if not care_entry[0]['platz_voll_pfl'] == "-" else 0
            elif care_entry[0]['status'] == "in Planung":
                market_study_dictionary['nursing_homes_planned'] += 1
                market_study_dictionary['beds_planned'] += int(care_entry[0]['platz_voll_pfl']) if not care_entry[0]['platz_voll_pfl'] == "-" else 0
            elif care_entry[0]['status'] == "im Bau":
                market_study_dictionary['nursing_homes_construct'] += 1
                market_study_dictionary['beds_construct'] += int(care_entry[0]['platz_voll_pfl']) if not care_entry[0]['platz_voll_pfl'] == "-" else 0
            if not care_entry[0]['invest'] == "-":
                market_study_dictionary['invest_cost'].append(float(care_entry[0]['invest']))
            if not care_entry[0]['betreiber'] == "-":
                if care_entry[0]['type'] == "privat" and care_entry[0]['betreiber'] not in market_study_dictionary['operator_private']:
                    market_study_dictionary['operator_private'].append(care_entry[0]['betreiber'])
                elif care_entry[0]['type'] == "gemeinnützig" and care_entry[0]['betreiber'] not in market_study_dictionary['operator_non_profit']:
                    market_study_dictionary['operator_non_profit'].append(care_entry[0]['betreiber'])
                elif care_entry[0]['type'] == "kommunal" and care_entry[0]['betreiber'] not in market_study_dictionary['operator_public']:
                    market_study_dictionary['operator_public'].append(care_entry[0]['betreiber'])
                if care_entry[0]['betreiber'] not in market_study_dictionary['operator']:
                    market_study_dictionary['operator'].append(care_entry[0]['betreiber'])

        keys = ['g_u6', 'g_6tou10', 'g_10tou16', 'g_16tou20', 'g_20tou30', 'g_30tou50', 'g_50tou65', 'g_65tou70', 'g_70tou80', 'g_80plus']
        market_study_dictionary['countie'] = market_study_dictionary['countie_data']['ex_dem_lk']['name'].split(',')[0]
        market_study_dictionary['people_u80'] = int(market_study_dictionary['countie_data']['dem_fc_lk']['g_65tou70_2020_abs']) + int(market_study_dictionary['countie_data']['dem_fc_lk']['g_70tou80_2020_abs'])
        market_study_dictionary['people_o80'] = int(market_study_dictionary['countie_data']['dem_fc_lk']['g_80plus_2020_abs'])
        market_study_dictionary['people_u80_fc'] = int(market_study_dictionary['countie_data']['dem_fc_lk']['g_65tou70_2030_abs']) + int(market_study_dictionary['countie_data']['dem_fc_lk']['g_70tou80_2030_abs'])
        market_study_dictionary['people_o80_fc'] = int(market_study_dictionary['countie_data']['dem_fc_lk']['g_80plus_2030_abs'])
        market_study_dictionary['people_u80_fc_35'] = int(market_study_dictionary['countie_data']['dem_fc_lk']['g_65tou70_2035_abs']) + int(market_study_dictionary['countie_data']['dem_fc_lk']['g_70tou80_2035_abs'])
        market_study_dictionary['people_o80_fc_35'] = int(market_study_dictionary['countie_data']['dem_fc_lk']['g_80plus_2035_abs'])
        market_study_dictionary['change_u80'] = float("{:.2f}".format(((market_study_dictionary['people_u80_fc'] * 100) / market_study_dictionary['people_u80']) - 100))
        market_study_dictionary['change_o80'] = float("{:.2f}".format(((market_study_dictionary['people_o80_fc'] * 100) / market_study_dictionary['people_o80']) - 100))
        market_study_dictionary['population_trend'] = "{:.1f}".format((market_study_dictionary['people_u80_fc_35'] + market_study_dictionary['people_o80_fc_35']) * 100 / (market_study_dictionary['people_u80'] + market_study_dictionary['people_o80']) - 100)
        market_study_dictionary['nursing_home_rate'] = round(float(market_study_dictionary['countie_data']['pfleg_stat_lk']['heimquote2019']) * 100, 1)
        for key in keys:
            market_study_dictionary['population_fc_30'] += int(market_study_dictionary['countie_data']['dem_fc_lk'][f'{key}_2030_abs'])
            market_study_dictionary['population_fc_35'] += int(market_study_dictionary['countie_data']['dem_fc_lk'][f'{key}_2035_abs'])

        for el in market_study_dictionary['care_data_district']:
            market_study_dictionary['inpatients_lk'] += int(el['number_of_patients_cared_for']) if el['number_of_patients_cared_for'] is not None else 0
            if el['status'] == 'aktiv':
                market_study_dictionary['beds_lk'] += int(el['number_of_places_fulltime_care']) if el['number_of_places_fulltime_care'] is not None else 0
            elif el['status'] == 'im Bau':
                market_study_dictionary['beds_building_lk'] += int(el['number_of_places_fulltime_care']) if el['number_of_places_fulltime_care'] is not None else 0
            elif el['status'] == 'in Planung':
                market_study_dictionary['beds_planning_lk'] += int(el['number_of_places_fulltime_care']) if el['number_of_places_fulltime_care'] is not None else 0

        market_study_dictionary['occupancy_lk'] = round((market_study_dictionary['inpatients_lk'] * 100) / market_study_dictionary['beds_lk'], 1)
        market_study_dictionary['free_beds_lk'] = market_study_dictionary['beds_lk'] - market_study_dictionary['inpatients_lk']

        market_study_dictionary['new_r_care_rate_raw'] = float("{:.3f}".format(market_study_dictionary['inpatients_lk'] / (market_study_dictionary['people_u80'] + market_study_dictionary['people_o80'])))
        market_study_dictionary['new_care_rate_raw'] = round((market_study_dictionary['inpatients_lk'] * 100 / round((market_study_dictionary['nursing_home_rate'] * market_study_dictionary['countie_data']['ex_dem_lk']['all_compl']) + 1)) * 100, 1)
        market_study_dictionary['pat_rec_full_care_fc_30_v1'] = round(market_study_dictionary['new_r_care_rate_raw'] * (market_study_dictionary['people_u80_fc'] + market_study_dictionary['people_o80_fc']))
        market_study_dictionary['care_rate_30_v1_raw'] = round((market_study_dictionary['pat_rec_full_care_fc_30_v1'] * 100 / (market_study_dictionary['population_fc_30'] * market_study_dictionary['nursing_home_rate'])) * 100, 1)
        market_study_dictionary['pat_rec_full_care_fc_30_v2'] = round((market_study_dictionary['new_r_care_rate_raw'] + 0.003) * (market_study_dictionary['people_u80_fc'] + market_study_dictionary['people_o80_fc']))
        market_study_dictionary['care_rate_30_v2_raw'] = round((market_study_dictionary['pat_rec_full_care_fc_30_v2'] * 100 / (market_study_dictionary['population_fc_30'] * market_study_dictionary['nursing_home_rate'])) * 100, 1)
        market_study_dictionary['pat_rec_full_care_fc_35_v1'] = round(market_study_dictionary['new_r_care_rate_raw'] * (market_study_dictionary['people_u80_fc_35'] + market_study_dictionary['people_o80_fc_35']))
        market_study_dictionary['care_rate_35_v1_raw'] = round((market_study_dictionary['pat_rec_full_care_fc_35_v1'] * 100 / (market_study_dictionary['population_fc_35'] * market_study_dictionary['nursing_home_rate'])) * 100, 1)
        market_study_dictionary['pat_rec_full_care_fc_35_v2'] = round((market_study_dictionary['new_r_care_rate_raw'] + 0.003) * (market_study_dictionary['people_u80_fc_35'] + market_study_dictionary['people_o80_fc_35']))
        market_study_dictionary['care_rate_35_v2_raw'] = round((market_study_dictionary['pat_rec_full_care_fc_35_v2'] * 100 / (market_study_dictionary['population_fc_35'] * market_study_dictionary['nursing_home_rate'])) * 100, 1)
        market_study_dictionary['inpatients_fc'] = round(market_study_dictionary['pat_rec_full_care_fc_30_v1'] * (round(((market_study_dictionary['inpatients'] * 100) / market_study_dictionary['inpatients_lk']), 1) / 100)) if not market_study_dictionary['inpatients_lk'] == 0 else 0
        market_study_dictionary['inpatients_fc_v2'] = round(market_study_dictionary['pat_rec_full_care_fc_30_v2'] * (round(((market_study_dictionary['inpatients'] * 100) / market_study_dictionary['inpatients_lk']), 1) / 100)) if not market_study_dictionary['inpatients_lk'] == 0 else 0
        market_study_dictionary['inpatients_fc_35'] = round(market_study_dictionary['pat_rec_full_care_fc_35_v1'] * (round(((market_study_dictionary['inpatients'] * 100) / market_study_dictionary['inpatients_lk']), 1) / 100)) if not market_study_dictionary['inpatients_lk'] == 0 else 0
        market_study_dictionary['inpatients_fc_35_v2'] = round(market_study_dictionary['pat_rec_full_care_fc_35_v2'] * (round(((market_study_dictionary['inpatients'] * 100) / market_study_dictionary['inpatients_lk']), 1) / 100)) if not market_study_dictionary['inpatients_lk'] == 0 else 0
        
        ''' Current Version '''
        # market_study_dictionary['beds_30_v1'] = round((market_study_dictionary['pat_rec_full_care_fc_30_v1'] / 0.95))
        # market_study_dictionary['beds_30_v2'] = round((market_study_dictionary['pat_rec_full_care_fc_30_v2'] / 0.95))
        # market_study_dictionary['beds_35_v1'] = round((market_study_dictionary['pat_rec_full_care_fc_35_v1'] / 0.95))
        # market_study_dictionary['beds_35_v2'] = round((market_study_dictionary['pat_rec_full_care_fc_35_v2'] / 0.95))
        ''' 2030 im Bau / 2035 in Planung '''
        market_study_dictionary['beds_30_v1'] = market_study_dictionary['beds_lk'] + market_study_dictionary['beds_building_lk']
        market_study_dictionary['beds_30_v2'] = market_study_dictionary['beds_lk'] + market_study_dictionary['beds_building_lk']
        market_study_dictionary['beds_35_v1'] = market_study_dictionary['beds_30_v1'] + market_study_dictionary['beds_planning_lk']
        market_study_dictionary['beds_35_v2'] = market_study_dictionary['beds_30_v2'] + market_study_dictionary['beds_planning_lk']
        
        market_study_dictionary['free_beds_30_v1'] = market_study_dictionary['beds_30_v1'] - market_study_dictionary['pat_rec_full_care_fc_30_v1']
        market_study_dictionary['free_beds_30_v2'] = market_study_dictionary['beds_30_v2'] - market_study_dictionary['pat_rec_full_care_fc_30_v2']
        market_study_dictionary['free_beds_35_v1'] = market_study_dictionary['beds_35_v1'] - market_study_dictionary['pat_rec_full_care_fc_35_v1']
        market_study_dictionary['free_beds_35_v2'] = market_study_dictionary['beds_35_v2'] - market_study_dictionary['pat_rec_full_care_fc_35_v2']
        market_study_dictionary['occupancy_lk_30_v1'] = round(market_study_dictionary['pat_rec_full_care_fc_30_v1'] * 100 / market_study_dictionary['beds_30_v1'], 1)
        market_study_dictionary['occupancy_lk_30_v2'] = round(market_study_dictionary['pat_rec_full_care_fc_30_v2'] * 100 / market_study_dictionary['beds_30_v2'], 1)
        market_study_dictionary['occupancy_lk_35_v1'] = round(market_study_dictionary['pat_rec_full_care_fc_35_v1'] * 100 / market_study_dictionary['beds_35_v1'], 1)
        market_study_dictionary['occupancy_lk_35_v2'] = round(market_study_dictionary['pat_rec_full_care_fc_35_v2'] * 100 / market_study_dictionary['beds_35_v2'], 1)
        
        for index, competitor in enumerate(market_study_dictionary['data_comp_analysis_nh']['data']):
            if not competitor[0]['ez'] == '-' or not competitor[0]['dz'] == '-':
                market_study_dictionary['facility_single_rooms'] = int(competitor[0]['ez']) if not competitor[0]['ez'] == '-' and competitor[0]['ez'] is not None else 0
                market_study_dictionary['facility_double_rooms'] = int(competitor[0]['dz']) if not competitor[0]['dz'] == '-' and competitor[0]['dz'] is not None else 0
                market_study_dictionary['facility_rooms'] = market_study_dictionary['facility_single_rooms'] + market_study_dictionary['facility_double_rooms']
                market_study_dictionary['facility_single_room_quote'] = market_study_dictionary['facility_single_rooms'] / market_study_dictionary['facility_rooms'] if market_study_dictionary['facility_rooms'] > 0 else 0
                market_study_dictionary['facility_bed_amount'] = market_study_dictionary['facility_single_rooms'] + market_study_dictionary['facility_double_rooms'] * 2
                market_study_dictionary['facility_single_room_quote_future'] = float(market_study_dictionary['regulations']['Existing']['sr_quote']) if not market_study_dictionary['regulations']['Existing']['sr_quote'] == '/' else 0
                market_study_dictionary['facility_max_beds_future'] = float(market_study_dictionary['regulations']['Existing']['max_beds']) if not market_study_dictionary['regulations']['Existing']['max_beds'] == '/' else 999999
                market_study_dictionary['data_comp_analysis_nh']['data'][index][0]['legal'] = "No" if market_study_dictionary['facility_single_room_quote'] < market_study_dictionary['facility_single_room_quote_future'] or market_study_dictionary['facility_bed_amount'] > market_study_dictionary['facility_max_beds_future'] else "Yes"
                if market_study_dictionary['facility_single_room_quote'] < market_study_dictionary['facility_single_room_quote_future']:
                    market_study_dictionary['facility_single_rooms_future'] = int(round(market_study_dictionary['facility_rooms'] * market_study_dictionary['facility_single_room_quote_future'], 0))
                    market_study_dictionary['facility_double_rooms_future'] = int(round(market_study_dictionary['facility_rooms'] - market_study_dictionary['facility_single_rooms_future'], 0))
                    market_study_dictionary['facility_bed_amount_future'] = int(round(market_study_dictionary['facility_single_rooms_future'] + market_study_dictionary['facility_double_rooms_future'] * 2, 0))
                else:
                    market_study_dictionary['facility_bed_amount_future'] = market_study_dictionary['facility_bed_amount']
                market_study_dictionary['facilities_bed_amount'] += market_study_dictionary['facility_bed_amount']
                market_study_dictionary['facilities_bed_amount_future'] += market_study_dictionary['facility_bed_amount_future']
            else:
                market_study_dictionary['data_comp_analysis_nh']['data'][index][0]['legal'] = "-"

        market_study_dictionary['loss_of_beds'] = market_study_dictionary['facilities_bed_amount_future'] - market_study_dictionary['facilities_bed_amount']
        market_study_dictionary['beds_adjusted_30_v1'] = market_study_dictionary['beds_active'] + market_study_dictionary['beds_planned'] + market_study_dictionary['beds_construct'] + market_study_dictionary['loss_of_beds']
        market_study_dictionary['beds_adjusted_30_v2'] = market_study_dictionary['beds_active'] + market_study_dictionary['beds_planned'] + market_study_dictionary['beds_construct'] + market_study_dictionary['loss_of_beds']
        market_study_dictionary['beds_adjusted_35_v1'] = market_study_dictionary['beds_active'] + market_study_dictionary['beds_planned'] + market_study_dictionary['beds_construct'] + market_study_dictionary['loss_of_beds']
        market_study_dictionary['beds_adjusted_35_v2'] = market_study_dictionary['beds_active'] + market_study_dictionary['beds_planned'] + market_study_dictionary['beds_construct'] + market_study_dictionary['loss_of_beds']
        market_study_dictionary['beds_surplus_35'] = market_study_dictionary['beds_adjusted_35_v1'] - market_study_dictionary['inpatients_fc_35']
        market_study_dictionary['beds_surplus_35_v2'] = market_study_dictionary['beds_adjusted_35_v2'] - market_study_dictionary['inpatients_fc_35_v2']
        market_study_dictionary['beds_surplus'] = market_study_dictionary['beds_adjusted_30_v1'] - market_study_dictionary['inpatients_fc']
        market_study_dictionary['beds_surplus_v2'] = market_study_dictionary['beds_adjusted_30_v2'] - market_study_dictionary['inpatients_fc_v2']

        anvil.js.call('update_loading_bar', 60, 'Generating Market Studies')
        Functions.manipulate_loading_overlay(False)
        versions = alert(Market_Study_Language(), buttons=[], dismissible=False, large=True, role='custom_alert')
        Functions.manipulate_loading_overlay(True)
        for version_index, version in enumerate(versions):
            anvil.js.call('update_loading_bar', 80 + 10 * version_index, f'Generating {version} Market Study')
            market_study_dictionary_language = copy.deepcopy(market_study_dictionary)
            market_study_dictionary_language['regulations'] = anvil.server.call('read_regulations', market_study_dictionary['federal_state'], version)
            market_study_dictionary_nh = generate_nursing_home_pages(version=version, market_study_dictionary=copy.deepcopy(market_study_dictionary_language))
            market_study_dictionary_final = generate_assisted_living_pages(version=version, market_study_dictionary=copy.deepcopy(market_study_dictionary_nh))
            create_market_study(application=application, version=version, version_index=version_index, market_study_dictionary=copy.deepcopy(market_study_dictionary_final))
        anvil.js.call('update_loading_bar', 0, '')
        Functions.manipulate_loading_overlay(False)


def get_bounding_box(coordinates):
    bounding_box = [0, 0, 0, 0]
    for point in coordinates:
        if point[0] < bounding_box[1] or bounding_box[1] == 0:
            bounding_box[1] = point[0]
        if point[0] > bounding_box[3] or bounding_box[3] == 0:
            bounding_box[3] = point[0]
        if point[1] < bounding_box[0] or bounding_box[0] == 0:
            bounding_box[0] = point[1]
        if point[1] > bounding_box[2] or bounding_box[2] == 0:
            bounding_box[2] = point[1]

    return bounding_box


def organize_ca_data(entries, topic, marker_coords, application):
    with anvil.server.no_loading_indicator:
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

                            if (not anz_vers_pat == "-") and (not anz_vers_pat == 0) and (not platz_voll_pfl == "-") and (not platz_voll_pfl == 0):
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
                            mdk_blacklist = ['report_date', 'data_date', 'result_ventilation',
                                             'result_vegetative_state', 'result_palliative_concept',
                                             'result_palliativ_outsourcing', 'result_palliativ_last_wishes',
                                             'result_palliativ_authority_known', 'result_palliativ_inform_relatives']
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
                                "name": entry['name'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;") if entry['name'] is not None else "-",
                                "raw_name": entry['name'],
                                "operator": "-" if entry['operator'] is None else entry['operator'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;"),
                                "raw_betreiber": entry['operator'],
                                "type": entry['type'].replace("ä", "&auml;").replace("ö", "&ouml;").replace("ü", "&uuml").replace("Ä", "&Auml;").replace("Ö", "&Ouml;").replace("Ü", "&Uuml").replace("ß", "&szlig").replace("’", "&prime;").replace("–", "&ndash;") if entry['type'] is not None else "-",
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
                Functions.manipulate_loading_overlay(False)
                if application.mobile:
                    Variables.home_address_nh = alert(content=Market_Study_NH_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
                else:
                    Variables.home_address_nh = alert(content=Market_Study_NH_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
                Functions.manipulate_loading_overlay(True)
                if not Variables.home_address_nh == []:
                    sorted_coords.insert(0, Variables.home_address_nh)
        else:
            if len(Variables.home_address_al) == 0:
                Functions.manipulate_loading_overlay(False)
                if application.mobile:
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

        # Build Request-String for Mapbox Static-Map-API
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

        if len(request) == 0:
            url = "https%3A%2F%2Fraw.githubusercontent.com/ShinyKampfkeule/geojson_germany/main/PinCBx075.png"
            encoded_url = url.replace("/", "%2F")
            request_static_map = request_static_map_raw + f"%7B%22type%22%3A%22Feature%22%2C%22properties%22%3A%7B%22marker%2Durl%22%3A%22{encoded_url}%22%7D%2C%22geometry%22%3A%7B%22type%22%3A%22Point%22%2C%22coordinates%22%3A%5B{res_data['marker_coords']['lng']},{res_data['marker_coords']['lat']}%5D%7D%7D%5D%7D"
            request.append(request_static_map)
            request_static_map = request_static_map_raw

        return {"data": res_data['sorted_coords'], "request": request, "request2": Variables.activeIso}


def generate_nursing_home_pages(version, market_study_dictionary):
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
        market_study_dictionary['current_competitor_analysis_page'] = 1
        market_study_dictionary['complied_regulations'] = 0
        market_study_dictionary['private_operator_nh'] = 0
        market_study_dictionary['uncomplied_regulations'] = 0
        market_study_dictionary['public_operator_nh'] = 0
        market_study_dictionary['non_profit_operator_nh'] = 0
        market_study_dictionary['invest_costs_private'] = []
        market_study_dictionary['invest_costs_public'] = []
        market_study_dictionary['invest_costs_non_profit'] = []
        market_study_dictionary['list_beds'] = []
        market_study_dictionary['list_years_of_construction_nh'] = []
        market_study_dictionary['invest_plot_data'] = []
        market_study_dictionary['competitor_pages'] = {}
        market_study_dictionary['page'] = 0
        market_study_dictionary['invest_costs_public_home'] = -1
        market_study_dictionary['invest_costs_non_profit_home'] = -1
        market_study_dictionary['invest_costs_private_home'] = -1
        market_study_dictionary['home_invest'] = -1
        market_study_dictionary['minimum_invest_cost'] = 0
        market_study_dictionary['maximum_invest_cost'] = 0
        market_study_dictionary['total_invest_cost'] = 0
        total_mdk_grade = 0
        total_occupancy_rate = 0
        total_single_room_quota = 0

        for index, competitor in enumerate(market_study_dictionary['data_comp_analysis_nh']['data']):
            if index % 9 == 0:
                if index > 0:
                    market_study_dictionary['competitor_pages'][f"competitor_analysis_{market_study_dictionary['page']}"] = current_competitor_page
                    market_study_dictionary['page'] += 1
                    market_study_dictionary['current_competitor_analysis_page'] += 1
                current_competitor_page = copy.deepcopy(Nursing_Homes_Competitor_Skeleton.nursing_homes_competitor_skeleton_en if version == "english" else Nursing_Homes_Competitor_Skeleton.nursing_homes_competitor_skeleton_de)
                current_competitor_page['page_number'] = market_study_dictionary['current_competitor_analysis_page']
                current_competitor_page['text']['heading_city']['txt'] = market_study_dictionary['city']
                current_competitor_page['image']['location_map']['path'] = f"tmp/map_image_{market_study_dictionary['unique_code']}.png"
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
                    'txt': competitor[0]['raw_name'] if len(
                        competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
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
                    'txt': competitor[0]['raw_betreiber'] if len(
                        competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
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
                        market_study_dictionary['complied_regulations'] += 1
                    else:
                        market_study_dictionary['uncomplied_regulations'] += 1
                if competitor[0]['type'] == 'privat':
                    market_study_dictionary['private_operator_nh'] += 1
                    if not competitor[0]['invest'] == '-':
                        market_study_dictionary['invest_costs_private'].append(float(competitor[0]['invest']))
                        market_study_dictionary['invest_costs_private_home'] = float(competitor[0]['invest'])
                elif competitor[0]['type'] == 'kommunal':
                    market_study_dictionary['public_operator_nh'] += 1
                    if not competitor[0]['invest'] == '-':
                        market_study_dictionary['invest_costs_public'].append(float(competitor[0]['invest']))
                        market_study_dictionary['invest_costs_public_home'] = float(competitor[0]['invest'])
                elif competitor[0]['type'] == 'gemeinnützig':
                    market_study_dictionary['non_profit_operator_nh'] += 1
                    if not competitor[0]['invest'] == '-':
                        market_study_dictionary['invest_costs_non_profit'].append(float(competitor[0]['invest']))
                        market_study_dictionary['invest_costs_non_profit_home'] = float(competitor[0]['invest'])
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
                    market_study_dictionary['list_beds'].append(beds)
                if not single_rooms == '-':
                    total_single_rooms += single_rooms
                if not double_rooms == '-':
                    total_double_rooms += double_rooms
                if not rooms == '-':
                    total_rooms += rooms
                if not single_room_quote == '-':
                    list_single_room_quota.append(single_room_quote)
                if not competitor[0]['occupancy'] == '-' and not competitor[0]['occupancy'] == 'N.A.' and competitor[0]['occupancy'] is not None:
                    list_occupancy_rate.append(competitor[0]['occupancy'])
                if not competitor[0]['invest'] == '-' and not competitor[0]['invest'] == 'N.A.' and competitor[0]['invest'] is not None:
                    list_invest_cost.append(float(competitor[0]['invest']))
                    market_study_dictionary['home_invest'] = float(competitor[0]['invest'])
                if not competitor[0]['mdk_note'] == '-' and not competitor[0]['mdk_note'] == 'N.A.' and competitor[0]['mdk_note'] is not None:
                    list_mdk_grade.append(mdk_grade_letters.index(competitor[0]['mdk_note']) + 1)
                if not competitor[0]['baujahr'] == '-' and not competitor[0]['baujahr'] == 'N.A.' and competitor[0]['baujahr'] is not None:
                    market_study_dictionary['list_years_of_construction_nh'].append(int(competitor[0]['baujahr']))
                if not competitor[0]['invest'] == '-' and not competitor[0]['invest'] == 'N.A.' and not competitor[0][
                                                                                                            'baujahr'] == '-' and not \
                competitor[0]['baujahr'] == 'N.A.' and competitor[0]['baujahr'] is not None and competitor[0]['invest'] is not None:
                    market_study_dictionary['invest_plot_data'].append(
                        ['home', competitor[0]['invest'], competitor[0]['baujahr'], '⌂'])

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
                    'txt': '-' if competitor[0]['mdk_note'] == 'N.A.' else '-' if competitor[0]['mdk_note'] is None else
                    competitor[0]['mdk_note'],
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
                    'color': [0, 176, 240] if competitor[0]['web'] is not None and "keine " not in competitor[0][
                        'web'] else [0, 0, 0],
                    'font': 'segoeui',
                    'size': 8,
                    'x': 17,
                    'y': current_page_height,
                    'w': 50,
                    'h': 6,
                    'txt': competitor[0]['raw_name'] if len(
                        competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
                    'align': 'left',
                    'link': competitor[0]['web'] if competitor[0]['web'] is not None and "keine " not in competitor[0][
                        'web'] else ""
                }
                current_competitor_page['cell'][f'competitor_{table_position}_operator'] = {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 8,
                    'x': 17,
                    'y': current_page_height + 4,
                    'w': 50,
                    'h': 6,
                    'txt': competitor[0]['raw_betreiber'] if len(
                        competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
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
                        market_study_dictionary['complied_regulations'] += 1
                    else:
                        market_study_dictionary['uncomplied_regulations'] += 1
                if competitor[0]['type'] == 'privat':
                    market_study_dictionary['private_operator_nh'] += 1
                    if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-':
                        market_study_dictionary['invest_costs_private'].append(float(competitor[0]['invest']))
                elif competitor[0]['type'] == 'kommunal':
                    market_study_dictionary['public_operator_nh'] += 1
                    if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-':
                        market_study_dictionary['invest_costs_public'].append(float(competitor[0]['invest']))
                elif competitor[0]['type'] == 'gemeinnützig':
                    market_study_dictionary['non_profit_operator_nh'] += 1
                    if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-':
                        market_study_dictionary['invest_costs_non_profit'].append(float(competitor[0]['invest']))
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
                    market_study_dictionary['list_beds'].append(beds)
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
                    market_study_dictionary['list_years_of_construction_nh'].append(int(competitor[0]['baujahr']))
                if competitor[0]['invest'] is not None and not competitor[0]['invest'] == '-' and competitor[0][
                    'baujahr'] is not None and not competitor[0]['baujahr'] == '-':
                    market_study_dictionary['invest_plot_data'].append(["private" if competitor[0][
                                                                                     'type'] == "privat" else "non-profit" if
                    competitor[0]['type'] == "gemeinnützig" else "public", competitor[0]['invest'],
                                                                    competitor[0]['baujahr'], prev_competitor_index])

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
                    'txt': '{:,}%'.format(round(competitor[0]['occupancy'] * 100, 1)) if not competitor[0][
                                                                                                 'occupancy'] == '-' else
                    competitor[0]['occupancy'],
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
                    'txt': '-' if competitor[0]['mdk_note'] == 'N.A.' else '-' if competitor[0]['mdk_note'] is None else
                    competitor[0]['mdk_note'],
                    'align': 'center',
                }

            current_page_height += 12

            if index == len(market_study_dictionary['data_comp_analysis_nh']['data']) - 1:
                median_dictionary = anvil.server.call(
                    "get_multiple_median",
                    {
                        'single_room_quota': list_single_room_quota,
                        'occupancy_rate': list_occupancy_rate,
                        'invest_cost': list_invest_cost,
                        'mdk_grade': list_mdk_grade
                    }
                )
                # Hier geht`s weiter
                if len(list_single_room_quota) > 0:
                    total_single_room_quota = median_dictionary['single_room_quota']
                if len(list_occupancy_rate) > 0:
                    total_occupancy_rate = median_dictionary['occupancy_rate']
                if len(list_invest_cost) > 0:
                    market_study_dictionary['minimum_invest_cost'] = min(list_invest_cost)
                    market_study_dictionary['maximum_invest_cost'] = max(list_invest_cost)
                    market_study_dictionary['total_invest_cost'] = median_dictionary['invest_cost']
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
                    'txt': 'x̃ {:,}'.format(round(market_study_dictionary['total_invest_cost'], 2)),
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

                market_study_dictionary['competitor_pages'][f'competitor_analysis_{market_study_dictionary["page"]}'] = current_competitor_page
                market_study_dictionary['page'] += 1
                market_study_dictionary['current_competitor_analysis_page'] += 1

        return market_study_dictionary


def generate_assisted_living_pages(version, market_study_dictionary):
    with anvil.server.no_loading_indicator:
        home_counter = 0
        prev_competitor_distance = 0
        prev_competitor_index = 0
        market_study_dictionary['list_years_of_construction_al'] = []
        market_study_dictionary['non_profit_operator_al'] = 0
        market_study_dictionary['public_operator_al'] = 0
        market_study_dictionary['private_operator_al'] = 0

        for index, competitor in enumerate(market_study_dictionary['data_comp_analysis_al']['data']):
            if index % 9 == 0:
                if index > 0:
                    market_study_dictionary['competitor_pages'][f'competitor_analysis_{market_study_dictionary["page"]}'] = current_competitor_page
                    market_study_dictionary['page'] += 1
                    market_study_dictionary['current_competitor_analysis_page'] += 1
                current_competitor_page = copy.deepcopy(Assisted_Living_Competitor_Skeleton.assisted_living_competitor_skeleton_en if version == "english" else Assisted_Living_Competitor_Skeleton.assisted_living_competitor_skeleton_de)
                current_competitor_page['page_number'] = market_study_dictionary['current_competitor_analysis_page']
                current_competitor_page['text']['heading_city']['txt'] = market_study_dictionary['city']
                current_competitor_page['image']['location_map']['path'] = f"tmp/map_image_{market_study_dictionary['unique_code']}.png"
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
                    'txt': competitor[0]['raw_name'] if len(
                        competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
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
                    'txt': competitor[0]['raw_betreiber'] if len(
                        competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
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
                    'txt': competitor[0]['year_of_construction'] if competitor[0][
                                                                        'year_of_construction'] is not None else '-',
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
                    'txt': '{:,}'.format(int(competitor[0]['number_apts'])) if competitor[0][
                                                                                       'number_apts'] is not None else '-',
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

                if competitor[0]['year_of_construction'] is not None:
                    market_study_dictionary['list_years_of_construction_al'].append(int(competitor[0]['year_of_construction']))
                if competitor[0]['type'] == 'gemeinnützig':
                    market_study_dictionary['non_profit_operator_al'] += 1
                elif competitor[0]['type'] == 'kommunal':
                    market_study_dictionary['public_operator_al'] += 1
                elif competitor[0]['type'] == 'privat':
                    market_study_dictionary['private_operator_al'] += 1
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
                    'color': [0, 176, 240] if competitor[0]['web'] is not None and "keine " not in competitor[0][
                        'web'] else [0, 0, 0],
                    'font': 'segoeui',
                    'size': 8,
                    'x': 17,
                    'y': current_page_height,
                    'w': 50,
                    'h': 6,
                    'txt': competitor[0]['raw_name'] if len(
                        competitor[0]['raw_name']) <= 30 else f"{competitor[0]['raw_name'][:30]}...",
                    'align': 'left',
                    'link': competitor[0]['web'] if competitor[0]['web'] is not None and "keine " not in competitor[0][
                        'web'] else ""
                }
                current_competitor_page['cell'][f'competitor_{table_position}_operator'] = {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 8,
                    'x': 17,
                    'y': current_page_height + 4,
                    'w': 50,
                    'h': 6,
                    'txt': competitor[0]['raw_betreiber'] if len(
                        competitor[0]['raw_betreiber']) <= 30 else f"{competitor[0]['raw_betreiber'][:30]}...",
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
                    'txt': competitor[0]['year_of_construction'] if competitor[0][
                                                                        'year_of_construction'] is not None else '-',
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
                    'txt': '{:,}'.format(int(competitor[0]['number_apts'])) if competitor[0][
                                                                                   'number_apts'] is not None else '-',
                    'align': 'center',
                }

                if competitor[0]['year_of_construction'] is not None:
                    market_study_dictionary['list_years_of_construction_al'].append(int(competitor[0]['year_of_construction']))
                if competitor[0]['type'] == 'gemeinnützig':
                    market_study_dictionary['non_profit_operator_al'] += 1
                elif competitor[0]['type'] == 'kommunal':
                    market_study_dictionary['public_operator_al'] += 1
                elif competitor[0]['type'] == 'privat':
                    market_study_dictionary['private_operator_al'] += 1
            
            current_page_height += 12

            if index == len(market_study_dictionary['data_comp_analysis_al']['data']) - 1:
                market_study_dictionary['competitor_pages'][f'competitor_analysis_{market_study_dictionary["page"]}'] = current_competitor_page
                market_study_dictionary['page'] += 1
                market_study_dictionary['current_competitor_analysis_page'] += 1
                pass

        return market_study_dictionary


def create_market_study(application, version, version_index, market_study_dictionary):
    market_study_dictionary['analysis_text_response'] = anvil.server.call('openai_test', market_study_dictionary['city'], version)
    Functions.manipulate_loading_overlay(False)
    market_study_dictionary['final_analysis_text'] = alert(ChatGPT(generated_text=market_study_dictionary['analysis_text_response']), buttons=[], dismissible=False, large=True, role='custom_alert')
    Functions.manipulate_loading_overlay(True)

    market_study_dictionary['market_study_pages'] = ['cover', 'summary', 'location_analysis']

    if version == "german":
        if market_study_dictionary['iso_movement'] == "walking":
            market_study_dictionary['iso_string'] = f"{market_study_dictionary['iso_time']} Minuten zu Fuß"
        elif market_study_dictionary['iso_movement'] == "cycling":
            market_study_dictionary['iso_string'] = f"{market_study_dictionary['iso_time']} Minuten fahren - Fahrrad"
        elif market_study_dictionary['iso_movement'] == "driving":
            market_study_dictionary['iso_string'] = f"{market_study_dictionary['iso_time']} Minuten fahren - Auto"
        market_study_data = Market_Study_Skeleton.market_study_skeleton_de({
            'street': market_study_dictionary['street'],
            'zipcode': market_study_dictionary['zipcode'],
            'city': market_study_dictionary['city'],
            'district': market_study_dictionary['district'],
            'federal_state': market_study_dictionary['federal_state'],
            'iso_string': market_study_dictionary['iso_string'],
            'created_date': market_study_dictionary['created_date'],
            'purchase_power': market_study_dictionary['purchase_power'],
            'population_trend': market_study_dictionary['population_trend'],
            'beds_surplus_35_v2': market_study_dictionary['beds_surplus_35_v2'],
            'countie': market_study_dictionary['countie'],
            'population_city_2020': market_study_dictionary['countie_data']['dem_city']['bevoelkerung_ges'],
            'population_county_2020': market_study_dictionary['countie_data']['ex_dem_lk']['all_compl'],
            'people_u80': market_study_dictionary['people_u80'],
            'people_o80': market_study_dictionary['people_o80'],
            'new_care_rate_raw': market_study_dictionary['new_care_rate_raw'],
            'nursing_home_rate': market_study_dictionary['nursing_home_rate'],
            'inpatients_lk': market_study_dictionary['inpatients_lk'],
            'occupancy_lk': market_study_dictionary['occupancy_lk'],
            'beds_lk': market_study_dictionary['beds_lk'],
            'free_beds_lk': market_study_dictionary['free_beds_lk'],
            'nursing_homes_active': market_study_dictionary['nursing_homes_active'],
            'beds_active': market_study_dictionary['beds_active'],
            'nursing_homes_planned': market_study_dictionary['nursing_homes_planned'],
            'nursing_homes_construct': market_study_dictionary['nursing_homes_construct'],
            'beds_planned': market_study_dictionary['beds_planned'],
            'beds_construct': market_study_dictionary['beds_construct'],
            'inpatients': market_study_dictionary['inpatients'],
            'population_fc_30': market_study_dictionary['population_fc_30'],
            'people_u80_fc': market_study_dictionary['people_u80_fc'],
            'people_o80_fc': market_study_dictionary['people_o80_fc'],
            'care_rate_30_v1_raw': market_study_dictionary['care_rate_30_v1_raw'],
            'pat_rec_full_care_fc_30_v1': market_study_dictionary['pat_rec_full_care_fc_30_v1'],
            'occupancy_lk_30_v1': market_study_dictionary['occupancy_lk_30_v1'],
            'beds_30_v1': market_study_dictionary['beds_30_v1'],
            'free_beds_30_v1': market_study_dictionary['free_beds_30_v1'],
            'loss_of_beds': market_study_dictionary['loss_of_beds'],
            'beds_adjusted_30_v1': market_study_dictionary['beds_adjusted_30_v1'],
            'inpatients_fc': market_study_dictionary['inpatients_fc'],
            'beds_surplus': market_study_dictionary['beds_surplus'],
            'care_rate_30_v2_raw': market_study_dictionary['care_rate_30_v2_raw'],
            'pat_rec_full_care_fc_30_v2': market_study_dictionary['pat_rec_full_care_fc_30_v2'],
            'occupancy_lk_30_v2': market_study_dictionary['occupancy_lk_30_v2'],
            'beds_30_v2': market_study_dictionary['beds_30_v2'],
            'free_beds_30_v2': market_study_dictionary['free_beds_30_v2'],
            'beds_adjusted_30_v2': market_study_dictionary['beds_adjusted_30_v2'],
            'inpatients_fc_v2': market_study_dictionary['inpatients_fc_v2'],
            'beds_surplus_v2': market_study_dictionary['beds_surplus_v2'],
            'population_fc_35': market_study_dictionary['population_fc_35'],
            'people_u80_fc_35': market_study_dictionary['people_u80_fc_35'],
            'people_o80_fc_35': market_study_dictionary['people_o80_fc_35'],
            'care_rate_35_v1_raw': market_study_dictionary['care_rate_35_v1_raw'],
            'pat_rec_full_care_fc_35_v1': market_study_dictionary['pat_rec_full_care_fc_35_v1'],
            'occupancy_lk_35_v1': market_study_dictionary['occupancy_lk_35_v1'],
            'beds_35_v1': market_study_dictionary['beds_35_v1'],
            'free_beds_35_v1': market_study_dictionary['free_beds_35_v1'],
            'beds_adjusted_35_v1': market_study_dictionary['beds_adjusted_35_v1'],
            'inpatients_fc_35': market_study_dictionary['inpatients_fc_35'],
            'beds_surplus_35': market_study_dictionary['beds_surplus_35'],
            'care_rate_35_v2_raw': market_study_dictionary['care_rate_35_v2_raw'],
            'pat_rec_full_care_fc_35_v2': market_study_dictionary['pat_rec_full_care_fc_35_v2'],
            'occupancy_lk_35_v2': market_study_dictionary['occupancy_lk_35_v2'],
            'beds_35_v2': market_study_dictionary['beds_35_v2'],
            'free_beds_35_v2': market_study_dictionary['free_beds_35_v2'],
            'beds_adjusted_35_v2': market_study_dictionary['beds_adjusted_35_v2'],
            'inpatients_fc_35_v2': market_study_dictionary['inpatients_fc_35_v2'],
            'analysis_text': market_study_dictionary['final_analysis_text'],
            'number_facilities_nh_value': len(market_study_dictionary['data_comp_analysis_nh']['data']),
            'number_facilities_al_value': len(market_study_dictionary['data_comp_analysis_al']['data']),
            'minimum_invest_cost': market_study_dictionary['minimum_invest_cost'],
            'maximum_invest_cost': market_study_dictionary['maximum_invest_cost'],
            'total_invest_cost': market_study_dictionary['total_invest_cost'],
            'home_invest': market_study_dictionary['home_invest'],
            'regulations': market_study_dictionary['regulations'],
            'complied_regulations': market_study_dictionary['complied_regulations'],
            'uncomplied_regulations': market_study_dictionary['uncomplied_regulations'],
            'share_url': market_study_dictionary['share_url'],
            'unique_code': market_study_dictionary['unique_code']
        })
    elif version == "english":
        market_study_dictionary['iso_string'] = f"{market_study_dictionary['iso_time']} minutes {market_study_dictionary['iso_movement']}"
        market_study_data = Market_Study_Skeleton.market_study_skeleton_en({
            'street': market_study_dictionary['street'],
            'zipcode': market_study_dictionary['zipcode'],
            'city': market_study_dictionary['city'],
            'district': market_study_dictionary['district'],
            'federal_state': market_study_dictionary['federal_state'],
            'iso_string': market_study_dictionary['iso_string'],
            'created_date': market_study_dictionary['created_date'],
            'purchase_power': market_study_dictionary['purchase_power'],
            'population_trend': market_study_dictionary['population_trend'],
            'beds_surplus_35_v2': market_study_dictionary['beds_surplus_35_v2'],
            'countie': market_study_dictionary['countie'],
            'population_city_2020': market_study_dictionary['countie_data']['dem_city']['bevoelkerung_ges'],
            'population_county_2020': market_study_dictionary['countie_data']['ex_dem_lk']['all_compl'],
            'people_u80': market_study_dictionary['people_u80'],
            'people_o80': market_study_dictionary['people_o80'],
            'new_care_rate_raw': market_study_dictionary['new_care_rate_raw'],
            'nursing_home_rate': market_study_dictionary['nursing_home_rate'],
            'inpatients_lk': market_study_dictionary['inpatients_lk'],
            'occupancy_lk': market_study_dictionary['occupancy_lk'],
            'beds_lk': market_study_dictionary['beds_lk'],
            'free_beds_lk': market_study_dictionary['free_beds_lk'],
            'nursing_homes_active': market_study_dictionary['nursing_homes_active'],
            'beds_active': market_study_dictionary['beds_active'],
            'nursing_homes_planned': market_study_dictionary['nursing_homes_planned'],
            'nursing_homes_construct': market_study_dictionary['nursing_homes_construct'],
            'beds_planned': market_study_dictionary['beds_planned'],
            'beds_construct': market_study_dictionary['beds_construct'],
            'inpatients': market_study_dictionary['inpatients'],
            'population_fc_30': market_study_dictionary['population_fc_30'],
            'people_u80_fc': market_study_dictionary['people_u80_fc'],
            'people_o80_fc': market_study_dictionary['people_o80_fc'],
            'care_rate_30_v1_raw': market_study_dictionary['care_rate_30_v1_raw'],
            'pat_rec_full_care_fc_30_v1': market_study_dictionary['pat_rec_full_care_fc_30_v1'],
            'occupancy_lk_30_v1': market_study_dictionary['occupancy_lk_30_v1'],
            'beds_30_v1': market_study_dictionary['beds_30_v1'],
            'free_beds_30_v1': market_study_dictionary['free_beds_30_v1'],
            'loss_of_beds': market_study_dictionary['loss_of_beds'],
            'beds_adjusted_30_v1': market_study_dictionary['beds_adjusted_30_v1'],
            'inpatients_fc': market_study_dictionary['inpatients_fc'],
            'beds_surplus': market_study_dictionary['beds_surplus'],
            'care_rate_30_v2_raw': market_study_dictionary['care_rate_30_v2_raw'],
            'pat_rec_full_care_fc_30_v2': market_study_dictionary['pat_rec_full_care_fc_30_v2'],
            'occupancy_lk_30_v2': market_study_dictionary['occupancy_lk_30_v2'],
            'beds_30_v2': market_study_dictionary['beds_30_v2'],
            'free_beds_30_v2': market_study_dictionary['free_beds_30_v2'],
            'beds_adjusted_30_v2': market_study_dictionary['beds_adjusted_30_v2'],
            'inpatients_fc_v2': market_study_dictionary['inpatients_fc_v2'],
            'beds_surplus_v2': market_study_dictionary['beds_surplus_v2'],
            'population_fc_35': market_study_dictionary['population_fc_35'],
            'people_u80_fc_35': market_study_dictionary['people_u80_fc_35'],
            'people_o80_fc_35': market_study_dictionary['people_o80_fc_35'],
            'care_rate_35_v1_raw': market_study_dictionary['care_rate_35_v1_raw'],
            'pat_rec_full_care_fc_35_v1': market_study_dictionary['pat_rec_full_care_fc_35_v1'],
            'occupancy_lk_35_v1': market_study_dictionary['occupancy_lk_35_v1'],
            'beds_35_v1': market_study_dictionary['beds_35_v1'],
            'free_beds_35_v1': market_study_dictionary['free_beds_35_v1'],
            'beds_adjusted_35_v1': market_study_dictionary['beds_adjusted_35_v1'],
            'inpatients_fc_35': market_study_dictionary['inpatients_fc_35'],
            'beds_surplus_35': market_study_dictionary['beds_surplus_35'],
            'care_rate_35_v2_raw': market_study_dictionary['care_rate_35_v2_raw'],
            'pat_rec_full_care_fc_35_v2': market_study_dictionary['pat_rec_full_care_fc_35_v2'],
            'occupancy_lk_35_v2': market_study_dictionary['occupancy_lk_35_v2'],
            'beds_35_v2': market_study_dictionary['beds_35_v2'],
            'free_beds_35_v2': market_study_dictionary['free_beds_35_v2'],
            'beds_adjusted_35_v2': market_study_dictionary['beds_adjusted_35_v2'],
            'inpatients_fc_35_v2': market_study_dictionary['inpatients_fc_35_v2'],
            'analysis_text': market_study_dictionary['final_analysis_text'],
            'number_facilities_nh_value': len(market_study_dictionary['data_comp_analysis_nh']['data']),
            'number_facilities_al_value': len(market_study_dictionary['data_comp_analysis_al']['data']),
            'minimum_invest_cost': market_study_dictionary['minimum_invest_cost'],
            'maximum_invest_cost': market_study_dictionary['maximum_invest_cost'],
            'total_invest_cost': market_study_dictionary['total_invest_cost'],
            'home_invest': market_study_dictionary['home_invest'],
            'regulations': market_study_dictionary['regulations'],
            'complied_regulations': market_study_dictionary['complied_regulations'],
            'uncomplied_regulations': market_study_dictionary['uncomplied_regulations'],
            'share_url': market_study_dictionary['share_url'],
            'unique_code': market_study_dictionary['unique_code']
        })
    
    max_pages = 3
    for page in market_study_dictionary['competitor_pages']:
        market_study_data['pages'][page] = market_study_dictionary['competitor_pages'][page]
        market_study_dictionary['market_study_pages'].append(page)
        max_pages += 1

    max_pages += 4
    market_study_dictionary['market_study_pages'].append('good_to_know')
    market_study_dictionary['market_study_pages'].append('regulations')
    market_study_dictionary['market_study_pages'].append('methodic')
    market_study_dictionary['market_study_pages'].append('contact')
    market_study_data['number_of_pages'] = max_pages
    market_study_data['pages']['good_to_know']['page_number'] = max_pages - 3
    market_study_data['pages']['regulations']['page_number'] = max_pages - 2
    market_study_data['pages']['methodic']['page_number'] = max_pages - 1
    market_study_data['pages']['contact']['page_number'] = max_pages

    good_to_know_median = anvil.server.call(
        'get_multiple_median',
        {
            'beds': market_study_dictionary['list_beds'],
            'years_of_construction_nh': market_study_dictionary['list_years_of_construction_nh'],
            'years_of_construction_al': market_study_dictionary['list_years_of_construction_al']
        }
    )

    market_study_data['pages']['good_to_know']['cell']['median_beds_value']['txt'] = str(good_to_know_median['beds'])
    market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_value']['txt'] = str(
        int(good_to_know_median['years_of_construction_nh'])) if not good_to_know_median[
                                                                         'years_of_construction_nh'] == '-' else \
    good_to_know_median['years_of_construction_nh']
    market_study_data['pages']['good_to_know']['cell']['median_year_of_construct_al_value']['txt'] = str(
        int(good_to_know_median['years_of_construction_al'])) if not good_to_know_median[
                                                                         'years_of_construction_al'] == '-' else \
    good_to_know_median['years_of_construction_al']

    competitor_map_request_data = application.build_competitor_map_request(
        market_study_dictionary['coords_nh'],
        Variables.home_address_nh,
        market_study_dictionary['coords_al'],
        [],
        'nursing_home'
    )
    competitor_map_request_data = application.build_competitor_map_request(
        competitor_map_request_data['controlling_marker'],
        Variables.home_address_al,
        competitor_map_request_data['working_marker'],
        competitor_map_request_data['request'],
        'assisted_living'
    )
    
    competitor_map_request = application.build_home_marker_map_request(
        competitor_map_request_data['controlling_marker']['marker_coords']['lng'],
        competitor_map_request_data['controlling_marker']['marker_coords']['lat'],
        competitor_map_request_data['request']
    )

    chart_data = {
        'operator': {
            'nursing_home_data': [market_study_dictionary['non_profit_operator_nh'],
                                  market_study_dictionary['public_operator_nh'],
                                  market_study_dictionary['private_operator_nh']],
            'assisted_living_data': [market_study_dictionary['non_profit_operator_al'],
                                     market_study_dictionary['public_operator_al'],
                                     market_study_dictionary['private_operator_al']]
        },
        'invest_cost_overall': market_study_dictionary['invest_plot_data'],
        'purchasing_power': market_study_dictionary['purchase_power'],
        'invest_cost_public': {
            'data': market_study_dictionary['invest_costs_public'],
            'home': market_study_dictionary['invest_costs_public_home']
        },
        'invest_cost_non_profit': {
            'data': market_study_dictionary['invest_costs_non_profit'],
            'home': market_study_dictionary['invest_costs_non_profit_home']
        },
        'invest_cost_private': {
            'data': market_study_dictionary['invest_costs_private'],
            'home': market_study_dictionary['invest_costs_private_home']
        },
    }

    anvil.server.call(
        'generate_market_study_pdf',
        market_study_data,  # Dictionary of Data to fill Market Study PDF
        market_study_dictionary['bounding_box'],  # Bounding Box of the Map
        market_study_dictionary['unique_code'],  # Unique creation Code for current Market Study
        market_study_dictionary['market_study_pages'],  # Ordered List of Pages inside Market Study
        competitor_map_request,  # Request Data for Competitor Map
        Variables.activeIso,  # Data of current Iso Layer
        market_study_dictionary['marker_coords'],  # Coordinates of Map Marker
        chart_data,  # Data to create all needed charts
        version  # Language Version of Market Study
    )

    anvil.js.call('update_loading_bar', 80 + 10 * version_index, 'Download Market Study')
    market_study = app_tables.pictures.search()[0]
    anvil.media.download(market_study['pic'])
