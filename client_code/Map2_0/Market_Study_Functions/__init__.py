import anvil.server
from .. import Variables
from anvil import alert

''' Organize Data for Compettior Analysis '''
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
        Functions.manipulate_loading_overlay(self, False)
        res = alert(content=Market_Study_Existing_Home(entry=entry, topic=topic), dismissible=False, large=True, buttons=[], role='custom_alert')
        Functions.manipulate_loading_overlay(self, True)
        if res == 'Yes':
          if topic == 'nursing_homes':
            Variables.home_address_nh.append(entry)
          else:
            Variables.home_address_al.append(entry)
      
    if topic == 'nursing_homes':
      if len(Variables.home_address_nh) == 0:
        from .Market_Study_NH_Home import Market_Study_NH_Home
        from .Market_Study_NH_Home_Mobile import Market_Study_NH_Home_Mobile
        Functions.manipulate_loading_overlay(self, False)
        if self.mobile:
          Variables.home_address_nh = alert(content=Market_Study_NH_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        else:
          Variables.home_address_nh = alert(content=Market_Study_NH_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        Functions.manipulate_loading_overlay(self, True)
        if not Variables.home_address_nh == []:
          sorted_coords.insert(0, Variables.home_address_nh)
    else:
      if Variables.home_address_al == []:
        from .Market_Study_AL_Home import Market_Study_AL_Home
        from .Market_Study_AL_Home_Mobile import Market_Study_AL_Home_Mobile
        Functions.manipulate_loading_overlay(self, False)
        if self.mobile:
          Variables.home_address_al = alert(content=Market_Study_AL_Home_Mobile(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        else:
          Variables.home_address_al = alert(content=Market_Study_AL_Home(marker_coords=marker_coords), dismissible=False, large=True, buttons=[], role='custom_alert')
        Functions.manipulate_loading_overlay(self, True)
        if not Variables.home_address_al == []:
          sorted_coords.insert(0, Variables.home_address_al)

    res_data = {'sorted_coords': sorted_coords[:30], 'marker_coords': marker_coords}
    
    return res_data

''' Build Request String for Competitor Map '''
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