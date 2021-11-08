import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

hoveredStateId = None
activeLayer = None
marker = {}
start = True
x = 0
icons = {}
last_bbox_doc = 0
last_bbox_den = 0
last_bbox_cli = 0
last_bbox_hos = 0
last_bbox_nur = 0
last_bbox_pha = 0
last_bbox_soc = 0
last_bbox_vet = 0
last_cat = None