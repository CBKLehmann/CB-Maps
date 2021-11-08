import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

hoveredStateId = None
activeLayer = None
marker = {}
start = True
x = 0
icons = {}
last_zoom = 100000
last_bbox = 0