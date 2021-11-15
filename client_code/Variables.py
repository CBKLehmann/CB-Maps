import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

hoveredStateId = None
activeLayer = None
marker = {}
start = True
x = 0
icons = {}
last_bbox_doc = [100000, 100000, 0, 0]
last_bbox_den = [100000, 100000, 0, 0]
last_bbox_cli = [100000, 100000, 0, 0]
last_bbox_hos = [100000, 100000, 0, 0]
last_bbox_nur = [100000, 100000, 0, 0]
last_bbox_pha = [100000, 100000, 0, 0]
last_bbox_soc = [100000, 100000, 0, 0]
last_bbox_vet = [100000, 100000, 0, 0]
last_bbox_bga = [100000, 100000, 0, 0]
last_cat = None