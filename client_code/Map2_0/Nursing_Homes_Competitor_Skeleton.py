import anvil.server
nursing_homes_competitor_skeleton = {
  'page_number': 4,
  'line': {
    'top_line': {
      'x1': 17,
      'y1': 176,
      'x2': 203,
      'y2': 176
    },
    'bottom_line': {
      'x1': 10,
      'y1': 285,
      'x2': 203,
      'y2': 285
    }
  },
  'text': {
    'heading_city': {
      'color': [218, 218, 218],
      'font': 'segoeui',
      'size': 27,
      'x': 10,
      'y': 30,
      'txt': 'city'
    },
    'page_name': {
      'color': [0, 0, 0],
      'font': 'segoeui',
      'size': 27,
      'x': 10,
      'y': 40,
      'txt': 'Competitor Analysis'
    },
    'facility_type': {
      'color': [244, 81, 94],
      'font': 'seguisb',
      'size': 9,
      'x': 19,
      'y': 173,
      'txt': 'Nursing homes'
    }
  },
  'image': {
    'location_map': {
      'x': 10,
      'y': 45,
      'w': 150,
      'path': f"tmp/map_image.png"
    },
    'table_header': {
      'x': 70,
      'y': 142,
      'w': 130,
      'path': "img/nh_header.png"
    }
  },
  'cell': {},
  'multi_cell': {
    'legal_info_1': {
      'color': [128, 128, 128],
      'font': 'segoeui',
      'size': 7,
      'x': 10,
      'y': 285,
      'w': 190,
      'h': 4,
      'txt': '¹The Facility does / does not comply with the respective federal state regulation.',
      'align': 'left'
    },
    'legal_info_2': {
      'color': [128, 128, 128],
      'font': 'segoeui',
      'size': 7,
      'x': 10,
      'y': 288,
      'w': 190,
      'h': 4,
      'txt': 'For more info see page "Regulations"',
      'align': 'left'
    }
  }
}
