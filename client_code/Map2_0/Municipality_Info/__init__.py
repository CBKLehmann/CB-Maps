from ._anvil_designer import Municipality_InfoTemplate
from anvil import *
import anvil.server
import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Municipality_Info(Municipality_InfoTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    data = properties['data']
    self.id_text.text = data['key']
    self.name_text.text = data['gm_name']
    self.area_text.text = f"{data['demographic']['flaeche']} km²"
    self.population_text.text = data['demographic']['bevoelkerung_ges']
    self.population_per_km_text.text = data['demographic']['bevoelkerung_jekm2']
    self.verstaedterung_text.text = data['demographic']['verstaedterung_bez']
    self.data_row_all.item = {
      'gender': 'All',
      'overall': data['demographic']['bevoelkerung_ges'],
      'u_3': data['exact_demographic']['all_u3'],
      '3_u6': data['exact_demographic']['all_3tou6'],
      '6_u10': data['exact_demographic']['all_6tou10'],
      '10_u15': data['exact_demographic']['all_10tou15'],
      '15_u18': data['exact_demographic']['all_15tou18'],
      '18_u20': data['exact_demographic']['all_18tou20'],
      '20_u25': data['exact_demographic']['all_20tou25'],
      '25_u30': data['exact_demographic']['all_25tou30'],
      '30_u35': data['exact_demographic']['all_30tou35'],
      '35_u40': data['exact_demographic']['all_35tou40'],
      '40_u45': data['exact_demographic']['all_40tou45'],
      '45_u50': data['exact_demographic']['all_45tou50'],
      '50_u55': data['exact_demographic']['all_50tou55'],
      '55_u60': data['exact_demographic']['all_55tou60'],
      '60_u65': data['exact_demographic']['all_60tou65'],
      '65_u75': data['exact_demographic']['all_65tou75'],
      '75plus': data['exact_demographic']['all_75']
    }
    self.data_row_men.item = {
      'gender': 'Men',
      'overall': data['exact_demographic']['man_compl'],
      'u_3': data['exact_demographic']['man_u3'],
      '3_u6': data['exact_demographic']['man_3tou6'],
      '6_u10': data['exact_demographic']['man_6tou10'],
      '10_u15': data['exact_demographic']['man_10tou15'],
      '15_u18': data['exact_demographic']['man_15tou18'],
      '18_u20': data['exact_demographic']['man_18tou20'],
      '20_u25': data['exact_demographic']['man_20tou25'],
      '25_u30': data['exact_demographic']['man_25tou30'],
      '30_u35': data['exact_demographic']['man_30tou35'],
      '35_u40': data['exact_demographic']['man_35tou40'],
      '40_u45': data['exact_demographic']['man_40tou45'],
      '45_u50': data['exact_demographic']['man_45tou50'],
      '50_u55': data['exact_demographic']['man_50tou55'],
      '55_u60': data['exact_demographic']['man_55tou60'],
      '60_u65': data['exact_demographic']['man_60tou65'],
      '65_u75': data['exact_demographic']['man_65tou75'],
      '75plus': data['exact_demographic']['man_75']
    }
    self.data_row_women.item = {
      'gender': 'Woman',
      'overall': data['exact_demographic']['woman_compl'],
      'u_3': data['exact_demographic']['woman_u3'],
      '3_u6': data['exact_demographic']['woman_3tou6'],
      '6_u10': data['exact_demographic']['woman_6tou10'],
      '10_u15': data['exact_demographic']['woman_10tou15'],
      '15_u18': data['exact_demographic']['woman_15tou18'],
      '18_u20': data['exact_demographic']['woman_18tou20'],
      '20_u25': data['exact_demographic']['woman_20tou25'],
      '25_u30': data['exact_demographic']['woman_25tou30'],
      '30_u35': data['exact_demographic']['woman_30tou35'],
      '35_u40': data['exact_demographic']['woman_35tou40'],
      '40_u45': data['exact_demographic']['woman_40tou45'],
      '45_u50': data['exact_demographic']['woman_45tou50'],
      '50_u55': data['exact_demographic']['woman_50tou55'],
      '55_u60': data['exact_demographic']['woman_55tou60'],
      '60_u65': data['exact_demographic']['woman_60tou65'],
      '65_u75': data['exact_demographic']['woman_65tou75'],
      '75plus': data['exact_demographic']['woman_75']
    }