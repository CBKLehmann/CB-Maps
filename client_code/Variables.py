import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

hoveredStateId = None
activeLayer = None
marker = {}
start = True
x = 0
data = {
      "type": "feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-77.03238901390978, 38.913188059745586]
      },
      "properties": {
        "title": "Mapbox DC"
      }
    }