import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
def poi_data(topic):

  if topic == 'bus_station':

    # Open POI-Data File and save all Data as JSON
    response = open('./src/poi/busstation.json', 'r')

  elif topic == 'tram_station':

    # Open POI-Data File and save all Data as JSON
    response = open('./src/poi/tramstation.json', 'r')

  else:

    #Open POI-Data File and save all Data as JSON
    response = open('./src/poi/all_data.json', 'r')

  raw_json = response.read()
  data = json.loads(raw_json)

  #Create empty Array for sendable Data
  new_data = []

  if topic == 'bus_station':

    # Loop through every Item in Data
    for el in data['elements']:

      # Get coordinates of current Icon
      el_coords = [el['lon'], el['lat']]

      # Check if Icon is inside visible Bounding Box
      if bbox[0] < el_coords[1] < bbox[2] and bbox[1] < el_coords[0] < bbox[3]:

        # Create empty JSON-Structure for Marker *Part 1*
        raw_data = {
          'type': 'Feature',
          'properties': {},
          'geometry': {}
        }

        # Create empty JSON-Structure for Marker *Part 2*
        geo_data = {
          'type': 'Point',
          'coordinates': el_coords
        }

        # Check if different tags are available
        if 'name' in el['tags']:

          name = el['tags']['name']

        elif 'name:de' in el['tags']:

          name = el['tags']['name:de']

        else:

          name = 'N.A.'

        # Insert data into JSON-Structure
        prop_data = {
          'name': name
        }

        # Save data in new JSON-Structure
        raw_data['geometry'] = geo_data
        raw_data['properties'] = prop_data

        # Add Marker-JSON to SendArray
        new_data.append(raw_data)

  elif topic == 'tram_station':

    # Loop through every Item in Data
    for el in data['elements']:

      # Get coordinates of current Icon
      el_coords = [el['lon'], el['lat']]

      # Check if Icon is inside visible Bounding Box
      if bbox[0] < el_coords[1] < bbox[2] and bbox[1] < el_coords[0] < bbox[3]:

        # Create empty JSON-Structure for Marker *Part 1*
        raw_data = {
          'type': 'Feature',
          'properties': {},
          'geometry': {}
        }

        # Create empty JSON-Structure for Marker *Part 2*
        geo_data = {
          'type': 'Point',
          'coordinates': el_coords
        }

        # Check if different tags are available
        if 'name' in el['tags']:

          name = el['tags']['name']

        elif 'name:de' in el['tags']:

          name = el['tags']['name:de']

        else:

          name = 'N.A.'

        # Insert data into JSON-Structure
        prop_data = {
          'name': name
        }

        # Save data in new JSON-Structure
        raw_data['geometry'] = geo_data
        raw_data['properties'] = prop_data

        # Add Marker-JSON to SendArray
        new_data.append(raw_data)

  else:

    #Loop through every Item in Data
    for el in data['elements']:

      #Check if element has same topic as given topic
      if el['tags']['amenity'] == topic:

        #Create empty JSON-Structure for Marker *Part 1*
        raw_data = {
          'type': 'Feature',
          'properties': {},
          'geometry': {}
        }

        # Create empty JSON-Structure for Marker *Part 2*
        geo_data = {
          'type': 'Point',
          'coordinates': [el['lon'], el['lat']]
        }

        #Check if different tags are available
        if 'addr:city' in el['tags']:

          city = el['tags']['addr:city']

        else:

          city = 'N.A.'

        if 'addr:suburb' in el['tags']:

          suburb = el['tags']['addr:suburb']

        else:

          suburb = 'N.A.'

        if 'addr:street' in el['tags']:

          street = el['tags']['addr:street']

        else:

          street = 'N.A.'

        if 'addr:housenumber' in el['tags']:

          housenumber = el['tags']['addr:housenumber']

        else:

          housenumber = 'N.A.'

        if 'addr:postcode' in el['tags']:

          postcode = el['tags']['addr:postcode']

        else:

          postcode = 'N.A.'

        if 'contact:phone' in el['tags']:

          phone = el['tags']['contact:phone']

        elif 'phone' in el['tags']:

          phone = el['tags']['phone']

        else:

          phone = 'N.A.'

        if 'contact:website' in el['tags']:

          website = el['tags']['contact:website']

        else:

          website = 'N.A.'

        if 'healthcare' in el['tags']:

          healthcare = el['tags']['healthcare']

        else:

          healthcare = 'N.A.'

        if 'name' in el['tags']:

          name = el['tags']['name']

        else:

          name = 'N.A.'

        if 'opening_hours' in el['tags']:

          opening_hours = el['tags']['opening_hours']

        else:

          opening_hours = 'N.A.'

        if 'wheelchair' in el['tags']:

          wheelchair = el['tags']['wheelchair']

        else:

          wheelchair = 'N.A.'

        if 'healthcare:speciality' in el['tags']:

          fachrichtung = el['tags']['healthcare:speciality']

        else:

          fachrichtung = 'N.A.'

        if 'fax' in el['tags']:

          fax = el['tags']['fax']

        elif 'contact:fax' in el['tags']:

          fax = el['tags']['contact:fax']

        else:

          fax = 'N.A.'

        if 'email' in el['tags']:

          email = el['tags']['email']

        elif 'contact:email' in el['tags']:

          email = el['tags']['contact:email']

        else:

          email = 'N.A.'

        if 'operator' in el['tags']:

          operator = el['tags']['operator']

        else:

          operator = 'N.A.'

        #Insert data into JSON-Structure
        prop_data = {
          'id': el['id'],
          'city': city,
          'suburb': suburb,
          'street': street,
          'housenumber': housenumber,
          'postcode': postcode,
          'phone': phone,
          'fax': fax,
          'website': website,
          'email': email,
          'healthcare': healthcare,
          'healthcare:speciality': fachrichtung,
          'name': name,
          'operator': operator,
          'opening_hours': opening_hours,
          'wheelchair': wheelchair
        }

        #Save data in new JSON-Structure
        raw_data['geometry'] = geo_data
        raw_data['properties'] = prop_data

        #Add Marker-JSON to SendArray
        new_data.append(raw_data)

  print(len(new_data))

  #Send Array
  return (new_data)

anvil.server.wait_forever()