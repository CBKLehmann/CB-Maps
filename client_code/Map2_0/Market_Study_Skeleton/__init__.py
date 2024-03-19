from .. import Variables

def market_study_skeleton(market_study_data):
  return {
    'number_of_pages': 0,
    'settings': {
        'fonts': ['segoeui', 'seguisb', 'segoeuisl', 'calibri']
    },
    'pages': {
        'cover': {
                'rect': {
                    'blue_rect': {
                        'color': [32, 49, 68],
                        'x': 120,
                        'y': 0,
                        'w': 90,
                        'h': 297,
                        'style': 'F'
                    }
                },
                'text': {
                    'ms_heading': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 27,
                        'x': 10,
                        'y': 130,
                        'txt': 'Market Study'
                    },
                    'ms_care': {
                        'color': [200, 176, 88],
                        'font': 'seguisb',
                        'size': 80,
                        'x': 10,
                        'y': 155,
                        'txt': 'Care'
                    },
                    'street_heading': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 180,
                        'txt': 'Street, no.'
                    },
                    'zip_heading': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 186,
                        'txt': 'Zip code'
                    },
                    'city_heading': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 192,
                        'txt': 'City'
                    },
                    'district_heading': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 198,
                        'txt': 'District'
                    },
                    'federal_state_heading': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 204,
                        'txt': 'Federal State'
                    },
                    'country_heading': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 210,
                        'txt': 'Country'
                    },
                    'street_value': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 180,
                        'txt': market_study_data['street']
                    },
                    'zip_value': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 186,
                        'txt': market_study_data['zipcode']
                    },
                    'city_value': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 192,
                        'txt': market_study_data['city']
                    },
                    'district_value': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 198,
                        'txt': market_study_data['district']
                    },
                    'federal_state_value': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 204,
                        'txt': market_study_data['federal_state']
                    },
                    'country_value': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 210,
                        'txt': 'Germany'
                    },
                    'radius_of_analysis': {
                        'color': [200, 176, 88],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 216,
                        'txt': 'Radius of analysis'
                    },
                    'radius_of_analysis_value': {
                        'color': [200, 176, 88],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 55,
                        'y': 216,
                        'txt': f"{market_study_data['iso_time']} minutes of {market_study_data['iso_movement']}"
                    },
                    'ms_text_1': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 240,
                        'txt': 'The'
                    },
                    'ms_text_2': {
                        'color': [0, 0, 0],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 18,
                        'y': 240,
                        'txt': 'Market Study'
                    },
                    'ms_text_3': {
                        'color': [200, 176, 88],
                        'font': 'seguisb',
                        'size': 12,
                        'x': 45,
                        'y': 240,
                        'txt': 'Care'
                    },
                    'ms_text_4': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 55,
                        'y': 240,
                        'txt': 'is a web based service'
                    },
                    'ms_text_5': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 246,
                        'txt': 'by Capital Bay, which provides investors with access'
                    },
                    'ms_text_6': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 252,
                        'txt': 'to data on the current German care market including'
                    },
                    'ms_text_7': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 258,
                        'txt': 'demographical forecasts and competitor analysis.'
                    },
                    'ms_text_8': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 264,
                        'txt': 'This allows for targeted examination of the market,'
                    },
                    'ms_text_9': {
                        'color': [0, 0, 0],
                        'font': 'segoeui',
                        'size': 12,
                        'x': 10,
                        'y': 270,
                        'txt': 'using protractile radii.'
                    },
                    'version': {
                        'color': [166, 166, 166],
                        'font': 'segoeui',
                        'size': 9,
                        'x': 10,
                        'y': 290,
                        'txt': f"Version 2.1.0 - Generated on {market_study_data['created_date']}"
                    }
                },
                'image': {
                    'logo': {
                        'x': 147,
                        'y': 12,
                        'w': 36,
                        'path': "img/LogoTrans.png"
                    },
                    'map': {
                        'x': 135,
                        'y': 30,
                        'w': 60,
                        'path': f"tmp/summary_map_{Variables.unique_code}.png"
                    },
                    'population': {
                        'x': 161,
                        'y': 195,
                        'w': 8,
                        'path': "img/pop_trend.png"
                    },
                    'beds': {
                        'x': 158,
                        'y': 245,
                        'w': 14,
                        'path': "img/beds.png"
                    }
                },
                'cell': {
                    'keyfacts': {
                        'color': [200, 176, 88],
                        'font': 'seguisb',
                        'size': 14,
                        'x': 120,
                        'y': 150,
                        'w': 90,
                        'txt': 'LOCATION KEYFACTS',
                        'align': 'center'
                    },
                    'purchasing_power_value': {
                        'color': [255, 255, 255],
                        'font': 'segoeuisl',
                        'size': 36,
                        'x': 120,
                        'y': 180,
                        'w': 90,
                        'txt': '{:,}'.format(market_study_data['purchase_power']),
                        'align': 'center'
                    },
                    'population_value': {
                        'color': [255, 255, 255],
                        'font': 'segoeuisl',
                        'size': 36,
                        'x': 120,
                        'y': 230,
                        'w': 90,
                        'txt': '{:,}%'.format(float(market_study_data['population_trend'])) if float(market_study_data['population_trend']) < 0 else '+{:,}%'.format(float(market_study_data['population_trend'])),
                        'align': 'center'
                    },
                    'beds_value': {
                        'color': [255, 255, 255],
                        'font': 'segoeuisl',
                        'size': 36,
                        'x': 120,
                        'y': 280,
                        'w': 90,
                        'txt': '{:,}'.format(market_study_data['beds_surplus_35_v2']),
                        'align': 'center'
                    }
                },
                'multi_cell': {
                    'purchasing_power_heading': {
                        'color': [255, 255, 255],
                        'font': 'segoeui',
                        'size': 9,
                        'x': 120,
                        'y': 160,
                        'w': 90,
                        'h': 4,
                        'txt': 'Purchasing Power\nat the location - As of 2022',
                        'align': 'center'
                    },
                    'population_trend_heading': {
                        'color': [255, 255, 255],
                        'font': 'segoeui',
                        'size': 9,
                        'x': 120,
                        'y': 210,
                        'w': 90,
                        'h': 4,
                        'txt': 'Population trend of the 65+ age group\nat the location - 2035',
                        'align': 'center'
                    },
                    'beds_heading': {
                        'color': [255, 255, 255],
                        'font': 'segoeui',
                        'size': 9,
                        'x': 120,
                        'y': 260,
                        'w': 90,
                        'h': 4,
                        'txt': 'Surplus or deficit of beds\nat the location - 2035',
                        'align': 'center'
                    },
                }
            },
        'summary': {
            'page_number': 2,
            'rect': {
                'blue_rect_1': {
                    'color': [32, 49, 68],
                    'x': 76,
                    'y': 50.3,
                    'w': 24,
                    'h': 9.7,
                    'style': 'F'
                },
                'blue_rect_2': {
                    'color': [32, 49, 68],
                    'x': 76,
                    'y': 60.3,
                    'w': 24,
                    'h': 44.7,
                    'style': 'F'
                },
                'blue_rect_3': {
                    'color': [32, 49, 68],
                    'x': 76,
                    'y': 105.3,
                    'w': 24,
                    'h': 9.7,
                    'style': 'F'
                },
                'blue_rect_4': {
                    'color': [32, 49, 68],
                    'x': 76,
                    'y': 115.3,
                    'w': 24,
                    'h': 52.7,
                    'style': 'F'
                },
                'blue_rect_5': {
                    'color': [32, 49, 68],
                    'x': 76,
                    'y': 168.3,
                    'w': 24,
                    'h': 9.7,
                    'style': 'F'
                },
                'blue_rect_6': {
                    'color': [32, 49, 68],
                    'x': 76,
                    'y': 178.3,
                    'w': 24,
                    'h': 74.7,
                    'style': 'F'
                },
                'gray_rect_1': {
                    'color': [223, 223, 223],
                    'x': 101,
                    'y': 50.3,
                    'w': 49,
                    'h': 9.7,
                    'style': 'F'
                },
                'gray_rect_2': {
                    'color': [223, 223, 223],
                    'x': 101,
                    'y': 60.3,
                    'w': 49,
                    'h': 44.7,
                    'style': 'F'
                },
                'gray_rect_3': {
                    'color': [223, 223, 223],
                    'x': 101,
                    'y': 105.3,
                    'w': 49,
                    'h': 9.7,
                    'style': 'F'
                },
                'gray_rect_4': {
                    'color': [223, 223, 223],
                    'x': 101,
                    'y': 115.3,
                    'w': 49,
                    'h': 52.7,
                    'style': 'F'
                },
                'gray_rect_5': {
                    'color': [223, 223, 223],
                    'x': 101,
                    'y': 168.3,
                    'w': 49,
                    'h': 9.7,
                    'style': 'F'
                },
                'gray_rect_6': {
                    'color': [223, 223, 223],
                    'x': 101,
                    'y': 178.3,
                    'w': 49,
                    'h': 74.7,
                    'style': 'F'
                },
                'lightgray_rect_1': {
                    'color': [242, 242, 242],
                    'x': 151,
                    'y': 50.3,
                    'w': 49,
                    'h': 9.7,
                    'style': 'F'
                },
                'lightgray_rect_2': {
                    'color': [242, 242, 242],
                    'x': 151,
                    'y': 60.3,
                    'w': 49,
                    'h': 44.7,
                    'style': 'F'
                },
                'lightgray_rect_3': {
                    'color': [242, 242, 242],
                    'x': 151,
                    'y': 105.3,
                    'w': 49,
                    'h': 9.7,
                    'style': 'F'
                },
                'lightgray_rect_4': {
                    'color': [242, 242, 242],
                    'x': 151,
                    'y': 115.3,
                    'w': 49,
                    'h': 52.7,
                    'style': 'F'
                },
                'lightgray_rect_5': {
                    'color': [242, 242, 242],
                    'x': 151,
                    'y': 168.3,
                    'w': 49,
                    'h': 9.7,
                    'style': 'F'
                },
                'lightgray_rect_6': {
                    'color': [242, 242, 242],
                    'x': 151,
                    'y': 178.3,
                    'w': 49,
                    'h': 74.7,
                    'style': 'F'
                },
                'demographic_top_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 50,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'demographic_bottom_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 60,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'demographic_top_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 50,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demographic_bottom_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 60,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demographic_top_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 50,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demographic_bottom_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 60,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'inpatient_care_top_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 105,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'inpatient_care_bottom_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 115,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'inpatient_care_top_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 105,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'inpatient_care_bottom_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 115,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'inpatient_care_top_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 105,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'inpatient_care_bottom_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 115,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demand_supply_top_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 168,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'demand_supply_bottom_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 178,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'demand_supply_top_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 168,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demand_supply_bottom_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 178,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demand_supply_top_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 168,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'demand_supply_bottom_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 178,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'final_line_1': {
                    'color': [0, 0, 0],
                    'x': 10,
                    'y': 253,
                    'w': 65,
                    'h': .3,
                    'style': 'F'
                },
                'final_line_2': {
                    'color': [0, 0, 0],
                    'x': 101,
                    'y': 253,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                },
                'final_line_3': {
                    'color': [0, 0, 0],
                    'x': 151,
                    'y': 253,
                    'w': 49,
                    'h': .3,
                    'style': 'F'
                }
            },
            'text': {
                'heading_city': {
                    'color': [218, 218, 218],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 30,
                    'txt': market_study_data['city']
                },
                'page_name': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 40,
                    'txt': 'Current Situation'
                }
            },
            'cell': {
                'demographic_trend_analysis': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 12,
                    'y': 55,
                    'w': 20,
                    'txt': 'Demographic trend analysis',
                    'align': 'left'
                },
                'population_city_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 65,
                    'w': 20,
                    'txt': f"Population {market_study_data['city']} (City)",
                    'align': 'left'
                },
                'population_county_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 71,
                    'w': 20,
                    'txt': f"Population {market_study_data['countie']} (County)",
                    'align': 'left'
                },
                'population_county_in_percent_heading': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 12,
                    'y': 77,
                    'w': 20,
                    'txt': 'in %',
                    'align': 'left'
                },
                'population_aged_65_79_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 83,
                    'w': 20,
                    'txt': 'of which population aged 65-79 years',
                    'align': 'left'
                },
                'population_aged_65_79_in_percent_heading': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 15,
                    'y': 89,
                    'w': 20,
                    'txt': 'in %',
                    'align': 'left'
                },
                'population_aged_80_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 95,
                    'w': 20,
                    'txt': 'of which population aged 80+',
                    'align': 'left'
                },
                'population_aged_80_in_percent_heading': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 15,
                    'y': 101,
                    'w': 20,
                    'txt': 'in %',
                    'align': 'left'
                },
                'full_inpatient_care': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 12,
                    'y': 110,
                    'w': 20,
                    'txt': 'Full inpatient care',
                    'align': 'left'
                },
                'care_rate_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 133,
                    'w': 20,
                    'txt': 'Care rate of population',
                    'align': 'left'
                },
                'nursing_home_rate_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 139,
                    'w': 20,
                    'txt': 'There of nursing home rate',
                    'align': 'left'
                },
                'full_inpatient_care_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 145,
                    'w': 20,
                    'txt': 'Patients receiving full inpatient care',
                    'align': 'left'
                },
                'occupancy_rate_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 151,
                    'w': 20,
                    'txt': 'Occupancy rate',
                    'align': 'left'
                },
                'number_of_beds_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 157,
                    'w': 20,
                    'txt': 'Number of beds',
                    'align': 'left'
                },
                'number_of_free_beds_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 163,
                    'w': 20,
                    'txt': 'Number of free beds',
                    'align': 'left'
                },
                'demand_supply': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 12,
                    'y': 173,
                    'w': 20,
                    'txt': 'Demand & Supply',
                    'align': 'left'
                },
                'demand_supply_viewing_radius': {
                    'color': [200, 176, 88],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 183,
                    'w': 20,
                    'txt': f"Viewing radius: {market_study_data['iso_time']} minutes of {market_study_data['iso_movement']}",
                    'align': 'left'
                },
                'nursing_homes_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 189,
                    'w': 20,
                    'txt': 'Nursing homes',
                    'align': 'left'
                },
                'beds_supply_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 195,
                    'w': 20,
                    'txt': 'Beds in supply',
                    'align': 'left'
                },
                'demand_occupancy_rate_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 201,
                    'w': 20,
                    'txt': 'Occupancy rate',
                    'align': 'left'
                },
                'planned_nursing_homes_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 207,
                    'w': 20,
                    'txt': 'Nursing homes in planning',
                    'align': 'left'
                },
                'constructing_nursing_homes_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 213,
                    'w': 20,
                    'txt': 'Nursing homes under construction',
                    'align': 'left'
                },
                'beds_planning_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 219,
                    'w': 20,
                    'txt': 'Beds in planning',
                    'align': 'left'
                },
                'beds_constructing_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 225,
                    'w': 20,
                    'txt': 'Beds under construction',
                    'align': 'left'
                },
                'loss_of_beds_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 231,
                    'w': 20,
                    'txt': 'Beds lost while meeting federal state law',
                    'align': 'left'
                },
                'adjusted_beds_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 237,
                    'w': 20,
                    'txt': 'Adjusted number of beds',
                    'align': 'left'
                },
                'demand_inpatients_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 243,
                    'w': 20,
                    'txt': 'Demand of number of inpatients',
                    'align': 'left'
                },
                'surplus_deficit_heading': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 12,
                    'y': 249,
                    'w': 20,
                    'txt': 'Surplus or deficit of beds',
                    'align': 'left'
                },
                'scenario_1_text': {
                    'color': [128, 128, 128],
                    'font': 'segoeui',
                    'size': 7,
                    'x': 12,
                    'y': 275,
                    'w': 20,
                    'txt': '¹In scenario 1 the relative situation (product of nursing home rate and care rate) as in 2020 is assumed to be constant for the entire forecasting period.',
                    'align': 'left'
                },
                'scenario_2_text': {
                    'color': [128, 128, 128],
                    'font': 'segoeui',
                    'size': 7,
                    'x': 12,
                    'y': 281,
                    'w': 20,
                    'txt': '²In scenario 2, it is assumed that the proportion of the nursing home rate will increase by 0.003 percent-points from 2020 to 2035.',
                    'align': 'left'
                },
                '2020_heading': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 76,
                    'y': 55,
                    'w': 23,
                    'txt': '2020',
                    'align': 'right'
                },
                'population_city_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 65,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['population_city_2020']),
                    'align': 'right'
                },
                'population_county_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 71,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['population_county_2020']),
                    'align': 'right'
                },
                'population_county_in_percent_2020': {
                    'color': [255, 255, 255],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 76,
                    'y': 77,
                    'w': 23,
                    'txt': '100%',
                    'align': 'right'
                },
                'population_aged_65_79_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 83,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['people_u80']),
                    'align': 'right'
                },
                'population_aged_65_79_in_percent_2020': {
                    'color': [255, 255, 255],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 76,
                    'y': 89,
                    'w': 23,
                    'txt': '{:,}%'.format(round(market_study_data['people_u80'] * 100 / market_study_data['population_county_2020'])),
                    'align': 'right'
                },
                'population_aged_80_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 95,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['people_o80']),
                    'align': 'right'
                },
                'population_aged_80_in_percent_2020': {
                    'color': [255, 255, 255],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 76,
                    'y': 101,
                    'w': 23,
                    'txt': '{:,}%'.format(round(market_study_data['people_o80'] * 100 / market_study_data['population_county_2020'])),
                    'align': 'right'
                },
                'care_rate_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 133,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['new_care_rate_raw']),
                    'align': 'right'
                },
                'nursing_home_rate_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 139,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['nursing_home_rate']),
                    'align': 'right'
                },
                'full_inpatient_care_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 145,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['inpatients_lk']),
                    'align': 'right'
                },
                'occupancy_rate_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 151,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['occupancy_lk']),
                    'align': 'right'
                },
                'number_of_beds_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 157,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_lk']),
                    'align': 'right'
                },
                'number_of_free_beds_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 163,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['free_beds_lk']),
                    'align': 'right'
                },
                'nursing_homes_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 189,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['nursing_homes_active']),
                    'align': 'right'
                },
                'beds_supply_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 195,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_active']),
                    'align': 'right'
                },
                'demand_occupancy_rate_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 201,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['occupancy_lk']),
                    'align': 'right'
                },
                'planned_nursing_homes_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 207,
                    'w': 23,
                    'txt': '-' if market_study_data['nursing_homes_planned'] == 0 else '{:,}'.format(market_study_data['nursing_homes_planned']),
                    'align': 'right'
                },
                'constructing_nursing_homes_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 213,
                    'w': 23,
                    'txt': '-' if market_study_data['nursing_homes_construct'] == 0 else '{:,}'.format(market_study_data['nursing_homes_construct']),
                    'align': 'right'
                },
                'beds_planning_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 219,
                    'w': 23,
                    'txt': '-' if market_study_data['beds_planned'] == 0 else '{:,}'.format(market_study_data['beds_planned']),
                    'align': 'right'
                },
                'beds_constructing_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 225,
                    'w': 23,
                    'txt': '-' if market_study_data['beds_construct'] == 0 else '{:,}'.format(market_study_data['beds_construct']),
                    'align': 'right'
                },
                'adjusted_beds_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 237,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_active']),
                    'align': 'right'
                },
                'demand_inpatients_2020': {
                    'color': [255, 255, 255],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 76,
                    'y': 243,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['inpatients']),
                    'align': 'right'
                },
                '2030_heading': {
                    'color': [0, 0, 0],
                    'fill_color': [223, 223, 223],
                    'font': 'segoeui',
                    'size': 12,
                    'x': 101,
                    'y': 50,
                    'w': 48,
                    'h': 10,
                    'txt': '2030',
                    'align': 'right'
                },
                'population_county_2030': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 71,
                    'w': 48,
                    'txt': '{:,}'.format(market_study_data['population_fc_30']),
                    'align': 'right'
                },
                'population_county_in_percent_2030': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 77,
                    'w': 48,
                    'txt': '100%',
                    'align': 'right'
                },
                'population_aged_65_79_2030': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 83,
                    'w': 48,
                    'txt': '{:,}'.format(market_study_data['people_u80_fc']),
                    'align': 'right'
                },
                'population_aged_65_79_in_percent_2030': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 89,
                    'w': 48,
                    'txt': '{:,}%'.format(round((market_study_data['people_u80_fc'] * 100) / market_study_data['population_fc_30'])),
                    'align': 'right'
                },
                'population_aged_80_2030': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 95,
                    'w': 48,
                    'txt': '{:,}'.format(market_study_data['people_o80_fc']),
                    'align': 'right'
                },
                'population_aged_80_in_percent_2030': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 101,
                    'w': 48,
                    'txt': '{:,}%'.format(round((market_study_data['people_o80_fc'] * 100) / market_study_data['population_fc_30'])),
                    'align': 'right'
                },
                'scenario_1_2030': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 101,
                    'y': 120,
                    'w': 23,
                    'txt': 'Scenario 1',
                    'align': 'right'
                },
                'care_rate_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 133,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['care_rate_30_v1_raw']),
                    'align': 'right'
                },
                'nursing_home_rate_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 139,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['nursing_home_rate']),
                    'align': 'right'
                },
                'full_inpatient_care_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 145,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['pat_rec_full_care_fc_30_v1']),
                    'align': 'right'
                },
                'occupancy_rate_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 151,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'number_of_beds_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 157,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_30_v1']),
                    'align': 'right'
                },
                'number_of_free_beds_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 163,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['free_beds_30_v1']),
                    'align': 'right'
                },
                'beds_supply_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 195,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_active'] + market_study_data['beds_planned'] + market_study_data['beds_construct']),
                    'align': 'right'
                },
                'demand_occupancy_rate_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 201,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'loss_of_beds_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 231,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['loss_of_beds']),
                    'align': 'right'
                },
                'adjusted_beds_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 237,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_adjusted_30_v1']),
                    'align': 'right'
                },
                'demand_inpatients_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 243,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['inpatients_fc']),
                    'align': 'right'
                },
                'surplus_deficit_2030_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 101,
                    'y': 249,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_surplus']),
                    'align': 'right'
                },
                'scenario_2_2030': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 125,
                    'y': 120,
                    'w': 23,
                    'txt': 'Scenario 2',
                    'align': 'right'
                },
                'care_rate_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 133,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['care_rate_30_v2_raw']),
                    'align': 'right'
                },
                'nursing_home_rate_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 139,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['nursing_home_rate']),
                    'align': 'right'
                },
                'full_inpatient_care_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 145,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['pat_rec_full_care_fc_30_v2']),
                    'align': 'right'
                },
                'occupancy_rate_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 151,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'number_of_beds_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 157,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_30_v2']),
                    'align': 'right'
                },
                'number_of_free_beds_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 163,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['free_beds_30_v2']),
                    'align': 'right'
                },
                'beds_supply_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 195,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_active'] + market_study_data['beds_planned'] + market_study_data['beds_construct']),
                    'align': 'right'
                },
                'demand_occupancy_rate_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 201,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'loss_of_beds_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 231,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['loss_of_beds']),
                    'align': 'right'
                },
                'adjusted_beds_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 237,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_adjusted_30_v2']),
                    'align': 'right'
                },
                'demand_inpatients_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 243,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['inpatients_fc_v2']),
                    'align': 'right'
                },
                'surplus_deficit_2030_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 125,
                    'y': 249,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_surplus_v2']),
                    'align': 'right'
                },
                '2035_heading': {
                    'color': [0, 0, 0],
                    'fill_color': [242, 242, 242],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 151,
                    'y': 50,
                    'w': 48,
                    'h': 10,
                    'txt': '2035',
                    'align': 'right'
                },
                'population_county_2035': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 71,
                    'w': 48,
                    'txt': '{:,}'.format(market_study_data['population_fc_35']),
                    'align': 'right'
                },
                'population_county_in_percent_2035': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 77,
                    'w': 48,
                    'txt': '100%',
                    'align': 'right'
                },
                'population_aged_65_79_2035': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 83,
                    'w': 48,
                    'txt': '{:,}'.format(market_study_data['people_u80_fc_35']),
                    'align': 'right'
                },
                'population_aged_65_79_in_percent_2035': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 89,
                    'w': 48,
                    'txt': '{:,}%'.format(round(market_study_data['people_u80_fc_35'] * 100 / market_study_data['population_fc_35'])),
                    'align': 'right'
                },
                'population_aged_80_2035': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 95,
                    'w': 48,
                    'txt': '{:,}'.format(market_study_data['people_o80_fc_35']),
                    'align': 'right'
                },
                'population_aged_80_in_percent_2035': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 101,
                    'w': 48,
                    'txt': '{:,}%'.format(round(market_study_data['people_o80_fc_35'] * 100 / market_study_data['population_fc_35'])),
                    'align': 'right'
                },
                'scenario_1_2035': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 151,
                    'y': 120,
                    'w': 23,
                    'txt': 'Scenario 1',
                    'align': 'right'
                },
                'care_rate_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 133,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['care_rate_35_v1_raw']),
                    'align': 'right'
                },
                'nursing_home_rate_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 139,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['nursing_home_rate']),
                    'align': 'right'
                },
                'full_inpatient_care_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 145,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['pat_rec_full_care_fc_35_v1']),
                    'align': 'right'
                },
                'occupancy_rate_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 151,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'number_of_beds_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 157,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_35_v1']),
                    'align': 'right'
                },
                'number_of_free_beds_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 163,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['free_beds_35_v1']),
                    'align': 'right'
                },
                'beds_supply_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 195,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_active'] + market_study_data['beds_planned'] + market_study_data['beds_construct']),
                    'align': 'right'
                },
                'demand_occupancy_rate_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 201,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'loss_of_beds_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 231,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['loss_of_beds']),
                    'align': 'right'
                },
                'adjusted_beds_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 237,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_adjusted_35_v1']),
                    'align': 'right'
                },
                'demand_inpatients_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 243,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['inpatients_fc_35']),
                    'align': 'right'
                },
                'surplus_deficit_2035_s1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 151,
                    'y': 249,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_surplus_35']),
                    'align': 'right'
                },
                'scenario_2_2035': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 175,
                    'y': 120,
                    'w': 24,
                    'txt': 'Scenario 2',
                    'align': 'right'
                },
                'care_rate_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 133,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['care_rate_35_v2_raw']),
                    'align': 'right'
                },
                'nursing_home_rate_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 139,
                    'w': 23,
                    'txt': '{:,}%'.format(market_study_data['nursing_home_rate']),
                    'align': 'right'
                },
                'full_inpatient_care_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 145,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['pat_rec_full_care_fc_35_v2']),
                    'align': 'right'
                },
                'occupancy_rate_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 151,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'number_of_beds_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 157,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_35_v2']),
                    'align': 'right'
                },
                'number_of_free_beds_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 163,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['free_beds_35_v2']),
                    'align': 'right'
                },
                'beds_supply_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 195,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_active'] + market_study_data['beds_planned'] + market_study_data['beds_construct']),
                    'align': 'right'
                },
                'demand_occupancy_rate_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 201,
                    'w': 23,
                    'txt': '95.0%',
                    'align': 'right'
                },
                'loss_of_beds_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 231,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['loss_of_beds']),
                    'align': 'right'
                },
                'adjusted_beds_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 237,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_adjusted_35_v2']),
                    'align': 'right'
                },
                'demand_inpatients_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 243,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['inpatients_fc_35_v2']),
                    'align': 'right'
                },
                'surplus_deficit_2035_s2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 175,
                    'y': 249,
                    'w': 23,
                    'txt': '{:,}'.format(market_study_data['beds_surplus_35_v2']),
                    'align': 'right'
                }
            },
            'multi_cell': {
                'scenario_1_2030_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 7,
                    'x': 101,
                    'y': 122,
                    'w': 24,
                    'h': 4,
                    'txt': "Constant care\nsituation¹",
                    'align': 'right'
                },
                'scenario_2_2030_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 7,
                    'x': 125,
                    'y': 122,
                    'w': 24,
                    'h': 4,
                    'txt': "Increase in care needs of 0,003%²",
                    'align': 'right'
                },
                'scenario_1_2035_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 7,
                    'x': 151,
                    'y': 122,
                    'w': 24,
                    'h': 4,
                    'txt': "Constant care\nsituation¹",
                    'align': 'right'
                },
                'scenario_2_2035_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 7,
                    'x': 175,
                    'y': 122,
                    'w': 24,
                    'h': 4,
                    'txt': "Increase in care needs of 0,003%²",
                    'align': 'right'
                }
            },
        },
        'location_analysis': {
            'page_number': 3,
            'text': {
                'heading_city': {
                    'color': [218, 218, 218],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 30,
                    'txt': market_study_data['city']
                },
                'page_name': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 40,
                    'txt': 'Location Analysis'
                },
                'investment_object': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 30,
                    'y': 210,
                    'txt': 'Investment object'
                },
                'nursing_home_competitor': {
                    'color': [128, 128, 128],
                    'font': 'segoeuisl',
                    'size': 9,
                    'x': 30,
                    'y': 216,
                    'txt': 'Competitor'
                },
                'nursing_home': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 30,
                    'y': 220,
                    'txt': 'Nursing home'
                },
                'assisted_living_competitor': {
                    'color': [128, 128, 128],
                    'font': 'segoeuisl',
                    'size': 9,
                    'x': 30,
                    'y': 226,
                    'txt': 'Competitor'
                },
                'assisted_living': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 30,
                    'y': 230,
                    'txt': 'Assisted Living'
                },
                'nursing_home_assisted_living_competitor': {
                    'color': [128, 128, 128],
                    'font': 'segoeuisl',
                    'size': 9,
                    'x': 30,
                    'y': 236,
                    'txt': 'Competitor'
                },
                'nursing_home_assisted_living': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 30,
                    'y': 240,
                    'txt': 'Nursing home & Assisted living'
                },
                'distance_layer': {
                    'color': [128, 128, 128],
                    'font': 'segoeuisl',
                    'size': 9,
                    'x': 30,
                    'y': 246,
                    'txt': 'Distance layer'
                },
                'distance_amount': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 30,
                    'y': 250,
                    'txt': f"{market_study_data['iso_time']} minutes of {market_study_data['iso_movement']}"
                }
            },
            'image': {
                'location_map': {
                    'x': 10,
                    'y': 50,
                    'w': 200,
                    'path': f"tmp/map_image_{Variables.unique_code}.png"
                },
                'invest_marker': {
                    'x': 13.5,
                    'y': 204,
                    'w': 8,
                    'path': "img/home_pin.png"
                },
                'nursing_home_marker': {
                    'x': 14,
                    'y': 214,
                    'w': 7,
                    'path': "img/nh_pin.png"
                },
                'assisted_living_marker': {
                    'x': 14,
                    'y': 224,
                    'w': 7,
                    'path': "img/al_pin.png"
                },
                'nh_al_marker': {
                    'x': 15,
                    'y': 234,
                    'w': 7,
                    'path': "img/mixed_pin.png"
                },
                'distance_layer': {
                    'x': 15,
                    'y': 244,
                    'w': 7,
                    'path': "img/distance_layer.png"
                },
                'web_view': {
                    'x': 178,
                    'y': 55,
                    'w': 25,
                    'path': "img/web_view.png",
                    'link': market_study_data['share_url']
                }
            },
            'multi_cell': {
                'gpt_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 115,
                    'y': 205,
                    'w': 85,
                    'h': 4,
                    'txt': market_study_data['analysis_text'],
                    'align': 'left'
                }
            }
        },
        'good_to_know': {
            'page_number': 7,
            'line': {
                'operator_top_line': {
                    'x1': 10,
                    'y1': 65,
                    'x2': 100,
                    'y2': 65
                },
                'operator_bottom_line': {
                    'x1': 10,
                    'y1': 76,
                    'x2': 100,
                    'y2': 76
                },
                'prices_top_line': {
                    'x1': 110,
                    'y1': 65,
                    'x2': 203,
                    'y2': 65
                },
                'prices_bottom_line': {
                    'x1': 110,
                    'y1': 76,
                    'x2': 203,
                    'y2': 76
                },
                'purchase_power_top_line': {
                    'x1': 10,
                    'y1': 199,
                    'x2': 100,
                    'y2': 199
                },
                'purchase_power_bottom_line': {
                    'x1': 10,
                    'y1': 210,
                    'x2': 100,
                    'y2': 210
                }
            },
            'text': {
                'heading_city': {
                    'color': [218, 218, 218],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 30,
                    'txt': market_study_data['city']
                },
                'page_name': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 40,
                    'txt': 'Good to know'
                },
                'market_shares': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 17,
                    'x': 10,
                    'y': 55,
                    'txt': 'Market shares'
                },
                'operator': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 10,
                    'y': 72,
                    'txt': 'Operator'
                },
                'prices': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 110,
                    'y': 72,
                    'txt': 'Prices'
                },
                'purchase_power': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 10,
                    'y': 206,
                    'txt': 'Purchasing power index (municipality)'
                }
            },
            'image': {
                'operator_chart': {
                    'x': -5,
                    'y': 105,
                    'w': 120,
                    'path': "tmp/operator_chart.png"
                },
                'invest_scatter_chart': {
                    'x': 105,
                    'y': 85,
                    'w': 100,
                    'path': "tmp/invest_cost_scatter_chart.png"
                },
                'purchasing_power_chart': {
                    'x': 10,
                    'y': 190,
                    'w': 90,
                    'path': "tmp/purchasing_power_chart.png"
                }
            },
            'cell': {
                'operator_viewing_radius': {
                    'color': [200, 176, 88],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 80,
                    'w': 20,
                    'txt': f"Viewing radius: {market_study_data['iso_time']} minutes of {market_study_data['iso_movement']}",
                    'align': 'left'
                },
                'number_facilities_nh': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 85,
                    'w': 20,
                    'txt': 'Number of facilities (NH)',
                    'align': 'left'
                },
                'number_facilities_nh_value': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 80,
                    'y': 85,
                    'w': 20,
                    'txt': '{:,}'.format(market_study_data['number_facilities_nh_value']),
                    'align': 'right'
                },
                'number_facilities_al': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 90,
                    'w': 20,
                    'txt': 'Number of facilities (AL)',
                    'align': 'left'
                },
                'number_facilities_al_value': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 80,
                    'y': 90,
                    'w': 20,
                    'txt': '{:,}'.format(market_study_data['number_facilities_al_value']),
                    'align': 'right'
                },
                'median_beds': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 95,
                    'w': 20,
                    'txt': 'Median numbers of beds (NH)',
                    'align': 'left'
                },
                'median_beds_value': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 80,
                    'y': 95,
                    'w': 20,
                    'txt': '20',
                    'align': 'right'
                },
                'median_year_of_construct_nh': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 100,
                    'w': 20,
                    'txt': 'Median year of construction (NH)',
                    'align': 'left'
                },
                'median_year_of_construct_value': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 80,
                    'y': 100,
                    'w': 20,
                    'txt': '1997',
                    'align': 'right'
                },
                'median_year_of_construct_al': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 105,
                    'w': 20,
                    'txt': 'Median year of construction (AL)',
                    'align': 'left'
                },
                'median_year_of_construct_al_value': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 80,
                    'y': 105,
                    'w': 20,
                    'txt': '2010',
                    'align': 'right'
                },
                'operator_types': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 10,
                    'y': 115,
                    'w': 20,
                    'txt': 'Operator types',
                    'align': 'left'
                },
                'prices_viewing_radius': {
                    'color': [200, 176, 88],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 110,
                    'y': 80,
                    'w': 20,
                    'txt': f"Viewing radius: {market_study_data['iso_time']} minutes of {market_study_data['iso_movement']}",
                    'align': 'left'
                },
                'invest_cost_nursing_home': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 110,
                    'y': 85,
                    'w': 20,
                    'txt': 'Invest costs in Nursing homes',
                    'align': 'left'
                }
            },
            'multi_cell': {
                'invest_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 110,
                    'y': 270,
                    'w': 90,
                    'h': 4,
                    'txt': f"""The investment cost rates of the facilities within the catchment area range between €{market_study_data['minimum_invest_cost']} and €{market_study_data['maximum_invest_cost']}.  The median investment cost amount to €{'{:.2f}'.format(market_study_data['total_invest_cost'])}. {f"The investment costs at the facility, that is subject to this study amounts to €{market_study_data['home_invest']}." if not market_study_data['home_invest'] == -1 else ''}""",
                    'align': 'left'
                }
            }
        },
        'regulations': {
            'page_number': 8,
            'rect': {
                'grey_rect': {
                    'color': [242, 242, 242],
                    'x': 10,
                    'y': 50,
                    'w': 190,
                    'h': 110,
                    'style': 'F'
                }
            },
            'line': {
                'state_top_line': {
                    'x1': 15,
                    'y1': 84,
                    'x2': 195,
                    'y2': 84
                },
                'state_bottom_line': {
                    'x1': 15,
                    'y1': 95,
                    'x2': 195,
                    'y2': 95
                }
            },
            'text': {
                'heading_city': {
                    'color': [218, 218, 218],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 30,
                    'txt': market_study_data['city']
                },
                'page_name': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 40,
                    'txt': 'Regulations'
                }
            },
            'cell': {
                'regulations_heading': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 15,
                    'x': 15,
                    'y': 60,
                    'w': 20,
                    'txt': 'Regulations of federal state',
                    'align': 'left'
                },
                'federal_state': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 15,
                    'y': 90,
                    'w': 20,
                    'txt': 'Federal state',
                    'align': 'left'
                },
                'federal_state_value': {
                    'color': [255, 255, 255],
                    'fill_color': [32, 49, 68],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 85,
                    'y': 84,
                    'w': 110,
                    'h': 11,
                    'txt': market_study_data['regulations']['federal_state'],
                    'align': 'left',
                    'fill': True
                },
                'single_room_quota': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 110,
                    'w': 20,
                    'txt': 'Single room quota (min.)',
                    'align': 'left'
                },
                'home_size': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 116,
                    'w': 20,
                    'txt': 'Maximum home size',
                    'align': 'left'
                },
                'room_size': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 122,
                    'w': 20,
                    'txt': 'Minimum room size (SR/DR)',
                    'align': 'left'
                },
                'common_area': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 128,
                    'w': 20,
                    'txt': 'Minimum common area/residential',
                    'align': 'left'
                },
                'comment': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 134,
                    'w': 20,
                    'txt': 'Comment',
                    'align': 'left'
                },
                'legal_basis': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 9,
                    'x': 15,
                    'y': 153,
                    'w': 20,
                    'txt': 'Legal basis',
                    'align': 'left'
                },
                'new': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 85,
                    'y': 100,
                    'w': 20,
                    'txt': 'New',
                    'align': 'left'
                },
                'new_single_room_quota': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 85,
                    'y': 110,
                    'w': 20,
                    'txt': f"{int(market_study_data['regulations']['New']['sr_quote_raw'] * 100)}%" if not type(market_study_data['regulations']['New']['sr_quote_raw']) == str else market_study_data['regulations']['New']['sr_quote_raw'],
                    'align': 'left'
                },
                'new_home_size': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 85,
                    'y': 116,
                    'w': 20,
                    'txt': market_study_data['regulations']['New']['max_beds_raw'],
                    'align': 'left'
                },
                'new_room_size': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 85,
                    'y': 122,
                    'w': 20,
                    'txt': market_study_data['regulations']['New']['min_room_size'],
                    'align': 'left'
                },
                'new_common_area': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 85,
                    'y': 128,
                    'w': 20,
                    'txt': market_study_data['regulations']['New']['min_common_area_resident'],
                    'align': 'left'
                },
                'new_legal_basis': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 85,
                    'y': 153,
                    'w': 20,
                    'txt': market_study_data['regulations']['New']['legal_basis'],
                    'align': 'left'
                },
                'existing': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 140,
                    'y': 100,
                    'w': 20,
                    'txt': 'Existing',
                    'align': 'left'
                },
                'existing_single_room_quota': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 140,
                    'y': 110,
                    'w': 20,
                    'txt': f"{int(market_study_data['regulations']['Existing']['sr_quote_raw'] * 100)}%" if not type(market_study_data['regulations']['Existing']['sr_quote_raw']) == str else market_study_data['regulations']['Existing']['sr_quote_raw'],
                    'align': 'left'
                },
                'existing_home_size': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 140,
                    'y': 116,
                    'w': 20,
                    'txt': market_study_data['regulations']['Existing']['max_beds_raw'],
                    'align': 'left'
                },
                'existing_room_size': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 140,
                    'y': 122,
                    'w': 20,
                    'txt': market_study_data['regulations']['Existing']['min_room_size'],
                    'align': 'left'
                },
                'existing_common_area': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 140,
                    'y': 128,
                    'w': 20,
                    'txt': market_study_data['regulations']['Existing']['min_common_area_resident'],
                    'align': 'left'
                },
                'existing_legal_basis': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 140,
                    'y': 153,
                    'w': 20,
                    'txt': market_study_data['regulations']['Existing']['legal_basis'],
                    'align': 'left'
                }
            },
            'multi_cell': {
                'regulations_text': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 8,
                    'x': 15,
                    'y': 70,
                    'w': 180,
                    'h': 4,
                    'txt': f"This market study consideres {market_study_data['nursing_homes_active']} nursing homes within the vicinity of {market_study_data['iso_time']} minutes {market_study_data['iso_movement']}. Thereof, {market_study_data['complied_regulations']} facilities comply with the federal state regulations and {market_study_data['uncomplied_regulations']} facilities that do not fullfill the federal requirements. Assuming that only 80% of the respective facilities need to comply with the below shown federal state regulations, the resulting loss of beds in the market until 2030 will amount to {market_study_data['loss_of_beds']}.",
                    'align': 'left'
                },
                'new_comment': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 85,
                    'y': 134,
                    'w': 55,
                    'h': 4,
                    'txt': market_study_data['regulations']['New']['comment'],
                    'align': 'left'
                },
                'existing_comment': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 140,
                    'y': 134,
                    'w': 55,
                    'h': 4,
                    'txt': market_study_data['regulations']['Existing']['comment'],
                    'align': 'left'
                }
            }
        },
        'methodic': {
            'page_number': 9,
            'rect': {
                'grey_rect': {
                    'color': [242, 242, 242],
                    'x': 10,
                    'y': 50,
                    'w': 205,
                    'h': 227,
                    'style': 'F'
                }
            },
            'text': {
                'about_the_study': {
                    'color': [218, 218, 218],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 30,
                    'txt': 'About the study'
                },
                'methodic': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 40,
                    'txt': 'Methodic'
                }
            },
            'multi_cell': {
                'heading_1': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 15,
                    'y': 65,
                    'w': 80,
                    'h': 4,
                    'txt': 'Methodology, Data analysis &\nforecasting',
                    'align': 'left'
                },
                'paragraph_1': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 15,
                    'y': 80,
                    'w': 80,
                    'h': 4,
                    'txt': 'The market study highlights the current state of the\ninpatient care market in Germany and provides a\nforecast for the demand for nursing care until 2030\nand 2035. The study emphasizes the key drivers of\ndemand and the methodology employed to arrive at\nthe forecasted figures\n\nThe study utilizes a combination of publicly available\nsecondary research. Secondary research includes\nanalyzing geographical, demographical and\nstatistical databases as well as government\npublications and reputable healthcare sources to\ngather quantitative data.\n\nThe collected data is analyzed to identify trends,\ngrowth drivers, and market dynamics. The analysis\nencompasses factors such as population\ndemographics, healthcare policies and available\nmarket information on existing and future care\nfacilities, prevalence of chronic diseases, and\neconomic indicators affecting the demand for\ninpatient care.\n\nTo forecast the future demand for nursing care, a\ncombination of demographic projection, trend\nanalysis and consideration of new care facilities to\nbe launched on the market is employed.\nDemographic projection takes into account\npopulation growth, aging trends, and migration\npatterns. Trend analysis examines historical data and\nidentifies patterns and growth rates to project future\ndemand. New care facilities takes into account\nbuildings that are in planning or under construction.\n\nAll findings of the market study will consider the\nfactors mentioned above to provide a\ncomprehensive understanding of the current state of\nthe inpatient care market.',
                    'align': 'left'
                },
                'heading_2': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 15,
                    'y': 240,
                    'w': 70,
                    'h': 4,
                    'txt': 'Limitations',
                    'align': 'left'
                },
                'paragraph_2': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 15,
                    'y': 250,
                    'w': 80,
                    'h': 4,
                    'txt': 'The forecast is based on available data and assumes\nthat there will be no major disruptive events or\npolicy changes that could significantly impact the\ndemand for inpatient care.',
                    'align': 'left'
                },
                'heading_3': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 120,
                    'y': 68,
                    'w': 80,
                    'h': 4,
                    'txt': 'Data sources',
                    'align': 'left'
                },
                'paragraph_3': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 120,
                    'y': 80,
                    'w': 80,
                    'h': 4,
                    'txt': 'Statistisches Bundesamt\nStatista\nPflegemarkt.com\nPflegemarktdatenbank (updates every 3 months)\nDemografieportal\nPflegeheim-Atlas Deutschland 2021, Wuest Partner\n21st Real Estate\nChatGPT\nOpen Street Maps\nMalbox',
                    'align': 'left'
                }
            }
        },
        'contact': {
            'page_number': 10,
            'rect': {
                'grey_rect': {
                    'color': [242, 242, 242],
                    'x': 10,
                    'y': 50,
                    'w': 205,
                    'h': 60,
                    'style': 'F'
                }
            },
            'text': {
                'keep_in_touch': {
                    'color': [218, 218, 218],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 30,
                    'txt': 'Keep in touch'
                },
                'capital_bay_team': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 27,
                    'x': 10,
                    'y': 40,
                    'txt': 'Capital Bay Team'
                },
                'left_person_name': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 25,
                    'y': 65,
                    'txt': 'Stephanie Kühn'
                },
                'left_person_position': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 25,
                    'y': 70,
                    'txt': 'Head of Transaction Management'
                },
                'left_person_company': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 25,
                    'y': 75,
                    'txt': 'CB Transaction Management GmbH'
                },
                'left_person_address': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 25,
                    'y': 80,
                    'txt': 'Sachsendamm 4/5, 10829 Berlin'
                },
                'left_person_phone': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 25,
                    'y': 85,
                    'txt': 'T + 49 30 120866215'
                },
                'right_person_name': {
                    'color': [0, 0, 0],
                    'font': 'seguisb',
                    'size': 12,
                    'x': 100,
                    'y': 65,
                    'txt': 'Daniel Ziv'
                },
                'right_person_position': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 100,
                    'y': 70,
                    'txt': 'Junior Transaction Manager'
                },
                'right_person_company': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 100,
                    'y': 75,
                    'txt': 'CB Transaction Management GmbH'
                },
                'right_person_address': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 100,
                    'y': 80,
                    'txt': 'Sachsendamm 4/5, 10829 Berlin'
                },
                'right_person_phone': {
                    'color': [0, 0, 0],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 100,
                    'y': 85,
                    'txt': 'T + 49 30 120866281'
                }
            },
            'image': {
                'contact': {
                    'x': 25,
                    'y': 100,
                    'w': 178,
                    'path': "img/contact.jpg"
                }
            },
            'cell': {
                'left_person_mail': {
                    'color': [0, 176, 240],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 25,
                    'y': 90,
                    'w': 20,
                    'txt': 'stephanie.kuehn@capitalbay.de',
                    'align': 'left',
                    'link': 'mailto:stephanie.kuehn@capitalbay.de'
                },
                'right_person_mail': {
                    'color': [0, 176, 240],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 100,
                    'y': 90,
                    'w': 20,
                    'txt': 'daniel.ziv@capitalbay.de',
                    'align': 'left',
                    'link': 'mailto:daniel.ziv@capitalbay.de'
                }
            },
            'multi_cell': {
                'bottom_text_left': {
                    'color': [191, 191, 191],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 25,
                    'y': 230,
                    'w': 90,
                    'h': 4,
                    'txt': "This study has been prepared by Capital Bay Group\nS.A. (hereinafter Capital Bay) to provide investors and\nbusiness partners of Capital Bay with an overview of\ncurrent developments in the care and assisted living\nsector of the real estate industry. Capital Bay\nemphasizes that this study is not a sufficient basis for\ndecision making and user discretion is necessary for\nthe decision making process.\n\nThis study has been prepared with reasonable care.\nThe information presented has not been verified by\nCapital Bay for completeness or accuracy.\nIt has beenobtained from the sources indicated and\nsupplemented by Capital Bay's own market\nknowledge. No confidential or non-public information\nhas been made use.",
                    'align': 'left'
                },
                'bottom_text_right': {
                    'color': [191, 191, 191],
                    'font': 'segoeui',
                    'size': 9,
                    'x': 110,
                    'y': 230,
                    'w': 90,
                    'h': 4,
                    'txt': "Capital Bay is not responsible for any incomplete or\ninaccurate information and readers are urged to verify\nthe information themselves before making any\ndecision. Capital Bay shall not be liable for any\nomissions or inaccuracies in this report or for any\nother oral or written statements made in connection\nwith this report.\n\n© 2023 Capital Bay Group\nAll rights reserved.",
                    'align': 'left'
                }
            }
        }
    }
  }