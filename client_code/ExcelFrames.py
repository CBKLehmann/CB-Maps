import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

cover_data = {
  'title': 'COVER',
  'print_area': 'A1:P63',
  'fit_to_pages': (1, 1),
  'columns_width': [
    10.88, 6.88, 14.88, 13.13, 9.38, 9.00, 6.25, 5.00, 4.13, 7.00, 10.00, 9.00, 10.38, 7.63, 6.25, 9.00
  ],
  'landscape': False,
  'data': [
    {
      'type': 'text',
      'insert': 'merge',
      'cell': 'A22:P22',
      'content': 'MARKET STUDY',
      'format': {
        'align': 'center',
        'font_size': 72,
        'font': 'Segoe UI Black'
      }
    },
    {
      'type': 'text',
      'insert': 'merge',
      'cell': 'A24:P24',
      'content': None,
      'format': {
        'align': 'center',
        'font_size': 48,
        'font': 'Segoe UI Black',
        'color': '#BFB273'
      }
    },
    {
      'type': 'text',
      'insert': 'merge',
      'cell': 'A25:P25',
      'content': None,
      'format': {
        'align': 'center',
        'font_size': 48,
        'font': 'Segoe UI Black',
        'color': '#BFB273'
      }
    },
    {
      'type': 'image',
      'cell': 'D41',
      'file': 'img/cb_logo.png',
      'style': {}
    }
  ]
}
summary_data = {
        'title': 'SUMMARY',
        'print_area': 'A1:M81',
        'fit_to_pages': (1, 1),
        'columns_width': [
            43.27, 26.75, 19, 19, 1.55, 9.00, 6.25, 5, 4.08, 7, 13.08, 2, 9.55
        ],
        'landscape': False,
        'data': [
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A1:B1',
                'content': 'EXECUTIVE SUMMARY',
                'format': {
                    'font_size': 24,
                    'font': 'Segoe UI Black',
                    'color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A4',
                'content': 'General Information',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A6',
                'content': 'Zip Code',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A7',
                'content': 'City',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A8',
                'content': 'District',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A9',
                'content': 'Federal State',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A10',
                'content': 'Radius of analysis',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A11',
                'content': 'Address',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A13',
                'content': 'Demographic trend',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A14',
                'content': 'Population Berlin',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A15',
                'content': 'Berlin, LK',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A16',
                'content': 'Population',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A17',
                'content': 'There of Population 65-79',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A18',
                'content': 'There of Population 80+',
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A20:B20',
                'content': 'Patients receiving full inpatient care scenarios',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A21',
                'content': 'Break even care rate',
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A22:E22',
                'content': 'Each percent-point greater than the break even care rate indicates an increasing demand on care capacities.',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A24',
                'content': 'Scenario 1',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A25:H25',
                'content': 'In scenario 1 the relative situation (product of nursing home rate and care rate) as in 2020 is assumed to be constant for the entire forecasting period.',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A26',
                'content': 'Care Rate of Population',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A27',
                'content': 'There of nursing home rate',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A28',
                'content': 'Patients receiving full inpatient care',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A29',
                'content': 'Occupancy rate',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A30',
                'content': 'Beds',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A31',
                'content': 'Free Beds',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A33',
                'content': 'Scenario 2',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A34:H34',
                'content': 'In scenario 2 we assume a very small increase rate of the product of care rate and nursing home rate of about 0.003 percent-points.',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A35',
                'content': 'Care Rate of Population',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A36',
                'content': 'There of nursing home rate',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A37',
                'content': 'Patients receiving full inpatient care',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A38',
                'content': 'Occupancy rate',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A39',
                'content': 'Beds',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A40',
                'content': 'Free Beds',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A42',
                'content': 'Demand',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A43',
                'content': 'Number of inpatients',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A44',
                'content': 'Number of inpatients forecast Scenario 1',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A45',
                'content': 'Number of inpatients forecast Scenario 2',
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A46:E46',
                'content': 'In 2030 the number of inpatients will based on our scenarios be between 64 and 69 (in average about 66).',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A47:E47',
                'content': 'In 2035 the number of inpatients will based on our scenarios be between 67 and 72 (in average about 70).',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A49',
                'content': 'Supply',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A50',
                'content': 'Beds',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A51',
                'content': 'Nursing homes',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A52',
                'content': 'Nursing homes in planning',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A53',
                'content': 'Nursing homes under construction',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A54',
                'content': 'Beds in planning',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A55',
                'content': 'Beds under construction',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A56',
                'content': 'Loss of beds due to \nregulations of federal state',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A57',
                'content': 'Adjusted number of beds \n(incl. beds in planning and under construction)',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A58',
                'content': 'Occupancy rate',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A59',
                'content': 'Beds in reserve',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A60',
                'content': 'Median Invest Cost',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A62',
                'content': 'Surplus or deficit of beds IC',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A63',
                'content': 'Scenario 1',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A64',
                'content': 'Supply',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A65',
                'content': 'Demand',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A66',
                'content': 'surplus/deficit',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A68',
                'content': 'Scenario 2',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A69',
                'content': 'Supply',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A70',
                'content': 'Demand',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A71',
                'content': 'surplus/deficit',
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A72:E72',
                'content': 'In 2030 the surplus/deficit on beds based on our scenarios is between 8 and 3 (in average 6).',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A73:E73',
                'content': 'In 2035 the surplus/deficit on beds based on our scenarios is between 5 and 0 (in average 2).',
                'format': {
                    'italic': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A75',
                'content': 'Market shares',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A76',
                'content': 'Number of operators',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A77',
                'content': 'Median Number of beds',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A78',
                'content': 'Median Year of construction',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A79',
                'content': '% Public operators',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A80',
                'content': '% Non-profit operators',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A81',
                'content': '% Private operators',
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B4',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B13',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B14',
                'content': 3664088,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B15',
                'content': '2020 Actual',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B16',
                'content': 3669491,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B17',
                'content': 484900,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B18',
                'content': 227100,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B20',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B21',
                'content': .016,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B26',
                'content': .042,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B27',
                'content': .183,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B28',
                'content': 28525,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B29',
                'content': .8539,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B30',
                'content': 33406,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B31',
                'content': 4881,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B35',
                'content': .042,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B36',
                'content': .183,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B37',
                'content': 28525,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B38',
                'content': .8539,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B39',
                'content': 33406,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B40',
                'content': 4881,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B42',
                'content': 'Radius:',
                'format': {
                    'align': 'right',
                    'bottom': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B43',
                'content': 70,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B49',
                'content': 'Radius:',
                'format': {
                    'align': 'right',
                    'bottom': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B50',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B51',
                'content': 2,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B52',
                'content': 0,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B53',
                'content': 0,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B54',
                'content': 0,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B55',
                'content': 0,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B57',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B58',
                'content': .97,
                'format': {
                    'align': 'right',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B59',
                'content': 2,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B60',
                'content': 15.18,
                'format': {
                    'align': 'right',
                    'num_format': '#,##0.00 €'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B62',
                'content': 'Radius:',
                'format': {
                    'align': 'right',
                    'bottom': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B64',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B65',
                'content': 70,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B69',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B70',
                'content': 70,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B75',
                'content': 'Radius:',
                'format': {
                    'align': 'right',
                    'bottom': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B76',
                'content': 1,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B77',
                'content': 36,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B78',
                'content': 1996,
                'format': {
                    'align': 'right',
                    'num_format': '0'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B79',
                'content': .7,
                'format': {
                    'align': 'right',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B80',
                'content': .2,
                'format': {
                    'align': 'right',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B81',
                'content': .1,
                'format': {
                    'align': 'right',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C4',
                'content': '',
                'format': {
                    'align': 'left',
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C13',
                'content': '',
                'format': {
                    'align': 'left',
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C15',
                'content': '2030 Forecast',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C16',
                'content': 3877900,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C17',
                'content': 559500,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C18',
                'content': 239600,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C20',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C21',
                'content': .019,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C26',
                'content': .045,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C27',
                'content': .183,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C28',
                'content': 31964,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C29',
                'content': .95,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C30',
                'content': 33646,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C31',
                'content': 1682,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C35',
                'content': .048,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C36',
                'content': .183,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C37',
                'content': 34361,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C38',
                'content': .95,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C39',
                'content': 36169,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C40',
                'content': 1751,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'C42:D42',
                'content': '15 minutes of walking',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C44',
                'content': 64,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C45',
                'content': 69,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'C49:D49',
                'content': '15 minutes of walking',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C56',
                'content': -144,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C57',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C58',
                'content': .95,
                'format': {
                    'align': 'right',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C59',
                'content': 4,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'C62:D62',
                'content': '15 minutes of walking',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C64',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C65',
                'content': 64,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C66',
                'content': 8,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C69',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C70',
                'content': 69,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C71',
                'content': 3,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'C75:D75',
                'content': '15 minutes of walking',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D4',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D6',
                'content': 10178,
                'format': {
                    'align': 'right',
                    'bold': True,
                    'num_format': '0'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D7',
                'content': 'Berlin',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D8',
                'content': 'Berlin',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D9',
                'content': 'Berlin',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'C10:D10',
                'content': '15 minutes of walking',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'B11:D11',
                'content': 'Blumberger Damm 201, 12687 Berlin, Germany',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D13',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D15',
                'content': '2035 Forecast',
                'format': {
                    'align': 'right',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D16',
                'content': 3921400,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D17',
                'content': 587600,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D18',
                'content': 244300,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D20',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D21',
                'content': .02,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D26',
                'content': .046,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D27',
                'content': .183,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D28',
                'content': 33276,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D29',
                'content': .95,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D30',
                'content': 35027,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D31',
                'content': 1808,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D35',
                'content': .05,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D36',
                'content': .183,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D37',
                'content': 35772,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D38',
                'content': .95,
                'format': {
                    'align': 'right',
                    'num_format': '0.0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D39',
                'content': 37655,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D40',
                'content': 1883,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D42',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D44',
                'content': 67,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D45',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D49',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D56',
                'content': -114,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D57',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D58',
                'content': .95,
                'format': {
                    'align': 'right',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D59',
                'content': 4,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D62',
                'content': '',
                'format': {
                    'bold': True,
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D64',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D65',
                'content': 67,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D66',
                'content': 5,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D69',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D70',
                'content': 72,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D71',
                'content': 0,
                'format': {
                    'align': 'right'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'F29:M30',
                'content': 0,
                'format': {
                    'align': 'center',
                    'font_size': 20,
                    'font': "Segoe UI Black",
                    'num_format': '0.00'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'BB2',
                'content': 100,
                'format': {
                    'num_format': '0.00'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'BB1',
                'content': 0,
                'format': {
                    'num_format': '0.00'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'F27:M28',
                'content': 'Purchasing Power',
                'format': {
                    'align': 'center',
                    'font_size': 20,
                    'font': "Segoe UI Black"
                }
            },
            {
                'type': 'image',
                'cell': 'K1',
                'file': 'img/cb_logo.png',
                'style': {
                    'x_scale': .21,
                    'y_scale': .085,
                    'x_offset': 50,
                    'y_offset': 10
                }
            },
            {
                'type': 'image',
                'cell': 'F4',
                'file': 'exampleMap.png',
                'style': {
                    'x_scale': .5,
                    'y_scale': .5
                }
            },
            {
                'type': 'chart',
                'subtype': 'column',
                'position': 'F39',
                'series': [
                    {
                        'values': '=SUMMARY!$B$43',
                        'name': 'Number of inpatients',
                        'data_labels': {
                            'value': True
                        },
                        'fill': {
                            'color': '#404040'
                        },
                        'overlap': -20},
                    {
                        'values': '=SUMMARY!$B$50',
                        'name': 'Beds',
                        'data_labels': {
                            'value': True
                        },
                        'fill': {
                            'color': '#BFB273'
                        }
                    },
                    {
                        'values': '=SUMMARY!$C$44',
                        'name': 'Number of inpatients forecast 2030 Scenario 1',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'large_grid',
                            'fg_color': '#BFB273',
                            'bg_color': '#404040'
                        }
                    },
                    {
                        'values': '=SUMMARY!$C$57',
                        'name': 'Adjusted number of beds (incl. beds in planning and under construction) 2030',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'large_grid',
                            'fg_color': '#404040',
                            'bg_color': '#BFB273'
                        }
                    },
                    {
                        'values': '=SUMMARY!$D$44',
                        'name': 'Number of inpatients forecast 2035 Scenario 1',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'dotted_diamond',
                            'fg_color': '#BFB273',
                            'bg_color': '#404040'
                        }
                    },
                    {
                        'values': '=SUMMARY!$D$57',
                        'name': 'Adjusted number of beds (incl. beds in planning and under construction) 2035',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'dotted_diamond',
                            'fg_color': '#404040',
                            'bg_color': '#BFB273'
                        }
                    },
                ],
                'styles': {
                    'x_axis': {
                        'visible': False
                    },
                    'y_axis': {
                        'visible': False,
                        'major_gridlines': {
                            'visible': False
                        }
                    },
                    'title': {
                        'name': 'DEMAND & SUPPLY',
                        'name_font': {
                            'name': 'Segoe UI Black'
                        },
                        'layout': {
                            'y': 0,
                            'x': 0.25
                        }
                    },
                    'legend': {
                        'position': 'bottom',
                        'name_font': {
                            'name': 'Segoe UI'
                        },
                        'layout': {
                            'x': 0,
                            'y': 0.7,
                            'width': 1,
                            'height': 0.35
                        }
                    },
                    'plotarea': {
                        'layout': {
                            'x': 0,
                            'y': 0.125,
                            'width': 1,
                            'height': 0.5
                        }
                    },
                    'chartarea': {
                        'border': {
                            'none': True
                        }
                    },
                    'size': {
                        'width': 430,
                        'height': 300
                    },
                    'chart': {}
                }
            },
            {
                'type': 'chart',
                'subtype': 'column',
                'position': 'F55',
                'series': [
                    {
                        'values': '=SUMMARY!$B$43',
                        'name': 'Number of inpatients',
                        'data_labels': {
                            'value': True
                        },
                        'fill': {
                            'color': '#404040'
                        },
                        'overlap': -20},
                    {
                        'values': '=SUMMARY!$B$50',
                        'name': 'Beds',
                        'data_labels': {
                            'value': True
                        },
                        'fill': {
                            'color': '#BFB273'
                        }
                    },
                    {
                        'values': '=SUMMARY!$C$45',
                        'name': 'Number of inpatients forecast 2030 Scenario 2',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'large_grid',
                            'fg_color': '#BFB273',
                            'bg_color': '#404040'
                        }
                    },
                    {
                        'values': '=SUMMARY!$C$57',
                        'name': 'Adjusted number of beds (incl. beds in planning and under construction) 2030',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'large_grid',
                            'fg_color': '#404040',
                            'bg_color': '#BFB273'
                        }
                    },
                    {
                        'values': '=SUMMARY!$D$45',
                        'name': 'Number of inpatients forecast 2035 Scenario 2',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'dotted_diamond',
                            'fg_color': '#BFB273',
                            'bg_color': '#404040'
                        }
                    },
                    {
                        'values': '=SUMMARY!$D$57',
                        'name': 'Adjusted number of beds (incl. beds in planning and under construction) 2035',
                        'data_labels': {
                            'value': True
                        },
                        'pattern': {
                            'pattern': 'dotted_diamond',
                            'fg_color': '#404040',
                            'bg_color': '#BFB273'
                        }
                    }
                ],
                'styles': {
                    'x_axis': {
                        'visible': False
                    },
                    'y_axis': {
                        'visible': False,
                        'major_gridlines': {
                            'visible': False
                        }
                    },
                    'legend': {
                        'position': 'bottom',
                        'name_font': {
                            'name': 'Segoe UI'
                        },
                        'layout': {
                            'x': 0,
                            'y': 0.6,
                            'width': 1,
                            'height': 0.45
                        }
                    },
                    'plotarea': {
                        'layout': {
                            'x': 0,
                            'y': 0.02,
                            'width': 1,
                            'height': 0.5
                        }
                    },
                    'chartarea': {
                        'border': {
                            'none': True
                        }
                    },
                    'size': {
                        'width': 430,
                        'height': 250
                    },
                    'chart': {}
                }
            },
            {
                'type': 'chart',
                'subtype': 'bar',
                'spec_type': 'stacked',
                'position': 'F31',
                'series': [
                    {
                        'values': '=SUMMARY!$BB$1',
                        'fill': {
                            'color': '#BFB273'
                        }
                    },
                    {
                        'values': '=SUMMARY!$BB$2',
                        'fill': {
                            'color': '#404040'
                        }
                    }
                ],
                'styles': {
                    'x_axis': {
                        'visible': False,
                        'major_gridlines': {
                            'visible': False
                        }
                    },
                    'y_axis': {
                        'visible': False,
                        'major_gridlines': {
                            'visible': False
                        }
                    },
                    'legend': {
                        'none': True
                    },
                    'plotarea': {
                        'layout': {
                            'x': .1,
                            'y': 0,
                            'width': .9,
                            'height': 1
                        }
                    },
                    'chartarea': {
                        'border': {
                            'none': True
                        }
                    },
                    'size': {
                        'width': 430,
                        'height': 50
                    },
                    'chart': {}
                }
            },
            {
                'type': 'chart',
                'subtype': 'doughnut',
                'position': 'F69',
                'series': [
                    {
                        'name': 'MARKET SHARES',
                        'categories': '=SUMMARY!$A$78:$A$80',
                        'values': '=SUMMARY!$B$78:$B$80',
                        'data_labels': {
                            'value': True,
                            'custom': [
                                {
                                    'value': 'SUMMARY!$B$78',
                                    'font': {
                                        'color': '#FFFFFF',
                                        'name': 'Segoe UI',
                                        'size': 7
                                    }
                                },
                                {
                                    'value': 'SUMMARY!$B$79',
                                    'font': {
                                        'color': '#000000',
                                        'name': 'Segoe UI',
                                        'size': 7
                                    }
                                },
                                {
                                    'value': 'SUMMARY!$B$80',
                                    'font': {
                                        'color': '#000000',
                                        'name': 'Segoe UI',
                                        'size': 7
                                    }
                                }
                            ]
                        },
                        'points': [
                            {
                                'fill': {
                                    'color': '#404040'
                                }
                            },
                            {
                                'fill': {
                                    'color': '#D9D9D6'
                                }
                            },
                            {
                                'fill': {
                                    'color': '#BFB273'
                                }
                            }
                        ]
                    }
                ],
                'styles': {
                    'title': {
                        'name': 'MARKET SHARES'
                    },
                    'legend': {
                        'position': 'bottom',
                        'name_font': {
                            'name': 'Segoe UI'
                        }
                    },
                    'size': {
                        'width': 430,
                        'height': 230
                    },
                    'chartarea': {
                        'border': {
                            'none': True
                        }
                    },
                    'chart': {}
                }
            }
        ]
    }
nca_data = {
        'title': 'COMPETITOR_ANALYSIS_NH',
        'print_area': 'A1:L1048576',
        'fit_to_pages': (1, 0),
        'columns_width': [5.82, 28, 9.64, 8.91, 9.36, 9.73, 12.18, 14.36, 10.55, 18.64, 13.73, 13.45],
        'row_height': 50,
        'row_start': 31,
        'row_count': 6,
        'landscape': False,
        'data': [
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A1:G1',
                'content': 'NURSING COMPETITOR ANALYSIS',
                'format': {
                    'font_size': 24,
                    'font': 'Segoe UI Black',
                    'color': '#BFB273'
                }
            },
            {
                'type': 'image',
                'cell': 'K1',
                'file': 'img/cb_logo.png',
                'style': {
                    'x_scale': .21,
                    'y_scale': .09,
                    'y_offset': 10,
                    'x_offset': 80
                }
            },
            {
                'type': 'image',
                'cell': 'A4',
                'file': 'map_image_5a7990_nh.png',
                'style': {
                    'x_scale': .8,
                    'y_scale': .8
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'J5',
                'content': 'Median Nursing charge (PG 3)',
                'format': {
                    'align': 'right',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'J6',
                'content': 'Median Specific co-payment',
                'format': {
                    'align': 'right',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'J7',
                'content': 'Median Invest costs',
                'format': {
                    'align': 'right',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'J8',
                'content': 'Median Board and lodging',
                'format': {
                    'align': 'right',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'K5',
                'content': 54.33,
                'format': {
                    'align': 'right',
                    'num_format': '#,##0.00 €',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'K6',
                'content': 12.84,
                'format': {
                    'align': 'right',
                    'num_format': '#,##0.00 €',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'K7',
                'content': 18.92,
                'format': {
                    'align': 'right',
                    'num_format': '#,##0.00 €',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'K8',
                'content': 18.36,
                'format': {
                    'align': 'right',
                    'num_format': '#,##0.00 €',
                    'color': '#FFFFFF'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A32',
                'content': 'no.',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B32',
                'content': 'name',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C32',
                'content': 'no. of beds',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D32',
                'content': 'single rooms',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E32',
                'content': 'double rooms',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'F32',
                'content': 'patients',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'G32',
                'content': 'rooms',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'H32',
                'content': 'sr-quota',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'I32',
                'content': 'occupancy',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'J32',
                'content': 'year of construction',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'K32',
                'content': 'status',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'L32',
                'content': 'operator',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'M32',
                'content': 'invest costs per day',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'N32',
                'content': 'MDK grade',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'chart',
                'subtype': 'doughnut',
                'position': 'J4',
                'series': [
                    {
                        'name': 'MEDIAN PRICE COMPOSITION',
                        'categories': '=COMPETITOR_ANALYSIS_NH!$J$5:JK$8',
                        'values': '=COMPETITOR_ANALYSIS_NH!$K$5:$K$8',
                        'data_labels': {
                            'value': True,
                            'custom': [
                                {
                                    'value': 'COMPETITOR_ANALYSIS_NH!$K$5',
                                    'font': {
                                        'color': '#FFFFFF',
                                        'name': 'Segoe UI Black',
                                        'size': 10
                                    }
                                },
                                {
                                    'value': 'COMPETITOR_ANALYSIS_NH!$K$6',
                                    'font': {
                                        'color': '#000000',
                                        'name': 'Segoe UI Black',
                                        'size': 10
                                    }
                                },
                                {
                                    'value': 'COMPETITOR_ANALYSIS_NH!$K$7',
                                    'font': {
                                        'color': '#000000',
                                        'name': 'Segoe UI Black',
                                        'size': 10
                                    }
                                },
                                {
                                    'value': 'COMPETITOR_ANALYSIS_NH!$K$8',
                                    'font': {
                                        'color': '#000000',
                                        'name': 'Segoe UI Black',
                                        'size': 10
                                    }
                                }
                            ]
                        },
                        'points': [
                            {
                                'fill': {
                                    'color': '#404040'
                                }
                            },
                            {
                                'fill': {
                                    'color': '#D9D9D6'
                                }
                            },
                            {
                                'fill': {
                                    'color': '#BFB273'
                                }
                            },
                            {
                                'fill': {
                                    'color': '#E5E0C7'
                                }
                            }
                        ]
                    }
                ],
                'styles': {
                    'title': {
                        'name': 'MEDIAN PRICE COMPOSITION'
                    },
                    'legend': {
                        'position': 'bottom',
                        'name_font': {
                            'name': 'Segoe UI'
                        },
                        'layout': {
                            'x': 0,
                            'y': .8,
                            'width': 1,
                            'height': .2
                        }
                    },
                    'size': {
                        'width': 330,
                        'height': 450
                    },
                    'chartarea': {
                        'border': {
                            'none': True
                        }
                    },
                    'plotarea': {
                        'layout': {
                            'x': .1,
                            'y': .2,
                            'width': .8,
                            'height': .5
                        }
                    },
                    'chart': {
                        'x_offset': 5
                    }
                }
            }
        ]
    }
reg_data = {
  'title': 'Regulations Overview',
        'print_area': 'A1:G12',
        'fit_to_pages': (1, 0),
        'columns_width': [10.71, 10.14, 32.71, 24.86, 50, 10.71, 10.14],
        'row_height': 36,
        'row_start': 1,
        'row_count': 12,
        'landscape': False,
        'data': [
          {
            'type': 'image',
            'cell': 'F1',
            'file': 'img/cb_logo.png',
            'style': {
                'x_scale': .21,
                'y_scale': .2,
                'y_offset': 10,
                'x_offset': 10
            }
          },
          {
            'type': 'text',
            'insert': 'merge',
            'cell': 'B2:F2',
            'content': 'Regulations of Federal State',
            'format': {
              'align': 'center',
              'valign': 'vcenter',
              'font_size': 26,
              'color': '#000000'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C4',
            'content': 'Federal State',
            'format': {
              'align': 'center',
              'color': '#000000',
              'bg_color': '#948a54',
              'font_size': 14,
              'border': 1,
              'bold': True
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C5',
            'content': '',
            'format': {
                'align': 'center',
                'color': '#000000',
                'border': 1,
                'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C6',
            'content': 'single room quota (min.)',
            'format': {
                'align': 'center',
                'color': '#000000',
                'border': 1,
                'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C7',
            'content': 'maximum home size',
            'format': {
                'align': 'center',
                'color': '#000000',
                'border': 1,
                'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C8',
            'content': 'minimum room size (sr/dr)',
            'format': {
                'align': 'center',
                'color': '#000000',
                'border': 1,
                'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C9',
            'content': 'minimum common area/resident',
            'format': {
                'align': 'center',
                'color': '#000000',
                'border': 1,
                'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C10',
            'content': 'comment',
            'format': {
              'align': 'center',
              'color': '#000000',
              'border': 1,
              'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'C11',
            'content': 'legal basis',
            'format': {
              'align': 'center',
              'color': '#000000',
              'border': 1,
              'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'merge',
            'cell': 'D4:E4',
            'content': 'Baden-Wurttemberg',
            'format': {
              'align': 'center',
              'color': '#000000',
              'bg_color': '#948a54',
              'font_size': 14,
              'border': 1,
              'bold': True
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'D5',
            'content': 'New',
            'format': {
              'align': 'center',
              'color': '#000000',
              'border': 1,
              'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'D6',
            'content': '100 %',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'D7',
            'content': '100 beds',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'D8',
            'content': '14m²/16m²*',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'D9',
            'content': '5m², min. 2/3 for living spaces',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'D10',
            'content': '/',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'merge',
            'cell': 'D11:E11',
            'content': 'WTPG, LHeimBauVO',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'E5',
            'content': 'Existing',
            'format': {
              'align': 'center',
              'color': '#000000',
              'border': 1,
              'bg_color': '#c4bd97'
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'E6',
            'content': '100 % (as of 2019)',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'E7',
            'content': '100 beds',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'E8',
            'content': '14m²/16m²*',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'E9',
            'content': '5m², min 2/3 for living spaces',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          },
          {
            'type': 'text',
            'insert': 'write',
            'cell': 'E10',
            'content': '*Transition period 10 years can be extended to 25 years',
            'format': {
              'align': 'center',
              'color': '#000000',
              'font_size': 10,
              'border': 1
            }
          }
        ]
}
ala_data = {
        'title': 'ASSISTED_LIVING_ANALYSIS',
        'print_area': 'A1:F57',
        'fit_to_pages': (1, 1),
        'columns_width': [39, 15.91, 16.33, 16.08, 16.73, 17.36],
        'landscape': False,
        'data': [
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A1:C1',
                'content': 'ASSISTED LIVING ANALYSIS',
                'format': {
                    'font_size': 24,
                    'font': 'Segoe UI Black',
                    'color': '#BFB273'
                }
            },
            {
                'type': 'image',
                'cell': 'E1',
                'file': 'img/cb_logo.png',
                'style': {
                    'x_scale': .21,
                    'y_scale': .09,
                    'y_offset': 10,
                    'x_offset': 130
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A4',
                'content': 'District Summary',
                'format': {
                    'bottom': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A5',
                'content': 'Population Salzlandkreis, LK',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A6',
                'content': 'Population 65-79',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A7',
                'content': 'Population 80+',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A8',
                'content': 'Population 65-79 (2030)',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A9',
                'content': 'Population 80+ (2030)',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A10',
                'content': 'inpatient care forecast district (2022-2030)',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A11',
                'content': 'active assisted apts. (adjusted)',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A12',
                'content': 'active apts. per 10.000 population',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A13',
                'content': 'active assisted living facilities',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A14',
                'content': 'planned/under construction assisted living facilities',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A15',
                'content': 'planned/under construction assisted apts. (adjusted)',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A16',
                'content': 'assisted Living facilities within 10km',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A17',
                'content': 'apts. within 10km',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A21',
                'content': 'Assisted Living Analysis in the region',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A22',
                'content': 'Supply',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A23',
                'content': '',
                'format': {
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A24',
                'content': 'active BW with apt. numbers',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A25',
                'content': 'active BW without apt. numbers',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A26',
                'content': 'active subtotal',
                'format': {
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A27',
                'content': 'under construction BW facilities with apt. Numbers',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A28',
                'content': 'under construction BW facilities without apt. Numbers',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A29',
                'content': 'under construction subtotal adjusted',
                'format': {
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A30',
                'content': 'planed BW facilities with apt. Numbers',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A31',
                'content': 'planed BW facilities without apt. numbers',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A32',
                'content': 'in planning subtotal adjusted',
                'format': {
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A33',
                'content': 'Total',
                'format': {
                    'border': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A35',
                'content': 'Demand',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A36',
                'content': '*Assume: % of 65+ population are in need of Assisted Living apt.',
                'format': {
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A37',
                'content': 0.01,
                'format': {
                    'border': True,
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A38',
                'content': 0.02,
                'format': {
                    'border': True,
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A39',
                'content': 0.03,
                'format': {
                    'border': True,
                    'bg_color': '#F1EFE2',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A40',
                'content': 0.04,
                'format': {
                    'border': True,
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A41',
                'content': 0.05,
                'format': {
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A42',
                'content': 0.07,
                'format': {
                    'border': True,
                    'bg_color': '#BFB273',
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A43',
                'content': 0.09,
                'format': {
                    'border': True,
                    'num_format': '0%'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A45:B45',
                'content': '* assume every apt accommodates 1,5 person'
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A47:B47',
                'content': 'REGIONAL DEMAND FOR ASSISTED LIVING',
                'format': {
                    'color': '#BFB273',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A48',
                'content': 'Holzminden',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A49',
                'content': 'Holzminden, LK 2022',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A50',
                'content': 'Holzminden, LK 2030',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A51',
                'content': 'potential demand in 2030 is',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B4',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B5',
                'content': 3669491,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B6',
                'content': 484900,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B7',
                'content': 227100,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B8',
                'content': 559500,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B9',
                'content': 239600,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B10',
                'content': 0.1206,
                'format': {
                    'align': 'right',
                    'bottom': True,
                    'num_format': '0.00%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B11',
                'content': 13870,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B12',
                'content': 37,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B13',
                'content': 211,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B14',
                'content': 11,
                'format': {
                  'align': 'right',
                  'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B15',
                'content': 1257,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B16',
                'content': 77,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B17',
                'content': 4889,
                'format': {
                    'align': 'right',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'B21:D21',
                'content': 'Berlin, LK',
                'format': {
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B22',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B23',
                'content': 'Facility No.',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B24',
                'content': 168,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B25',
                'content': 43,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B26',
                'content': 211,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B27',
                'content': 5,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B28',
                'content': 1,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B29',
                'content': 6,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B30',
                'content': 3,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B31',
                'content': 2,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B32',
                'content': 5,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B33',
                'content': 222,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B35',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B36',
                'content': 'Demand in 2022',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B37',
                'content': 125,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B38',
                'content': 250,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B39',
                'content': 375,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#F1EFE2',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B40',
                'content': 500,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B41',
                'content': 625,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B42',
                'content': 875,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#BFB273',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B43',
                'content': 1125,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B48',
                'content': 'national level',
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B49',
                'content': -56,
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B50',
                'content': -123,
                'format': {
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B51',
                'content': 'low',
                'format': {
                    'border': True,
                    'num_format': '0.00%',
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C4',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C5',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C6',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C7',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C8',
                'content': 0.1274,
                'format': {
                    'align': 'right',
                    'num_format': '0.00%',
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C9',
                'content': 0.003,
                'format': {
                    'bottom': True,
                    'align': 'right',
                    'num_format': '0.00%'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C10',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C11',
                'content': 'apts',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C12',
                'content': 'apts',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C13',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C14',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C15',
                'content': 'apts',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C16',
                'content': '',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C17',
                'content': 'apts',
                'format': {
                    'bottom': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C22',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C23',
                'content': 'apartments',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C24',
                'content': 308,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C25',
                'content': 0,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C26',
                'content': 308,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C27',
                'content': 29,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C28',
                'content': 0,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C29',
                'content': 29,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C30',
                'content': 70,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C31',
                'content': 0,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C32',
                'content': 70,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C33',
                'content': 407,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C35',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C36',
                'content': '+surplus/-deficit (2022)',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C37',
                'content': 306,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C38',
                'content': 181,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C39',
                'content': 56,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#F1EFE2',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C40',
                'content': -69,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C41',
                'content': -194,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C42',
                'content': -443,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#BFB273',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C43',
                'content': -693,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D22',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D23',
                'content': 'average apt./Facility',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D24',
                'content': 62,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D25',
                'content': 0,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D26',
                'content': 431,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True,
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D27',
                'content': 29,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D28',
                'content': 0,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D29',
                'content': 29,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True,
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D30',
                'content': 35,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D31',
                'content': 0,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D32',
                'content': 70,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True,
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D33',
                'content': 530,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bold': True,
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D35',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D36',
                'content': 'Demand in 2030',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D37',
                'content': 136,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D38',
                'content': 271,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D39',
                'content': 407,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#F1EFE2',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D40',
                'content': 542,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D41',
                'content': 678,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D42',
                'content': 949,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#BFB273',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D43',
                'content': 1220,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'E26:F26',
                'content': '(Existing apts in Pro-Forma)',
                'format': {
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'E33:F33',
                'content': '(Existing apts in Pro-Forma)',
                'format': {
                    'color': 'red'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E35',
                'content': '',
                'format': {
                    'bold': True,
                    'bg_color': '#E5E0C7'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E36',
                'content': '+surplus/-deficit (2030)',
                'format': {
                    'align': 'center',
                    'bold': True,
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E37',
                'content': 395,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E38',
                'content': 259,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E39',
                'content': 123,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#F1EFE2',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E40',
                'content': -12,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E41',
                'content': -148,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#E5E0C7',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E42',
                'content': -419,
                'format': {
                    'align': 'right',
                    'border': True,
                    'bg_color': '#BFB273',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E43',
                'content': -690,
                'format': {
                    'align': 'right',
                    'border': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'F39',
                'content': 'national level',
                'format': {
                    'align': 'center',
                    'bg_color': '#F1EFE2',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'F41',
                'content': 'small city',
                'format': {
                    'align': 'center',
                    'bg_color': '#E5E0C7',
                    'bold': True
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'F42',
                'content': 'top 30 city',
                'format': {
                    'align': 'center',
                    'bg_color': '#BFB273',
                    'bold': True
                }
            },
            {
                'type': 'chart',
                'subtype': 'column',
                'position': 'C45',
                'series': [
                    {
                        'values': '=ASSISTED_LIVING_ANALYSIS!$B$49',
                        'name': 'Holzminden, LK 2022',
                        'data_labels': {
                            'value': True,
                            'position': 'inside_end',
                            'font': {
                                'color': '#FFFFFF',
                                'name': 'Segoe UI'
                            }
                        },
                        'fill': {
                            'color': '#404040'
                        },
                        'overlap': -60
                    },
                    {
                        'values': '=ASSISTED_LIVING_ANALYSIS!$B$50',
                        'name': 'Holzminden, LK 2030',
                        'data_labels': {
                            'value': True,
                            'position': 'inside_end',
                            'font': {
                                'name': 'Segoe UI'
                            }
                        },
                        'fill': {
                            'color': '#BFB273'
                        }
                    }
                ],
                'styles': {
                    'x_axis': {
                        'visible': False
                    },
                    'y_axis': {
                        'visible': True,
                        'major_gridlines': {
                            'visible': True
                        }
                    },
                    'legend': {
                        'position': 'bottom',
                        'name_font': {
                            'name': 'Segoe UI'
                        },
                        'layout': {
                            'x': 0,
                            'y': .9,
                            'width': 1,
                            'height': .1
                        }
                    },
                    'plotarea': {
                        'layout': {
                            'x': .1,
                            'y': .2,
                            'width': .8,
                            'height': .6
                        }
                    },
                    'chartarea': {
                        'border': {
                            'none': True
                        }
                    },
                    'size': {
                        'width': 430,
                        'height': 250
                    },
                    'chart': {
                        'x_offset': 30
                    },
                    'title': {
                        'name': 'REGIONAL DEMAND FOR ASSISTED LIVING',
                        'name_font': {
                            'size': 12,
                            'name': 'Segoe UI Black'
                        }
                    }
                }
            }
        ]
    }
alca_data = {
        'title': 'ASS_LIVING_COMPETITOR_ANALYSIS',
        'print_area': 'A1:G1048576',
        'fit_to_pages': (1, 0),
        'columns_width': [5.27, 37.18, 34.27, 14, 16.91, 14.09, 10.55],
        'row_height': 40,
        'row_start': 28,
        'row_count': 7,
        'landscape': False,
        'data': [
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A1:E1',
                'content': 'ASSISTED LIVING COMPETITOR ANALYSIS',
                'format': {
                    'font_size': 24,
                    'font': 'Segoe UI Black',
                    'color': '#BFB273'
                }
            },
            {
                'type': 'image',
                'cell': 'F1',
                'file': 'img/cb_logo.png',
                'style': {
                    'x_scale': .21,
                    'y_scale': .09,
                    'y_offset': 10,
                    'x_offset': 50
                }
            },
            {
                'type': 'image',
                'cell': 'A4',
                'file': 'map_image_5a7990_nh.png',
                'style': {
                    'x_scale': .7,
                    'y_scale': .7
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A29',
                'content': 'No.',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B29',
                'content': 'Name',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C29',
                'content': 'Operator',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D29',
                'content': 'Type',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E29',
                'content': 'City',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'F29',
                'content': 'Status',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'G29',
                'content': 'No. of apts.',
                'format': {
                    'align': 'center',
                    'font': 'Segoe UI Black',
                    'bg_color': '#BFB273'
                }
            }
        ]
}
comp_data = {
        'title': 'Comparable List',
        'print_area': 'A1:P1048576',
        'fit_to_pages': (1, 0),
        'columns_width': [16, 23, 11, 13, 18, 11, 15, 15, 18, 16, 13, 13, 12, 20, 20, 13],
        'landscape': True,
        'data': [
            {
                'type': 'text',
                'insert': 'merge',
                'cell': 'A1:E1',
                'content': 'Comparable List Micro Living',
                'format': {
                    'font_size': 16,
                    'font': 'Segoe UI Semibold'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'A3',
                'content': 'Operator name',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'B3',
                'content': 'Address',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'C3',
                'content': 'Distance to Investment',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'D3',
                'content': 'A Company of 360 Operator Platform',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'E3',
                'content': 'Living Concept',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'F3',
                'content': 'No. of Apartments',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'G3',
                'content': 'Apartment size range (sqm)',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'H3',
                'content': 'All-in rent range (€/ sqm/ month)',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'I3',
                'content': 'Rent Range per month',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'J3',
                'content': 'Equipment',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'K3',
                'content': 'Community Spaces',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'L3',
                'content': 'Furnishing',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'M3',
                'content': 'Services',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'N3',
                'content': 'Note',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'O3',
                'content': 'Source',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
                'type': 'text',
                'insert': 'write',
                'cell': 'P3',
                'content': 'Data entry',
                'format': {
                    'font_size': 10,
                    'font': 'Segoe UI',
                    'color': '#FFFFFF',
                    'bold': True,
                    'bg_color': '#CCB666'
                }
            },
            {
              'type': 'image',
              'cell': 'O1',
              'file': 'img/cb_logo.png',
              'style': {
                    'x_scale': .29,
                    'y_scale': .21,
                    'x_offset': 60
              }
            }
        ]
}