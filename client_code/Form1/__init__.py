from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.writeDT_Table()
    
  def writeDT_Table(self):
    self.dt_panel.items = [
      {'dt': 'Berlin, LK', '2019': '2019 Actual', '2030': '2030 Forecast', 'change': 'Change in %'},
      {'dt': 'Population', '2019': '3669491', '2030': '', 'change': ''},
      {'dt': 'Population 65-74', '2019': '326584', '2030': '999999', 'change': '999%'},
      {'dt': 'Population 75+', '2019': '377957', '2030': '999999', 'change': '999%'},
      {'dt': 'Patients receiving full inpatient care', '2019': '28511', '2030': '999999', 'change': '999%'},
    ]
