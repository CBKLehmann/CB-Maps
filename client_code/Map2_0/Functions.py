import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from .. import Variables, Layer, Images
from anvil.js.window import document
import datetime

global Variables, Layer, Images

def show_hide_marker(self, check_box, marker_id):
  #Show or Hide markers from given Excel Table
  
  for el in Variables.marker[marker_id]['marker']:
    if marker_id in Variables.marker.keys():
      if check_box:
        el.addTo(self.mapbox)
      else:
        el.remove()

def change_active_Layer(self, layer, inactive_layer, visibility, other_checkbox):
  #This method is called when the active Layer is changed

  for layer_entry in layer:
    self.mapbox.setLayoutProperty(layer_entry, 'visibility', visibility)
    for inactive_layer_entries in inactive_layer:
      for inactive_layer_entry in inactive_layer_entries:
        self.mapbox.setLayoutProperty(inactive_layer_entry, 'visibility', 'none')

  for checkbox in other_checkbox:
    checkbox.checked = False

  if visibility == 'visible':
    Variables.activeLayer = layer[0]
  else:
    Variables.activeLayer = None
  
def refresh_icons(self):
    
  checkbox =  self.poi_category.get_components()
  for panel in checkbox:
    if isinstance(panel, anvil.GridPanel):
      for component in panel.get_components():
        if not component.text == 'Select All':
          self.change_icons(component.text)

def create_bounding_box(self):
  
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
      
  return bbox

def manipulate_loading_overlay(self, state):
    html = document.getElementsByClassName('anvil-root-container')[0]
    if state:
      if not Variables.loading:
        self.loading = document.createElement('div')
        self.loading.style.width = '100vw'
        self.loading.style.height = '100vh'
        self.loading.style.backgroundColor = 'rgba(62, 62, 62, .3)'
        self.loading.style.zIndex = '10000'
        self.loading.style.cursor = 'wait'
        self.loading.style.position = 'fixed'
        self.loading.style.top = '0'
        self.loading.style.left = '0'
        html.appendChild(self.loading)
        Variables.loading = True
    else:
      html.removeChild(self.loading)
      Variables.loading = False

