#***POI-Layer***
#     dlen = anvil.server.call('get_len_of_features2')
  
#     i = 0
#     check = 0
#     gm_id = 0
#     data = []
  
#     #while check < dlen:
#     while check < 50000:
    
#       #Create index-variable
#       j = 0 
    
#       #Get data-pack from geojson
#       gm = anvil.server.call('get_json_bh', i)
    
#       #Increase Value of Data-Variable
#       i += 50000
  
#       #Check if index-variable is smaller than amount of data-pack
#       while j < len(gm):
  
#         #Append data-pack to local data
#         data.append(gm[j])
      
#         #Increase index-variable
#         j += 1
#         gm_id += 1
      
#       #Get new value for municipalities-amount  
#       check = len(data)
  
#     for el in data:

#       lnglat = [el['lon'], el['lat']]
    
#       html_el = document.createElement('div')
    
#       html_el.className = 'icon'
#       html_el.style.backgroundImage = f'url(https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Zeichen_224_-_Haltestelle%2C_StVO_2017.svg/2048px-Zeichen_224_-_Haltestelle%2C_StVO_2017.svg.png)'
#       html_el.style.width = '20px'
#       html_el.style.height = '20px'
#       html_el.style.backgroundSize = '100%'
#       html_el.style.backgroundrepeat = 'no-repeat'
    
#       poi_marker = mapboxgl.Marker(html_el).setLngLat(lnglat).addTo(self.mapbox)
#***End of POI-Layer***