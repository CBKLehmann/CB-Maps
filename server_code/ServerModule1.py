import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import anvil.pdf

@anvil.server.callable
def create_pdf():
  
  pdf = anvil.pdf.render_form('Form1')
  return pdf