def create_marker(self, check_box, last_bbox, category, picture, bbox, marker_coords, mapboxgl):

  # Check if Category is PflegeDB
  if category == 'nursing_homes':
    geojson = anvil.server.call('get_care_db_data', bbox, 'Pflegeheime')
    Variables.nursing_homes_entries = geojson

  elif category == 'assisted_living':

    geojson = anvil.server.call('get_care_db_data', bbox, 'BetreutesWohnen')
    Variables.assisted_living_entries = geojson

  elif category == 'nursing-schools':

    geojson = anvil.server.call('get_einrichtungen', bbox)

  elif category in Variables.micro_living_categories:
    if category == 'business_living':
      geojson = anvil.server.call('get_micro_living_facilities', 'Business living', marker_coords)
    elif category == 'co_living':
      geojson = anvil.server.call('get_micro_living_facilities', 'Co-living', marker_coords)
    elif category == 'service_living':
      geojson = anvil.server.call('get_micro_living_facilities', 'Serviced living', marker_coords)
    elif category == 'student_living':
      geojson = anvil.server.call('get_micro_living_facilities', 'Student living', marker_coords)
  
  else:

    # Get geojson of POIs inside Bounding Box
    geojson = anvil.server.call('poi_data', category, bbox, marker_coords, int(self.max_marker.text))

  # Check if Elements are over 3000 for performance Reasons
  if len(geojson) > 3000:

    # Tell the User about to many Elements
    alert('Zu große Ergebnismenge ! Näher ranzoomen !')

  # Do if Elements are under 3000
  else:

    if category == 'subway':

      self.opnv_layer = []

      #Create empty Icons Array to save Elements
      icons = []
      id_counter = 0
      
      for route in geojson:
        coordinates = []
        if 'colour' in route['tags']:
          colour = route['tags']['colour']
        else:
          colour = '#000000'
        for point in route['members']:
          if point['role'] == 'stop':

            # Create HTML Element for Icon
            el = document.createElement('div')
            el.className = 'marker'
            el.id = f'{category}_{id_counter}'
            el.style.width = '15px'
            el.style.height = '15px'
            el.style.backgroundSize = '100%'
            el.style.backgroundrepeat = 'no-repeat'
            el.style.zIndex = '220'
            el.style.cursor = 'pointer'
            el.style.backgroundColor = colour
            el.style.borderRadius = '50%'

            # Add Icon to the Map
            newicon = mapboxgl.Marker(el, {'anchor': 'center'}).setLngLat([point['lon'], point['lat']]).setOffset([0, 0]).addTo(self.mapbox)

            id_counter += 1
            
            coordinates.append([point['lon'], point['lat']])
            # Add current Element-Icon to Icon-Array
            icons.append(newicon)
            
        geometry = {
          'type': 'LineString',
          'coordinates': coordinates
        }
        if 'name' in route['tags']:
          id = route['tags']['name']
        else:
          id = route['tags']['ref']
        self.mapbox.addLayer({
          'id': id,
          'type': 'line',
          'source': {
            'type': 'geojson',
            'data': {
              'type': 'Feature',
              'properties': {},
              'geometry': geometry
            }
          },
          'layout': {'line-cap': 'round'},
          'paint': {
            'line-color': colour,
            'line-width': 4
          }
        })

        self.opnv_layer.append(id)
      
    else:

      #Create empty Icons Array to save Elements
      icons = []
      id_counter = 0

      # Loop through every Element in geojson
      for ele in geojson:

        deleted = False

        # Create HTML Element for Icon
        el = document.createElement('div')
        el.className = 'marker'
        el.id = f'{category}_{id_counter}'
        el.style.width = '40px'
        el.style.height = '40px'
        el.style.backgroundSize = '100%'
        el.style.backgroundrepeat = 'no-repeat'
        el.style.zIndex = '220'
        el.style.cursor = 'pointer'

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

          if category in Variables.removed_markers.keys():
            for marker in Variables.removed_markers[category]:
              if marker['lng'] == el_coords[0] and marker['lat'] == el_coords[1]:
                deleted = True

          if not deleted:
            distance = anvil.server.call('get_point_distance', marker_coords, el_coords)
  
            marker_details = f"<div class='objectName'>{name}</div>"
            if not self.role == 'guest':
              marker_details += "<div class='rmv_container'><button id='remove' class='btn btn-default'>Remove Marker</button></div>"
            
            # Create Popup for Element
            popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
              f"<p class='popup_name'><b>{name}</b></p>"
              f"<p class='popup_distance'>{distance} km  to the location</p>"
            )
          
        # Check if Category is PflegeDB
        elif category == 'nursing_homes':

          el_coords = [ele['coord_lon'], ele['coord_lat']]

          if category in Variables.removed_markers.keys():
            for marker in Variables.removed_markers[category]:
              if str(marker['lng']) == el_coords[0] and str(marker['lat']) == el_coords[1]:
                deleted = True

          if not deleted:
            distance = anvil.server.call('get_point_distance', marker_coords, el_coords)
            
            # Create Popup for Element
            popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
              f"<p class='popup_name'><b>{ele['name']}</b></p>"
              f"<p class='popup_type'>{ele['sektor']}</p>"
              f"<p class='popup_distance'>{distance} km  to the location</p>"
              "<p class='popup_betreiber_label'><b>Operator:</b></p>"
              f"<p class='popup_betreiber'>{ele['betreiber']}</p>"
              f"<p class='popup_status'><b>Status:</b> {ele['status']}</p>"
            )
            # popup_element = popup.getElement()
            # print(popup_element)
            # popup.getElement().addEventListener('mouseenter', print('Hello'))
            marker_details = f"<div class='x-btn-container'><button id='close' class='btn btn-default'>X</button></div>"
            # Name of Object
            marker_details += f"<div class='objectName'>{ele['name']}</div>"
            # Tags
            marker_details += "<div class='tagContainer'>"
            marker_details += f"<p class='tag'>{ele['sektor']}</p>"
            marker_details += f"<p class='tag'>{ele['art']}</p>"
            spez = ele['spezialisierung'].split('|')
            for entry in spez:
              marker_details += f"<p class='tag'>{entry}</p>"
            marker_details += f"<p class='tag'>{ele['status']}</p>"
            marker_details += "</div>"
            # Year of Construction/Modernisation
            marker_details += f"<p>Year of construction: {ele['baujahr']}</p>"
            marker_details += f"<p>Year od modernization: {ele['modernisierung']}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # Contact Details
            marker_details += f"<div class='containerAddress'><img src='{self.app_url}/_/theme/Pins/Address.png' class='iconAddress' /><p>{ele['strasse']}, {ele['plz']} {ele['ort']}"
            states = ['Berlin', 'Bremen', 'Hamburg']
            if not ele['bundesland'] in states:
              marker_details += f", {ele['bundesland']}</p></div>"
            else:
              marker_details += "</p></div>"
            marker_details += f"<div class='containerAddress'><img src='{self.app_url}/_/theme/Icons/telefon.png' class='iconAddress' /><p>{ele['telefon']}</p></div>"
            marker_details += f"<p>{ele['email']}</p>"
            marker_details += f"<p>{ele['webseite']}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # Operator
            marker_details += f"<p>Operator: {ele['betreiber']}</p>"
            marker_details += f"<p>Subsidiary 1: {ele['tochterfirma1']}</p>"
            marker_details += f"<p>Subsidiary 2: {ele['tochterfirma2']}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # MDK Grade
            if not ele['mdk_datum'] == "-":
              date = ele['mdk_datum'].split('-')
              marker_details += f"<p>MDK Evaluation from the {date[2]}.{date[1]}.{date[0]}</p>"
            else:
              marker_details += f"<p>MDK Evaluation from the {ele['mdk_datum']}</p>"
            marker_details += f"<p><b>Nursing and medical care: </b> {ele['pfl_u_med_vers']}</p>"
            marker_details += f"<p><b>Dealing with residents with dementia: </b> {ele['umg_mit_dem_bew']}</p>"
            marker_details += f"<p><b>Social care and daily routine: </b> {ele['soz_betrualltag']}</p>"
            marker_details += f"<p><b>Housing, food, housekeeping and hygiene: </b> {ele['wohn_verpfl_hausw_hyg']}</p>"
            marker_details += f"<p><b>Survey of residents: </b> {ele['befr_bew']}</p>"
            marker_details += f"<p><b>MDK Grade: </b> {ele['mdk_note']}</p>"
            marker_details += "<div class='partingLine'></div>"
            marker_details += f"<p><b>Number of patients treated: </b> {ele['anz_vers_pat']}</p>"
            
            marker_details += f"<p><b>Number of places full care: </b> {ele['platz_voll_pfl']}</p>"
            marker_details += f"<p><b>Number of places for short-term care: </b> {ele['platz_kurzpfl']}</p>"
            marker_details += f"<p><b>Number of places night care: </b> {ele['platz_nachtpfl']}</p>"
            
            marker_details += f"<p><b>Single rooms: </b> {ele['ez']}</p>"
            marker_details += f"<p><b>Double roooms: </b> {ele['dz']}</p>"
            marker_details += "<div class='line'></div>"
            marker_details += f"<p><b>Education fee: </b> {ele['ausbildungsumlage']}</p>"
            marker_details += f"<p><b>EEE: </b> {ele['eee']}</p>"
            marker_details += f"<p><b>UuV: </b> {ele['uuv']}</p>"
            marker_details += f"<p><b>Invest: </b> {ele['invest']}</p>"
            marker_details += f"<p><b>PG 1: </b> {ele['pg_1']}</p>"
            marker_details += f"<p><b>PG 2: </b> {ele['pg_2']}</p>"
            marker_details += f"<p><b>PG 3: </b> {ele['pg_3']}</p>"
            marker_details += f"<p><b>PG 4: </b> {ele['pg_4']}</p>"
            marker_details += f"<p><b>PG 5: </b> {ele['pg_5']}</p>"
            marker_details += "<div class='line'></div>"
            marker_details += f"<p><b>Holder ID: </b> {ele['traeger_id']}</p>"
            marker_details += f"<p><b>IK_Number: </b> {ele['ik_nummer']}</p>"
            if not self.role == 'guest':
              marker_details += f"<div class='rmv_container'><button id='remove' class='btn btn-default'><img src='{self.app_url}/_/theme/Icons/remove_marker.png' class='iconRemove' />Remove Marker</button></div>"

        elif category == 'assisted_living':

          el_coords = [ele['coord_lon'], ele['coord_lat']]

          if category in Variables.removed_markers.keys():
            for marker in Variables.removed_markers[category]:
              if str(marker['lng']) == el_coords[0] and str(marker['lat']) == el_coords[1]:
                deleted = True

          if not deleted:
            wohnungen = "N.A." if ele['anz_wohnungen'] == "-" else ele['anz_wohnungen']
            ez = "N.A." if ele['ez'] == "-" else ele['ez']
            dz = "N.A." if ele['dz'] == "-" else ele['dz']
            miete_ab = "N.A." if ele['miete_ab'] == "-" else f"{ele['miete_ab']} €"
            miete_bis = "N.A." if ele['miete_bis'] == "-" else f"{ele['miete_bis']} €"
            distance = anvil.server.call('get_point_distance', marker_coords, el_coords)
            
            
            # Name of Object
            marker_details = f"<div class='objectName'>{ele['name']}</div>"
            # Tags
            marker_details += "<div class='tagContainer'>"
            marker_details += f"<p class='tag'>{ele['sektor']}</p>"
            marker_details += f"<p class='tag'>{ele['art']}</p>"
            spez = ele['spezialisierung'].split('|')
            for entry in spez:
              marker_details += f"<p class='tag'>{entry}</p>"
            marker_details += f"<p class='tag'>{ele['status']}</p>"
            marker_details += "</div>"
            # Year of Construction/Modernisation
            marker_details += f"<p>Year of construction: {ele['baujahr']}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # Contact Details
            marker_details += f"<p>{ele['strasse']}, {ele['plz']} {ele['ort']}"
            states = ['Berlin', 'Bremen', 'Hamburg']
            if not ele['bundesland'] in states:
              marker_details += f", {ele['bundesland']}</p>"
            else:
              marker_details += "</p>"
            marker_details += f"<p>{ele['telefon']}</p>"
            marker_details += f"<p>{ele['email']}</p>"
            marker_details += f"<p>{ele['webseite']}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # Operator
            if not ele['betreiber'] == "-":
              marker_details += f"<p>Operator: {ele['betreiber']}</p>"
            if not ele['tochterfirma1'] == "-":
              marker_details += f"<p>Subsidiary 1: {ele['tochterfirma1']}</p>"
            if not ele['tochterfirma2'] == "-":
              marker_details += f"<p>Subsidiary 2: {ele['tochterfirma2']}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            #Flats
            marker_details += f"<p><b>Number of apartments:</b> {wohnungen}</p>"
            marker_details += f"<p><b>Single rooms:</b> {ez}</p>"
            marker_details += f"<p><b>Double rooms:</b> {dz}</p>"
            marker_details += f"<p><b>Rent starting from:</b> {miete_ab}</p>"
            marker_details += f"<p><b>Rent ending at:</b> {miete_bis}</p>"
            marker_details += "<div class='line'></div>"
            marker_details += f"<p><b>Holder ID:</b> {ele['traeger_id']}</p>"
            if not self.role == 'guest':
              marker_details += "<div class='rmv_container'><button id='remove' class='btn btn-default'>Remove Marker</button></div>"
  
            # Create Popup for Element
            popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
              f"<p class='popup_name'><b>{ele['name']}</b></p>"
              f"<p class='popup_type'>{ele['sektor']}</p>"
              f"<p class='popup_distance'>{distance} km to the location</p>"
              "<p class='popup_betreiber_label'><b>Operator:</b></p>"
              f"<p class='popup_betreiber'>{ele['betreiber']}</p>"
              f"<p class='popup_status'><b>Status:</b> {ele['status']}</p>"
            )

        elif category == 'nursing-schools':

          if category in Variables.removed_markers.keys():
            for marker in Variables.removed_markers[category]:
              if str(marker['lng']) == el_coords[0] and str(marker['lat']) == el_coords[1]:
                deleted = True

          if not deleted:
            distance = anvil.server.call('get_point_distance', marker_coords, el_coords)
  
            # Name of Object
            marker_details = f"<div class='objectName'>{name}</div>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # Contact Details
            marker_details += f"<p>{street}, {postcode} {city}</p>"
            marker_details += f"<p>{telefon}</p>"
            marker_details += f"<p>{email}</p>"
            marker_details += f"<p>{web}</p>"
            # Parting Line
            marker_details += "<div class='partingLine'></div>"
            # Informations
            marker_details += f"<p>Degree: {degree}</p>"
            marker_details += f"<p>Parttime Education: {parttime_education}</p>"
            marker_details += f"<p>Certificate: {certificate}</p>"
            marker_details += f"<p>Inserted: {inserted}</p>"
            marker_details += f"<p>Updated: {updated}</p>"
            if not self.role == 'guest':
              marker_details += "<div class='rmv_container'><button id='remove' class='btn btn-default'>Remove Marker</button></div>"
  
            popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
              f"<p class='popup_name'><b>{name}</b></p>"
              f"<p class='popup_type'>Nursing School</p>"
              f"<p class='popup_distance'>{distance} km  to the location</p>"
            )
          
        # Check if Category is not Bus or Tram or PflegeDB
        else:

          if category in Variables.removed_markers.keys():
            for marker in Variables.removed_markers[category]:
              if marker['lng'] == el_coords[0] and marker['lat'] == el_coords[1]:
                deleted = True

          if not deleted:
            distance = anvil.server.call('get_point_distance', marker_coords, el_coords)
            
            # Create Popup for Element
            marker_details = f'<b>ID:</b> {o_id}'
            marker_details += f'<br>'
            marker_details += f'<b>Name:</b>'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;{name}'
            marker_details += f'<br>'
            marker_details += f'<b>Operator:</b>'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;{operator}'
            marker_details += f'<br>'
            marker_details += f'<b>Adresse:</b>'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;{street} {housenumber}'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;{postcode}, {city} {suburb}'
            marker_details += f'<br>'
            marker_details += f'<b>Contact</b>'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Phone: {phone}'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Email: {email}'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Webpage:'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;&nbsp;&nbsp;{website}'
            marker_details += f'<br>'
            marker_details += f'<b>Informations</b>'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Category: {healthcare}'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Speciality: {speciality}'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Opening hours:'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;&nbsp;&nbsp;{opening_hours}'
            marker_details += f'<br>'
            marker_details += f'&nbsp;&nbsp;Wheelchair accessible: {wheelchair}'
            if not self.role == 'guest':
              marker_details += "<div class='rmv_container'><button id='remove' class='btn btn-default'>Remove Marker</button></div>"
            
            popup = mapboxgl.Popup({'offset': 25, 'className': 'markerPopup'}).setHTML(
              f"<p class='popup_name'><b>{name}</b></p>"
              f"<p class='popup_type'>{category.capitalize()}</p>"
              f"<p class='popup_distance'>{distance} km  to the location</p>"
            )

        if not deleted:

          # Add Icon to the Map
          newicon = mapboxgl.Marker(el, {'anchor': 'bottom'}).setLngLat(el_coords).setOffset([0, 0]).addTo(self.mapbox).setPopup(popup).setPopup(name_popup)
          newiconElement = newicon.getElement()
          self.addHoverEffect(newiconElement, popup, newicon, ele, category, marker_details)
          # anvil.js.call('addHoverEffect', newiconElement, popup, self.mapbox, newicon, ele, category, marker_details, self.role)
  
          # Add current Element-Icon to Icon-Array
          icons.append(newicon)

    # Refresh global Variables
    Variables.activeIcons.pop(f'{category}', None)
    Variables.icons.update({f'{category}': icons})
    Variables.activeIcons.update({f'{category}': icons})
    last_bbox = bbox
    Variables.last_cat = f'{category}'

def addPopup():
  print('Added')

def get_current_date_as_string():
  with anvil.server.no_loading_indicator:
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
    return f"{day}.{month}.{year} {hour}:{minute}"