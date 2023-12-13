import anvil.users
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

market_study_data = {
        'base_worksheet_settings': {
            'paper': 9,
            'hide_grid': 2,
            'fit_to_pages': (1, 1),
            'margins': (0, 0, 0, 0)
        },
        'workbook_format': {
            'font_size': 11,
            'font_name': "Segoe UI"
        },
        'cell_formats': {
            'normal_format': {
                'font': "Segoe UI",
                'font_size': 12
            },
            'normal_format_bold': {
                'font': "Segoe UI Semibold",
                'font_size': 12
            },
            'gold_format': {
                'font': "Segoe UI",
                'font_size': 12,
                'color': '#C8B058'
            },
            'gold_format_bold': {
                'font': "Segoe UI Semibold",
                'font_size': 12,
                'color': '#C8B058'
            },
            'place_heading_format': {
                'font': "Segoe UI",
                'font_size': 27,
                'color': '#DADADA'
            },
            'situation_heading_format': {
                'font': "Segoe UI",
                'font_size': 27
            },
            'chapter_heading_format': {
                'font': "Segoe UI Semibold",
                'font_size': 12,
                'top': 1,
                'bottom': 1,
                'valign': 'vcenter',
                'indent': 1
            },
            'chapter_topics_wrap_format': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'text_wrap': True,
                'indent': 1
            },
            'chapter_last_topic_format': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bottom': 1,
                'indent': 1
            },
            'viewing_radius_format': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'color': '#C8B058',
                'indent': 1
            },
            'percentage_topic_format': {
                'font': "Segoe UI Semilight",
                'font_size': 9,
                'italic': True,
                'indent': 1
            },
            'side_note_format': {
                'font': "Segoe UI Semilight",
                'font_size': 8,
                'italic': True,
                'color': '#808080',
                'indent': 1
            },
            'chapter_topics_format': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'indent': 1
            },
            'blue_column_year_format': {
                'font': "Segoe UI Semibold",
                'font_size': 12,
                'bg_color': '#203144',
                'top': 1,
                'bottom': 1,
                'border_color': '#FFFFFF',
                'right': 1,
                'right_color': '#FFFFFF',
                'color': '#FFFFFF',
                'valign': 'vcenter',
                'indent': 1,
                'align': 'right'
            },
            'blue_data_normal': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bg_color': '#203144',
                'color': '#FFFFFF',
                'right': 1,
                'right_color': '#FFFFFF',
                'indent': 1,
                'align': 'right'
            },
            'blue_data_number': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bg_color': '#203144',
                'color': '#FFFFFF',
                'right': 1,
                'right_color': '#FFFFFF',
                'indent': 1,
                'align': 'right',
                'num_format': '#,##0'
            },
            'blue_data_normal_right': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bg_color': '#203144',
                'color': '#FFFFFF',
                'align': 'right',
                'valign': 'vcenter',
                'right': 1,
                'right_color': '#FFFFFF',
                'indent': 1
            },
            'blue_data_normal_percentage': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bg_color': '#203144',
                'color': '#FFFFFF',
                'num_format': '0.0%',
                'right': 1,
                'right_color': '#FFFFFF',
                'indent': 1,
                'align': 'right'
            },
            'blue_data_normal_italic': {
                'font': "Segoe UI Semilight",
                'font_size': 9,
                'bg_color': '#203144',
                'color': '#FFFFFF',
                'italic': True,
                'num_format': '0%',
                'right': 1,
                'right_color': '#FFFFFF',
                'indent': 1,
                'align': 'right'
            },
            'grey_scenario_format': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'indent': 1,
                'bg_color': '#DFDFDF',
                'align': 'right'
            },
            'grey_column_year_format': {
                'font': "Segoe UI Semibold",
                'font_size': 12,
                'bg_color': '#DFDFDF',
                'top': 1,
                'bottom': 1,
                'valign': 'vcenter',
                'indent': 1,
                'align': 'right'
            },
            'grey_data_normal': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'indent': 1,
                'align': 'right'
            },
            'grey_data_normal_right': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'align': 'right',
                'valign': 'vcenter',
                'indent': 1
            },
            'grey_data_normal_right_number': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'align': 'right',
                'valign': 'vcenter',
                'indent': 1,
                'num_format': '#,##0'
            },
            'grey_data_normal_right_semibold': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'align': 'right',
                'valign': 'vcenter',
                'indent': 1,
                'bottom': 1,
                'num_format': '#,##0'
            },
            'grey_data_normal_percentage': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'num_format': '0.0%',
                'indent': 1,
                'align': 'right'
            },
            'grey_data_normal_italic': {
                'font': "Segoe UI Semilight",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'italic': True,
                'num_format': '0%',
                'indent': 1,
                'align': 'right'
            },
            'grey_text_italic': {
                'font': "Segoe UI Semilight",
                'font_size': 9,
                'bg_color': '#DFDFDF',
                'italic': True,
                'indent': 1,
                'align': 'right',
                'text_wrap': True,
                'valign': 'top'
            },
            'lightgrey_scenario_format': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'indent': 1,
                'align': 'right',
                'bg_color': '#F2F2F2'
            },
            'lightgrey_column_year_format': {
                'font': "Segoe UI Semibold",
                'font_size': 12,
                'bg_color': '#F2F2F2',
                'top': 1,
                'bottom': 1,
                'valign': 'vcenter',
                'indent': 1,
                'align': 'right'
            },
            'lightgrey_data_normal': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'indent': 1,
                'align': 'right'
            },
            'lightgrey_data_normal_right': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'align': 'right',
                'valign': 'vcenter',
                'indent': 1
            },
            'lightgrey_data_normal_right_number': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'align': 'right',
                'valign': 'vcenter',
                'indent': 1,
                'num_format': '#,##0'
            },
            'lightgrey_data_normal_percentage': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'num_format': '0.0%',
                'indent': 1,
                'align': 'right'
            },
            'lightgrey_data_normal_italic': {
                'font': "Segoe UI Semilight",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'italic': True,
                'num_format': '0%',
                'indent': 1,
                'align': 'right'
            },
            'lightgrey_text_italic': {
                'font': "Segoe UI Semilight",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'italic': True,
                'indent': 1,
                'align': 'right',
                'text_wrap': True,
                'valign': 'top'
            },
            'lightgrey_data_normal_right_semibold': {
                'font': "Segoe UI Semibold",
                'font_size': 9,
                'bg_color': '#F2F2F2',
                'align': 'right',
                'valign': 'vcenter',
                'indent': 1,
                'bottom': 1,
                'num_format': '#,##0'
            },
            'cover_fill_format': {
                'bg_color': "#203144"
            },
            'competitor_text': {
                'font': 'Segoe UI',
                'font_size': 9,
                'color': '#808080',
                'indent': 2,
                'valign': 'vcenter'
            },
            'icon_text': {
                'font': 'Segoe UI Semibold',
                'font_size': 12,
                'indent': 2
            },
            'gpt_text': {
                'font': 'Segoe UI',
                'font_size': 9,
                'text_wrap': True
            },
            'underline': {
                'bottom': 1
            },
            'rotated_text': {
                'font': 'Segoe UI',
                'font_size': 9,
                'rotation': 65,
                'align': 'center'
            },
            'nh_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'color': '#F4515E'
            },
            'al_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'color': '#F99398'
            },
            'operator_heading': {
                'font': 'Segoe UI',
                'font_size': 9
            },
            'home_icon': {
                'font_size': 14,
                'color': '#CCB666',
                'bg_color': '#1B2939',
                'align': 'center',
                'valign': 'vcenter',
                'bold': True,
                'bottom': 1,
                'bottom_color': '#FFFFFF'
            },
            'home_line_normal': {
                'font': 'Segoe UI',
                'font_size': 8,
                'bg_color': '#F4EFDC',
                'valign': 'vcenter'
            },
            'home_line_centered': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#F4EFDC',
                'text_wrap': True
            },
            'home_line_centered_link': {
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'color': '#00B0F0',
                'bg_color': '#F4EFDC',
                'underline': 1,
                'bold': True
            },
            'home_line_centered_percentage': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.0%',
                'bg_color': '#F4EFDC'
            },
            'home_line_centered_number': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#F4EFDC',
                'num_format': '0.0',
                'text_wrap': True
            },
            'home_line_centered_number_double': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'bg_color': '#F4EFDC',
                'num_format': '0.#0',
                'text_wrap': True
            },
            'row_number': {
                'font': 'Segoe UI',
                'font_size': 11,
                'bold': True,
                'bg_color': '#F4515E',
                'color': '#FFFFFF',
                'align': 'center',
                'valign': 'vcenter',
                'bottom': 1,
                'bottom_color': '#FFFFFF'
            },
            'row_normal': {
                'font': 'Segoe UI',
                'font_size': 8,
                'valign': 'vcenter'
            },
            'last_row_normal': {
                'font': 'Segoe UI',
                'font_size': 8,
                'valign': 'vcenter',
                'bottom': 1
            },
            'row_centered': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            },
            'row_centered_number': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.0',
                'text_wrap': True
            },
            'last_row_centered_number': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.0',
                'text_wrap': True,
                'bottom': 1
            },
            'row_centered_number_double': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.#0',
                'text_wrap': True
            },
            'last_row_centered_number_double': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.#0',
                'text_wrap': True,
                'bottom': 1
            },
            'last_row_centered': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'bottom': 1
            },
            'row_centered_link': {
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'color': '#00B0F0',
                'underline': 1
            },
            'last_row_centered_link': {
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'color': '#00B0F0',
                'underline': 1,
                'bottom': 1
            },
            'row_centered_percentage': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.0%'
            },
            'last_row_centered_percentage': {
                'font': 'Segoe UI',
                'font_size': 8,
                'align': 'center',
                'valign': 'vcenter',
                'num_format': '0.0%',
                'bottom': 1
            },
            'overall_sum': {
                'font': 'Segoe UI Semibold',
                'font_size': 8,
                'valign': 'vcenter',
                'align': 'center',
                'num_format': '"∑" #'
            },
            'overall_median_percentage': {
                'font': 'Segoe UI Semibold',
                'font_size': 8,
                'valign': 'vcenter',
                'align': 'center',
                'num_format': '"x̃" 0.0% '
            },
            'overall_median': {
                'font': 'Segoe UI Semibold',
                'font_size': 8,
                'valign': 'vcenter',
                'align': 'center',
                'num_format': '"x̃" 0.0'
            },
            'row_number_al': {
                'font': 'Segoe UI',
                'font_size': 11,
                'bold': True,
                'bg_color': '#F99398',
                'color': '#FFFFFF',
                'align': 'center',
                'valign': 'vcenter',
                'bottom': 1,
                'bottom_color': '#FFFFFF'
            },
            'foot_text': {
                'font': 'Segoe UI',
                'font_size': 8,
                'color': '#808080'
            },
            'page_display': {
                'font': 'Segoe UI',
                'size': 9,
                'align': 'right',
                'valign': 'vcenter',
                'bold': True
            },
            'small_heading': {
                'font': 'Segoe UI',
                'font_size': 17,
                'valign': 'vcenter'
            },
            'small_heading_background': {
                'font': 'Segoe UI',
                'font_size': 17,
                'valign': 'vcenter',
                'bg_color': '#F2F2F2'
            },
            'smaller_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 12,
                'top': 1,
                'bottom': 1,
                'valign': 'vcenter'
            },
            'smaller_heading_borderless_center': {
                'font': 'Segoe UI Semibold',
                'font_size': 12,
                'valign': 'vcenter',
                'align': 'center'
            },
            'smaller_heading_background': {
                'font': 'Segoe UI Semibold',
                'font_size': 12,
                'top': 1,
                'bottom': 1,
                'valign': 'vcenter',
                'bg_color': '#F2F2F2'
            },
            'gold_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'color': '#C8B058',
                'italic': True,
                'valign': 'vcenter'
            },
            'normal_text': {
                'font': 'Segoe UI',
                'font_size': 9,
                'valign': 'vcenter'
            },
            'normal_text_right': {
                'font': 'Segoe UI',
                'font_size': 9,
                'valign': 'vcenter',
                'align': 'right'
            },
            'mass_text': {
                'font': 'Segoe UI',
                'font_size': 9,
                'valign': 'vcenter',
                'text_wrap': True
            },
            'mass_text_background': {
                'font': 'Segoe UI',
                'font_size': 9,
                'valign': 'vcenter',
                'text_wrap': True,
                'bg_color': '#F2F2F2'
            },
            'blue_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 12,
                'bg_color': '#203144',
                'color': '#FFFFFF',
                'top': 1,
                'bottom': 1,
                'valign': 'vcenter'
            },
            'table_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 12,
                'valign': 'vcenter',
                'bg_color': '#F2F2F2'
            },
            'table_row_heading': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'valign': 'vcenter',
                'bg_color': '#F2F2F2'
            },
            'table_normal_text': {
                'font': 'Segoe UI',
                'font_size': 9,
                'valign': 'vcenter',
                'bg_color': '#F2F2F2',
                'text_wrap': True
            },
            'background': {
                'bg_color': '#F2F2F2'
            },
            'name_format': {
                'font': "Segoe UI",
                'font_size': 12,
                'bg_color': "#F2F2F2",
                'bold': True
            },
            'small_normal_format': {
                'font': "Segoe UI",
                'font_size': 9,
                'bg_color': "#F2F2F2"
            },
            'link_format': {
                'font': "Segoe UI",
                'font_size': 11,
                'color': "#00B0F0",
                'bg_color': "#F2F2F2"
            },
            'web_view_link_format': {
                'font': "Segoe UI",
                'font_size': 8,
                'color': "#00B0F0",
                'valign': "top"
            },
            'web_view_text': {
              'valign': 'bottom',
              'align': 'left',
              'font': "Segoe UI"
            }
        },
        'pages': {
            'COVER': {
                'settings': {
                    'area': "A1:AN51",
                    'column_width': [
                        1.88, 1.88, 1.88, 0.54, 0.38, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88,
                        1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88,
                        1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 1.88, 2.88
                    ],
                    'row_height': [
                        16.50, 14.25, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50,
                        16.50, 15.00, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50,
                        16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50,
                        16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50
                    ],
                    'columns_to_fill': [
                        'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN'
                    ],
                    'rows_to_fill': (1, 52),
                    'fill_format': {
                        'base': "cover_fill_format"
                    }
                },
                'cell_content': {
                    'images': {
                        'AB7': {
                            'file': "img/Map.png",
                            'settings': {
                                'x_scale': .32,
                                'y_scale': .35,
                                'y_offset': 20
                            }
                        },
                        'AC4': {
                            'file': "img/LogoTrans.png",
                            'settings': {
                              'x_offset': 10
                            }
                        },
                        'AF34': {
                            'file': "img/pop_trend.png",
                            'settings': {
                                'x_offset': 15,
                                'y_offset': 15
                            }
                        },
                        'AF43': {
                            'file': "img/beds.png",
                            'settings': {
                                'x_offset': 4,
                                'y_offset': 15
                            }
                        }
                    },
                    'textboxes': {
                        'C20': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI Semibold",
                                    'size': 27
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 250,
                                'height': 100,
                                'x_offset': -5
                            }
                        },
                        'C21': {
                            'text': "Care",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semibold',
                                    'size': 80,
                                    'color': '#C8B058'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 300,
                                'height': 150,
                                'x_offset': -10
                            }
                        },
                        'C41_A': {
                            'text': "The",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI',
                                    'size': 12
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': -5
                            }
                        },
                        'C41_B': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semibold',
                                    'size': 12
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 18
                            }
                        },
                        'C41_C': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semibold',
                                    'size': 12,
                                    'color': '#C8B058'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 106
                            }
                        },
                        'C41_D': {
                            'text': "is a web based service",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI',
                                    'size': 12
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 145,
                                'width': 174
                            }
                        },
                        'C42': {
                            'text': "by Capital Bay, which provides investors with access to data on the current German care market including demographical forecasts and competitor analysis. This allows for targeted examination of the market, using protractile radii.",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI',
                                    'size': 12
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': -5,
                                'width': 340
                            }
                        },
                        'Y26': {
                            'text': "LOCATION KEYFACTS",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semibold',
                                    'size': 14,
                                    'color': '#C8B058'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300
                            }
                        },
                        'Y28': {
                            'text': "Purchasing Power\nat the location - As of 2022",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI',
                                    'size': 9,
                                    'color': '#FFFFFF'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300
                            }
                        },
                        'Y29': {
                            'text': "102.80",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI Semilight",
                                    'size': 36,
                                    'color': '#FFFFFF'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300,
                                'y_offset': 8
                            }
                        },
                        'Y37': {
                            'text': "Population trend of the 65+ age group\nat the location - 2035",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI',
                                    'size': 9,
                                    'color': '#FFFFFF'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300
                            }
                        },
                        'Y38': {
                            'text': "+ 6.5%",
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semilight',
                                    'size': 36,
                                    'color': '#FFFFFF'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300,
                                'y_offset': 8
                            }
                        },
                        'Y46': {
                            'text': "Surplus or deficit of beds\nat the location - 2035",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': '#FFFFFF'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300
                            }
                        },
                        'Y47': {
                            'text': "1058",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI Semilight",
                                    'size': 36,
                                    'color': '#FFFFFF'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'horizontal': 'center',
                                    'text': 'center'
                                },
                                'width': 300,
                                'y_offset': 8
                            }
                        },
                        'C51': {
                            'text': "Version 1.8.3 Generated on 14.07.2023 07:45",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': '#A6A6A6'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 400,
                                'x_offset': -5
                            }
                        },
                    },
                    'cells': {
                        'C30': {
                            'text': "Street, no.",
                            'format': "normal_format"
                        },
                        'C31': {
                            'text': "Zip code",
                            'format': "normal_format"
                        },
                        'C32': {
                            'text': "City",
                            'format': "normal_format"
                        },
                        'C33': {
                            'text': "District",
                            'format': "normal_format"
                        },
                        'C34': {
                            'text': "Federal state",
                            'format': "normal_format"
                        },
                        'C35': {
                            'text': "Land",
                            'format': "normal_format"
                        },
                        'C36': {
                            'text': "Radius of analysis",
                            'format': "gold_format"
                        },
                        'L30': {
                            'text': "Musterstraße 15",
                            'format': "normal_format_bold"
                        },
                        'L31': {
                            'text': "63333",
                            'format': "normal_format_bold"
                        },
                        'L32': {
                            'text': "Bad Soden-Saalmünster",
                            'format': "normal_format_bold"
                        },
                        'L33': {
                            'text': "Mainz-Kinzig-Kreis",
                            'format': "normal_format_bold"
                        },
                        'L34': {
                            'text': "Hesse",
                            'format': "normal_format_bold"
                        },
                        'L35': {
                            'text': "Germany",
                            'format': "normal_format_bold"
                        },
                        'L36': {
                            'text': "15 min of walking",
                            'format': "gold_format_bold"
                        }
                    }
                }
            },
            'SUMMARY': {
                'settings': {
                    'area': "A1:V43",
                    'column_width': [
                        2.09, 2.09, 2.09, 2.09, 0.78, 0.56, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.73,
                        12.64, 0.17, 12.64, 12.45, 0.17, 12.64, 12.64
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 32.50, 16.50, 
                        16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 32.50, 16.50, 42.50, 16.50, 
                        16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 32.50, 16.50, 16.50, 16.50, 
                        16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.00, 16.50, 
                        33.00, 16.50, 16.50
                    ],
                    'columns_to_fill': ["P", "R", "S", "U", "V"],
                    'rows_to_fill': (9, 40),
                    'fill_format': {
                        'P': {
                            '17': "blue_column_year_format",
                            '27': "blue_column_year_format",
                            "base": "blue_data_normal"
                        },
                        'R': {
                            '9': "grey_column_year_format",
                            '17': "grey_column_year_format",
                            '27': "grey_column_year_format",
                            "base": "grey_data_normal"
                        },
                        'S': {
                            '17': "grey_column_year_format",
                            '27': "grey_column_year_format",
                            "base": "grey_data_normal"
                        },
                        'U': {
                            '9': "lightgrey_column_year_format",
                            '17': "lightgrey_column_year_format",
                            '27': "lightgrey_column_year_format",
                            "base": "lightgrey_data_normal"
                        },
                        'V': {
                            '17': "lightgrey_column_year_format",
                            '27': "lightgrey_column_year_format",
                            "base": "lightgrey_data_normal"
                        }
                    }
                },
                'cell_content': {
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'G1': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 10
                            }
                        },
                        'K1': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'V1': {
                            'text': "2 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'text': 'right'
                                },
                                'width': 100
                            }
                        }
                    },
                    'cells': {
                        'P9': {
                            'text': 2020,
                            'format': "blue_column_year_format"
                        },
                        'P10': {
                            'text': 5527,
                            'format': "blue_data_number"
                        },
                        'P11': {
                            'text': 162302,
                            'format': "blue_data_number"
                        },
                        'P12': {
                            'text': 1,
                            'format': "blue_data_normal_italic"
                        },
                        'P13': {
                            'text': 10600,
                            'format': "blue_data_number"
                        },
                        'P14': {
                            'text': .23,
                            'format': "blue_data_normal_italic"
                        },
                        'P15': {
                            'text': 10600,
                            'format': "blue_data_number"
                        },
                        'P16': {
                            'text': .02,
                            'format': "blue_data_normal_italic"
                        },
                        'P20': {
                            'text': .042,
                            'format': "blue_data_normal_percentage"
                        },
                        'P21': {
                            'text': .183,
                            'format': "blue_data_normal_percentage"
                        },
                        'P22': {
                            'text': 28500,
                            'format': "blue_data_number"
                        },
                        'P23': {
                            'text': .854,
                            'format': "blue_data_normal_percentage"
                        },
                        'P24': {
                            'text': 33406,
                            'format': "blue_data_number"
                        },
                        'P25': {
                            'text': 4881,
                            'format': "blue_data_number"
                        },
                        'P29': {
                            'text': 136,
                            'format': "blue_data_number"
                        },
                        'P30': {
                            'text': 16113,
                            'format': "blue_data_number"
                        },
                        'P31': {
                            'text': .854,
                            'format': "blue_data_normal_percentage"
                        },
                        'P32': {
                            'text': "-",
                            'format': "blue_data_number"
                        },
                        'P33': {
                            'text': 13703,
                            'format': "blue_data_number"
                        },
                        'P34': {
                            'text': "-",
                            'format': "blue_data_number"
                        },
                        'P35': {
                            'text': "-",
                            'format': "blue_data_number"
                        },
                        'P37': {
                            'text': 16113,
                            'format': "blue_data_number"
                        },
                        'P38': {
                            'text': 13703,
                            'format': "blue_data_number"
                        },
                        'R18': {
                            'text': "Scenario 1",
                            'format': "grey_scenario_format"
                        },
                        'R19': {
                            'text': "Constant core situation¹",
                            'format': "grey_text_italic"
                        },
                        'R20': {
                            'text': .045,
                            'format': "grey_data_normal_percentage"
                        },
                        'R21': {
                            'text': .183,
                            'format': "grey_data_normal_percentage"
                        },
                        'R22': {
                            'text': 31964,
                            'format': "grey_data_normal_right_number"
                        },
                        'R23': {
                            'text': .95,
                            'format': "grey_data_normal_percentage"
                        },
                        'R24': {
                            'text': 33646,
                            'format': "grey_data_normal_right_number"
                        },
                        'R25': {
                            'text': 33646,
                            'format': "grey_data_normal_right_number"
                        },
                        'R30': {
                            'text': 34512,
                            'format': "grey_data_normal_right_number"
                        },
                        'R31': {
                            'text': .95,
                            'format': "grey_data_normal_percentage"
                        },
                        'R36': {
                            'text': -144,
                            'format': "grey_data_normal_right_number"
                        },
                        'R37': {
                            'text': -144,
                            'format': "grey_data_normal_right_number"
                        },
                        'R38': {
                            'text': 34512,
                            'format': "grey_data_normal_right_number"
                        },
                        'R39': {
                            'text': 770,
                            'format': "grey_data_normal_right_semibold"
                        },
                        'S9': {
                            'text': 2030,
                            'format': "grey_column_year_format"
                        },
                        'S11': {
                            'text': 161500,
                            'format': "grey_data_normal_right_number"
                        },
                        'S12': {
                            'text': 1,
                            'format': "grey_data_normal_italic"
                        },
                        'S13': {
                            'text': 31800,
                            'format': "grey_data_normal_right_number"
                        },
                        'S14': {
                            'text': .23,
                            'format': "grey_data_normal_italic"
                        },
                        'S15': {
                            'text': 11100,
                            'format': "grey_data_normal_right_number"
                        },
                        'S16': {
                            'text': .02,
                            'format': "grey_data_normal_italic"
                        },
                        'S18': {
                            'text': "Scenario 2",
                            'format': "grey_scenario_format"
                        },
                        'S19': {
                            'text': "Increase in \ncare need of \n0.003%²",
                            'format': "grey_text_italic"
                        },
                        'S20': {
                            'text': .048,
                            'format': "grey_data_normal_percentage"
                        },
                        'S21': {
                            'text': .183,
                            'format': "grey_data_normal_percentage"
                        },
                        'S22': {
                            'text': 34361,
                            'format': "grey_data_normal_right_number"
                        },
                        'S23': {
                            'text': .95,
                            'format': "grey_data_normal_percentage"
                        },
                        'S24': {
                            'text': 36169000,
                            'format': "grey_data_normal_right_number"
                        },
                        'S25': {
                            'text': 1808,
                            'format': "grey_data_normal_right_number"
                        },
                        'S30': {
                            'text': 34512,
                            'format': "grey_data_normal_right_number"
                        },
                        'S31': {
                            'text': .95,
                            'format': "grey_data_normal_percentage"
                        },
                        'S36': {
                            'text': -144,
                            'format': "grey_data_normal_right_number"
                        },
                        'S37': {
                            'text': -144,
                            'format': "grey_data_normal_right_number"
                        },
                        'S38': {
                            'text': 34512,
                            'format': "grey_data_normal_right_number"
                        },
                        'S39': {
                            'text': -380,
                            'format': "grey_data_normal_right_semibold"
                        },
                        'U18': {
                            'text': "Scenario 1",
                            'format': "lightgrey_scenario_format"
                        },
                        'U19': {
                            'text': "Constant care situation¹",
                            'format': "lightgrey_text_italic"
                        },
                        'U20': {
                            'text': .046,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'U21': {
                            'text': .183,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'U22': {
                            'text': 33276,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U23': {
                            'text': .95,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'U24': {
                            'text': 35027,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U25': {
                            'text': 1751,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U30': {
                            'text': 34512,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U31': {
                            'text': .95,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'U36': {
                            'text': -144,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U37': {
                            'text': 5468,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U38': {
                            'text': 34512,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'U39': {
                            'text': 141,
                            'format': "lightgrey_data_normal_right_semibold"
                        },
                        'V9': {
                            'text': 2035,
                            'format': "lightgrey_column_year_format"
                        },
                        'V11': {
                            'text': 160700,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V12': {
                            'text': 1,
                            'format': "lightgrey_data_normal_italic"
                        },
                        'V13': {
                            'text': 32800,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V14': {
                            'text': .23,
                            'format': "lightgrey_data_normal_italic"
                        },
                        'V15': {
                            'text': 12400,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V16': {
                            'text': .02,
                            'format': "lightgrey_data_normal_italic"
                        },
                        'V18': {
                            'text': "Scenario 2",
                            'format': "lightgrey_scenario_format"
                        },
                        'V19': {
                            'text': "Increase in \ncare needs of \n0.003%²",
                            'format': "lightgrey_text_italic"
                        },
                        'V20': {
                            'text': .05,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'V21': {
                            'text': .183,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'V22': {
                            'text': 37655,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V23': {
                            'text': .95,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'V24': {
                            'text': 37655,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V25': {
                            'text': 1883,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V30': {
                            'text': 34512,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V31': {
                            'text': .95,
                            'format': "lightgrey_data_normal_percentage"
                        },
                        'V36': {
                            'text': -144,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V37': {
                            'text': 5468,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V38': {
                            'text': 34512,
                            'format': "lightgrey_data_normal_right_number"
                        },
                        'V39': {
                            'text': -1058,
                            'format': "lightgrey_data_normal_right_semibold"
                        }
                    },
                    'merge_cells': {
                        'C4:P5': {
                            'text': "Bad Rappenau",
                            'format': "place_heading_format"
                        },
                        'C6:P7': {
                            'text': "Current Situation",
                            'format': "situation_heading_format"
                        },
                        'C9:O9': {
                            'text': "Demographic trend analysis",
                            'format': "chapter_heading_format"
                        },
                        'C10:O10': {
                            'text': "Population Giebelstadt (City)",
                            'format': "chapter_topics_format"
                        },
                        'C11:O11': {
                            'text': "Population Würzburg (County)",
                            'format': "chapter_topics_format"
                        },
                        'C12:O12': {
                            'text': "in %",
                            'format': "percentage_topic_format"
                        },
                        'D13:O13': {
                            'text': "of which population aged 65-79 years",
                            'format': "chapter_topics_format"
                        },
                        'D14:O14': {
                            'text': "in %",
                            'format': "percentage_topic_format"
                        },
                        'D15:O15': {
                            'text': "of which population aged 80+",
                            'format': "chapter_topics_format"
                        },
                        'D16:O16': {
                            'text': "in %",
                            'format': "percentage_topic_format"
                        },
                        'C17:O17': {
                            'text': "Full inpatient care",
                            'format': "chapter_heading_format"
                        },
                        'C20:O20': {
                            'text': "Care rate of population",
                            'format': "chapter_topics_format"
                        },
                        'C21:O21': {
                            'text': "There of nursing home rate",
                            'format': "chapter_topics_format"
                        },
                        'C22:O22': {
                            'text': "Patients receiving full inpatient care",
                            'format': "chapter_topics_format"
                        },
                        'C23:O23': {
                            'text': "Occupancy rate",
                            'format': "chapter_topics_format"
                        },
                        'C24:O24': {
                            'text': "Number of beds",
                            'format': "chapter_topics_format"
                        },
                        'C25:O25': {
                            'text': "Number of free beds",
                            'format': "chapter_topics_format"
                        },
                        'C27:O27': {
                            'text': "Demand & supply",
                            'format': "chapter_heading_format"
                        },
                        'C28:O28': {
                            'text': "Viewing radius: 15 minutes of driving",
                            'format': "viewing_radius_format"
                        },
                        'C29:O29': {
                            'text': "Nursing homes",
                            'format': "chapter_topics_format"
                        },
                        'C30:O30': {
                            'text': "Beds in supply",
                            'format': "chapter_topics_format"
                        },
                        'C31:O31': {
                            'text': "Occupancy rate",
                            'format': "chapter_topics_format"
                        },
                        'C32:O32': {
                            'text': "Nursing homes in planning",
                            'format': "chapter_topics_format"
                        },
                        'C33:O33': {
                            'text': "Nursing homes under construction",
                            'format': "chapter_topics_format"
                        },
                        'C34:O34': {
                            'text': "Beds in planning",
                            'format': "chapter_topics_format"
                        },
                        'C35:O35': {
                            'text': "Beds under construction",
                            'format': "chapter_topics_format"
                        },
                        'C36:O36': {
                            'text': "Beds lost while meeting federal state law",
                            'format': "chapter_topics_format"
                        },
                        'C37:O37': {
                            'text': "Beds adjusted",
                            'format': "chapter_topics_format"
                        },
                        'C38:O38': {
                            'text': "Demand of beds",
                            'format': "chapter_topics_format"
                        },
                        'C39:O39': {
                            'text': "Beds in surplus or deficit",
                            'format': "chapter_last_topic_format"
                        },
                        'C42:V42': {
                            'text': "¹In scenario 1 the relative situation (product of nursing home rate and care rate) as in 2020 is assumed to be constant for the entire forecasting period.",
                            'format': "side_note_format"
                        },
                        'C43:V43': {
                            'text': "²In scenario 2, it is assumed that the proportion of the nursing home rate will increase by 0.003 percent-points from 2020 to 2035.",
                            'format': "side_note_format"
                        }
                    }
                }
            },
            'LOCATION ANALYSIS': {
                'settings': {
                    'area': "A1:S38",
                    'column_width': [
                        2.18, 2.18, 2.45, 0.22, 27.09, 0.22, 19.00, 3.09, 3.09, 3.09, 3.09, 3.09, 3.09, 3.45, 3.45,
                        3.45, 3.45, 5.27, 3.09
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 95.50, 7.50, 30.00, 30.00, 30.00, 30.00,
                        30.00, 30.00, 30.00, 30.00, 30.00, 30.00, 30.00, 30.00, 30.00, 11.00, 16.50, 7.00, 11.00, 16.50,
                        7.00, 11.00, 16.50, 7.00, 11.00, 16.00, 7.00, 11.00, 16.50, 16.00
                    ]
                },
                'cell_content': {
                    'images': {
                        'C9': {
                            'file': "img/test_map.png",
                            'settings': {
                                'x_scale': .78,
                                'y_scale': .78,
                                'y_offset': 20
                            }
                        },
                        'C24': {
                            'file': "img/locator.png",
                            'settings': {
                                'x_offset': 0,
                                'y_offset': 10,
                                'x_scale': .9,
                                'y_scale': .9
                            }
                        },
                        'C27': {
                            'file': "img/nh_pin.png",
                            'settings': {
                                'x_offset': 0,
                                'y_offset': 10,
                                'x_scale': .9,
                                'y_scale': .9
                            }
                        },
                        'C30': {
                            'file': "img/al_pin.png",
                            'settings': {
                                'x_offset': 0,
                                'y_offset': 10,
                                'x_scale': .9,
                                'y_scale': .9
                            }
                        },
                        'C33': {
                            'file': "img/mixed_pin.png",
                            'settings': {
                                'x_offset': 4,
                                'y_offset': 10,
                                'x_scale': .9,
                                'y_scale': .9
                            }
                        },
                        'C36': {
                            'file': "img/distance_layer.png",
                            'settings': {
                                'x_offset': 0,
                                'y_offset': 10,
                                'x_scale': .9,
                                'y_scale': .9
                            }
                        }
                    },
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'E1_A': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 46
                            }
                        },
                        'E1_B': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 128
                            }
                        },
                        'R1': {
                            'text': "3 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'text': 'right'
                                },
                                'width': 65
                            }
                        }
                    },
                    'cells': {
                        'E25': {
                            'text': "Investment object",
                            'format': "icon_text"
                        },
                        'E27': {
                            'text': "Competitor",
                            'format': "competitor_text"
                        },
                        'E28': {
                            'text': "Nursing home",
                            'format': "icon_text"
                        },
                        'E30': {
                            'text': "Competitor",
                            'format': "competitor_text"
                        },
                        'E31': {
                            'text': "Assisted living",
                            'format': "icon_text"
                        },
                        'E33': {
                            'text': "Competitor",
                            'format': "competitor_text"
                        },
                        'E34': {
                            'text': "Nursing home & Assisted living",
                            'format': "icon_text"
                        },
                        'E36': {
                            'text': "Distance layer",
                            'format': "competitor_text"
                        },
                        'E37': {
                            'text': "15 min walking",
                            'format': "icon_text"
                        },
                    },
                    'merge_cells': {
                        'C20:E20': {
                            'text': "Web view: ",
                            'format': "web_view_text"  
                          },
                        'C21:S21': {
                            'text': "https://www.capitalbay.de",
                            'format': "web_view_link_format"
                        },
                        'C4:J5': {
                            'text': "Bad Rappenau",
                            'format': "place_heading_format"
                        },
                        'C6:J7': {
                            'text': "Location Analysis",
                            'format': "situation_heading_format"
                        },
                        'H23:R38': {
                            'text': "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.",
                            'format': "gpt_text"
                        }
                    }
                }
            },
            'COMPETITOR ANALYSIS 1': {
                'settings': {
                    'area': "A1:X28",
                    'column_width': [
                        2.09, 2.09, 2.64, 0.17, 25.36, 0.00, 24.45, 3.27, 3.27, 6.45, 8.18, 4.73, 3.27, 3.55, 5.82,
                        5.82, 5.82, 5.82, 5.18, 6.00, 5.27, 4.91, 0.00, 3.91
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 95.50, 3.50, 19.00, 17.00, 17.00,
                        17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 17.00, 16.50,
                        14.00, 8.00
                    ],
                    'columns_to_fill': [
                        'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                        'V', 'W', 'X'
                    ],
                    'landscape': True,
                    'rows_to_fill': [8, 10, 25],
                    'fill_format': {
                        'base': {
                            '8': "underline",
                            '10': "underline",
                            '25': "underline"
                        }
                    }
                },
                'cell_content': {
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'E1_A': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 46
                            }
                        },
                        'E1_B': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 128
                            }
                        },
                        'V1': {
                            'text': "4 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'text': 'right'
                                },
                                'width': 65
                            }
                        }
                    },
                    'merge_cells': {
                        'C3:X4': {
                            'text': "Bad Rappenau",
                            'format': "place_heading_format"
                        },
                        'C5:X6': {
                            'text': "Competitor Analysis",
                            'format': "situation_heading_format"
                        }
                    },
                    'cells': {}
                }
            },
            'GOOD TO KNOW': {
                'settings': {
                    'area': "A1:Y50",
                    'column_width': [
                        2.09, 2.09, 2.09, 2.09, 0.78, 0.50, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 5.18, 6.55, 6.55,
                        4.82, 12.55, 0.17, 3.18, 14.64, 2.09, 2.09, 2.09, 5.91, 2.09
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 32.50, 18.00, 32.50, 18.00, 14.50,
                        14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50,
                        14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 7.50, 7.50, 7.50, 11.50, 27.00, 18.00, 15.00,
                        18.00, 15.00, 32.50, 31.00, 15.00, 15.00, 15.00, 15.00, 40.50, 16.50, 9.00
                    ]
                },
                'cell_content': {
                    'images': {
                        'P14': {
                            'file': "img/plot1.png",
                            'settings': {
                                'x_offset': 15,
                                'x_scale': .6,
                                'y_scale': .6
                            }
                        },
                        'A34': {
                            'file': "img/plot2.png",
                            'settings': {
                                'x_scale': .6,
                                'y_scale': .6,
                                'y_offset': 5
                            }
                        },
                        'A16': {
                            'file': "img/plot3.png",
                            'settings': {
                                'x_scale': .7,
                                'y_scale': .7
                            }
                        }
                    },
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'E1_A': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 26
                            }
                        },
                        'E1_B': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 96
                            }
                        },
                        'X1': {
                            'text': "3 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'text': 'right'
                                },
                                'width': 65
                            }
                        }
                    },
                    'cells': {
                        'C12': {
                            'text': "Viewing radius: 15 minutes of driving",
                            'format': "gold_heading"
                        },
                        'Q12': {
                            'text': "Viewing radius: 15 minutes of driving",
                            'format': "gold_heading"
                        },
                        'C13': {
                            'text': "Number of NH facilities",
                            'format': "normal_text"
                        },
                        'O13': {
                            'text': 54,
                            'format': "normal_text_right"
                        },
                        'C14': {
                            'text': "Number of AL facilities",
                            'format': "normal_text"
                        },
                        'O14': {
                            'text': 54,
                            'format': "normal_text_right"
                        },
                        'C15': {
                            'text': "Median numbers of beds (NH)",
                            'format': "normal_text"
                        },
                        'O15': {
                            'text': 117,
                            'format': "normal_text_right"
                        },
                        'C16': {
                            'text': "Median year of construction (NH)",
                            'format': "normal_text"
                        },
                        'O16': {
                            'text': 2007,
                            'format': "normal_text_right"
                        },
                        'C17': {
                            'text': "Median year of construction (AL)",
                            'format': "normal_text"
                        },
                        'O17': {
                            'text': 2007,
                            'format': "normal_text_right"
                        },
                        'Q13': {
                            'text': "Invest costs in nursing homes",
                            'format': "normal_text"
                        }
                    },
                    'merge_cells': {
                        'C4:X5': {
                            'text': "Bad Rappenau",
                            'format': "place_heading_format"
                        },
                        'C6:X7': {
                            'text': "Good to Know",
                            'format': "situation_heading_format"
                        },
                        'C9:N9': {
                            'text': "Market shares",
                            'format': "small_heading"
                        },
                        'C11:O11': {
                            'text': "Operator & facilities",
                            'format': "smaller_heading"
                        },
                        'Q11:X11': {
                            'text': "Prices",
                            'format': "smaller_heading"
                        },
                        'Q47:X51': {
                            'text': "The investment cost rates of the facilities within the catchment area range between €5.50 and €35.60. The median investment cost amount to €10.50. The investment costs at the facility, that is subject to this study amounts to €9.90.",
                            'format': "mass_text"
                        },
                        'C37:O38': {
                            'text': "Purchasing power index (municipality)",
                            'format': "smaller_heading"
                        }
                    }
                }
            },
            'REGULATIONS': {
                'settings': {
                    'area': "A1:Y50",
                    'column_width': [
                        2.09, 2.09, 2.09, 2.09, 0.78, 0.50, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 5.18, 6.55, 6.55,
                        4.82, 12.55, 0.17, 3.18, 14.64, 2.09, 2.09, 2.09, 5.91, 2.09
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 11.50, 27.00, 18.00, 15.00,
                        18.00, 15.00, 32.50, 31.00, 15.00, 15.00, 15.00, 15.00, 40.50, 16.50, 9.00, 32.50, 18.00, 
                        32.50, 18.00, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 
                        14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 7.50, 7.50
                    ],
                    'columns_to_fill': [
                        'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                        'T', 'U', 'V', 'W', 'X', 'Y'
                    ],
                    'rows_to_fill': (9, 24),
                    'fill_format': {
                        'base': "background"
                    }
                },
                'cell_content': {
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'E1_A': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 26
                            }
                        },
                        'E1_B': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 96
                            }
                        },
                        'W1': {
                            'text': "3 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'align': {
                                    'text': 'right'
                                },
                                'width': 65
                            }
                        }
                    },
                    'cells': {
                        'C17': {
                            'text': "Single room quota (min.)",
                            'format': "table_row_heading"
                        },
                        'C18': {
                            'text': "Maximum home size",
                            'format': "table_row_heading"
                        },
                        'C19': {
                            'text': "Minimum room size (SR/DR)",
                            'format': "table_row_heading"
                        },
                        'C20': {
                            'text': "Minimum common area/ residential",
                            'format': "table_row_heading"
                        },
                        'C21': {
                            'text': "Comment",
                            'format': "table_row_heading"
                        },
                        'C22': {
                            'text': "Legal basis",
                            'format': "table_row_heading"
                        }
                    },
                    'merge_cells': {
                        'C4:X5': {
                            'text': "Bad Rappenau",
                            'format': "place_heading_format"
                        },
                        'C6:X7': {
                            'text': "REGULATIONS",
                            'format': "situation_heading_format"
                        },
                        'C10:S10': {
                            'text': "Regulations of federal state",
                            'format': "small_heading_background"
                        },
                        'C12:X14': {
                            'text': "This market study consideres X nursing homes within the vicinity of X minutes driving/walking/cycling. Thereof, Y facilities comply with the federal state regulations and Z facilities that do not fullfill the federal requirements. Assumuning that only 80% of the respective facilities need to comply with the below shown federal state regulations, the resulting loss of beds in the market until 2030 will amount to Z.",
                            'format': "mass_text_background"
                        },
                        'C15:N15': {
                            'text': "Federal state",
                            'format': "smaller_heading_background"
                        },
                        'O15:X15': {
                            'text': "Baden-Wurttemberg",
                            'format': "blue_heading"
                        },
                        'O16:S16': {
                            'text': "New",
                            'format': "table_heading"
                        },
                        'O17:S17': {
                            'text': "100%",
                            'format': "table_normal_text"
                        },
                        'O18:S18': {
                            'text': "100 beds",
                            'format': "table_normal_text"
                        },
                        'O19:S19': {
                            'text': "14 sqm/ 16 sqm¹",
                            'format': "table_normal_text"
                        },
                        'O20:S20': {
                            'text': "5 sqm, min 2/3 for living spaces",
                            'format': "table_normal_text"
                        },
                        'O21:S21': {
                            'text': "/",
                            'format': "table_normal_text"
                        },
                        'O22:S22': {
                            'text': "WTPG, LHeimBauVO",
                            'format': "table_normal_text"
                        },
                        'T16:X16': {
                            'text': "Existing",
                            'format': "table_heading"
                        },
                        'T17:X17': {
                            'text': "100% (as of 2019)",
                            'format': "table_normal_text"
                        },
                        'T18:X18': {
                            'text': "100 beds",
                            'format': "table_normal_text"
                        },
                        'T19:X19': {
                            'text': "14 sqm/ 16 sqm",
                            'format': "table_normal_text"
                        },
                        'T20:X20': {
                            'text': "5 sqm, min 2/3 for living spaces",
                            'format': "table_normal_text"
                        },
                        'T21:X21': {
                            'text': "Transition period 10 years can be extended to 25 years",
                            'format': "table_normal_text"
                        },
                        'T22:X22': {
                            'text': "WTPG, LHeimBauVO",
                            'format': "table_normal_text"
                        }
                    }
                }
            },
            'METHODIC': {
                'settings': {
                    'area': "A1:Z34",
                    'column_width': [
                        2.09, 2.09, 2.09, 2.09, 0.78, 0.56, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.73,
                        0.17, 12.64, 12.45, 0.17, 6.00, 18.00, 2.09, 2.09, 2.09, 2.09, 2.09
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 32.50, 32.50, 18.00, 18.00, 18.00,
                        16.00, 34.00, 34.00, 32.50, 50.00, 50.00, 50.00, 50.00, 50.00, 50.00, 15.00, 15.00, 15.00,
                        15.00, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00
                    ],
                    'columns_to_fill': [
                        'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
                        'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
                    ],
                    'rows_to_fill': (9, 30),
                    'fill_format': {
                        'base': "background"
                    }
                },
                'cell_content': {
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'E1_A': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 26
                            }
                        },
                        'E1_B': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 96
                            }
                        },
                        'Y1': {
                            'text': "6 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'C3': {
                            'text': "About the Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 27,
                                    'color': "#DADADA"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320,
                                'y_offset': 15
                            }
                        },
                        'C5': {
                            'text': "Methodic",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 27,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320,
                                'y_offset': 15
                            }
                        },
                        'D10': {
                            'text': "Methodology, Data analysis & forecasting",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI Semibold",
                                    'size': 12,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 350
                            }
                        },
                        'D11': {
                            'text': f"""The market study highlights the current state of the inpatient care market in Germany and provides a forecast for the demand for nursing care until 2030 and 2035. The study emphasizes the key drivers of demand and the methodology employed to arrive at the forecasted figures. 

The study utilizes a combination of publicly available secondary research. Secondary research includes analyzing geographical, demographical and statistical databases as well as government publications and reputable healthcare sources to gather quantitative data. 

The collected data is analyzed to identify trends, growth drivers, and market dynamics. The analysis encompasses factors such as population demographics, healthcare policies and available market information on existing and future care facilities, prevalence of chronic diseases, and economic indicators affecting the demand for inpatient care. 

To forecast the future demand for nursing care, a combination of demographic projection, trend analysis and consideration of new care facilities to be launched on the market is employed. Demographic projection takes into account population growth, aging trends, and migration patterns. Trend analysis examines historical data and identifies patterns and growth rates to project future demand. New care facilities takes into account buildings that are in planning or under construction. 

All findings of the market study will consider the factors mentioned above to provide a comprehensive understanding of the current state of the inpatient care market.
            """,
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 310,
                                'height': 600
                            }
                        },
                        'D23': {
                            'text': "Limitations",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI Semibold",
                                    'size': 12,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 330,
                                'y_offset': 40
                            }
                        },
                        'D25': {
                            'text': "The forecast is based on available data and assumes that there will be no major disruptive events or policy changes that could significantly impact the demand for inpatient care.",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320
                            }
                        },
                        'R10': {
                            'text': "Data sources",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI Semibold",
                                    'size': 12,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320,
                                'x_offset': 10
                            }
                        },
                        'R11': {
                            'text': """Statistisches Bundesamt
Statista
Pflegemarkt.com
Pflegemarktdatenbank (updates every 3 months)
Demografieportal
Pflegeheim-Atlas Deutschland 2021, Wuest Partner
21st Real Estate
ChatGPT
Open Street Maps
Mapbox
            """,
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320,
                                'x_offset': 10
                            }
                        }
                    }
                }
            },
            'CONTACT': {
                'settings': {
                    'area': "A1:Z35",
                    'column_width': [
                        2.09, 2.09, 2.09, 2.09, 0.78, 0.56, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.09, 2.73,
                        0.17, 12.64, 12.45, 0.17, 6.00, 18.00, 2.09, 2.09, 2.09, 2.09, 2.09
                    ],
                    'row_height': [
                        16.50, 15.50, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 26.50, 16.50, 16.50, 16.50, 16.50,
                        9.00, 16.50, 16.50, 16.50, 16.50, 16.50, 16.50, 50.00, 50.00, 50.00, 50.00, 50.00, 50.00,
                        50.00, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00, 15.00
                    ],
                    'columns_to_fill': [
                        'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                        'V', 'W', 'X', 'Y', 'Z'
                    ],
                    'rows_to_fill': (9, 19),
                    'fill_format': {
                        'base': "background"
                    }
                },
                'cell_content': {
                    'images': {
                        'D18': {
                            'file': "img/Contact.jpg",
                            'settings': {
                                'x_offset': 10
                            }
                        }
                    },
                    'textboxes': {
                        'A1': {
                            'text': "Capital Bay Group   |",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'E1_A': {
                            'text': "Market Study",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 26
                            }
                        },
                        'E1_B': {
                            'text': "CARE",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True,
                                    'color': "#C8B058"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 96
                            }
                        },
                        'Y1': {
                            'text': "7 | 7",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'bold': True
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'C3': {
                            'text': "Keep in Touch",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 27,
                                    'color': "#DADADA"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320,
                                'y_offset': 15
                            }
                        },
                        'C5': {
                            'text': "Capital Bay Team",
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 27,
                                    'color': "#000000"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 320,
                                'y_offset': 15
                            }
                        },
                        'E27': {
                            'text': """This study has been prepared by Capital Bay Group S.A. (hereinafter Capital Bay) to provide investors and business partners of Capital Bay with an overview of current developments in the care and assisted living sector of the real estate industry. Capital Bay emphasizes that this study is not a sufficient basis for decision making and user discretion is necessary for the decision making process. 

This study has been prepared with reasonable care. The information presented has not been verified by Capital Bay for completeness or accuracy. It has been obtained from the sources indicated and supplemented by Capital 
                """,
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': "#BFBFBF"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 308,
                                'height': 280
                            }
                        },
                        'R27': {
                            'text': """Bay's own market knowledge. No confidential or non-public information has been made use.

Capital Bay is not responsible for any incomplete or inaccurate information and readers are urged to verify the information themselves before making any decision. Capital Bay shall not be liable for any omissions or inaccuracies in this report or for any other oral or written statements made in connection with this report.


© 2023 Capital Bay Group
All rights reserved.
    """,
                            'settings': {
                                'font': {
                                    'name': "Segoe UI",
                                    'size': 9,
                                    'color': "#BFBFBF"
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'width': 308,
                                'height': 280,
                                'x_offset': 50
                            }
                        }
                    },
                    'merge_cells': {
                        'E10:O10': {
                            'text': "Stephanie Kühn",
                            'format': "name_format"
                        },
                        'E11:O11': {
                            'text': "Head of Transaction Management",
                            'format': "small_normal_format"
                        },
                        'E12:O12': {
                            'text': "CB Transaction Management GmbH",
                            'format': "small_normal_format"
                        },
                        'E13:O13': {
                            'text': "Sachsendamm 4/5, 10829 Berlin",
                            'format': "small_normal_format"
                        },
                        'E15:O15': {
                            'text': "T +49 30 120866215",
                            'format': "small_normal_format"
                        },
                        'E16:O16': {
                            'text': "mailto:stephanie.kuehn@capitalbay.de",
                            'format': "link_format"
                        },
                        'R10:U10': {
                            'text': "Daniel Ziv",
                            'format': "name_format"
                        },
                        'R11:U11': {
                            'text': "Junior Transaction Manager",
                            'format': "small_normal_format"
                        },
                        'R12:U12': {
                            'text': "CB Transaction Management GmbH",
                            'format': "small_normal_format"
                        },
                        'R13:U13': {
                            'text': "Sachsendamm 4/5, 10829 Berlin",
                            'format': "small_normal_format"
                        },
                        'R15:U15': {
                            'text': "T +49 30 120866281",
                            'format': "small_normal_format"
                        },
                        'R16:U16': {
                            'text': "mailto:daniel.ziv@capitalbay.de",
                            'format': "link_format"
                        }
                    }
                }
            }
        }
    }
micro_living_comparables = {
        'base_worksheet_settings': {
            'paper': 9,
            'hide_grid': 2,
            'fit_to_pages': (1, 1),
            'margins': (0, 0, 0, 0)
        },
        'workbook_format': {
            'font_size': 11,
            'font_name': "Segoe UI"
        },
        'cell_formats': {
            'bold_underline': {
                'font': 'Segoe UI Semibold',
                'bottom': 1
            },
            'bold_vcenter': {
                'font': 'Segoe UI Semibold',
                'valign': 'vcenter'
            },
            'bold_right': {
                'font': 'Segoe UI Semibold',
                'align': 'right'
            },
            'bold_fs9': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'align': 'center'
            },
            'bold_fs9_underline': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'align': 'center',
                'bottom': 1
            },
            'bold_fs9_vcenter_wrap': {
                'font': 'Segoe UI Semibold',
                'font_size': 9,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            },
            'bold_investment_fs9': {
                'font': 'Segoe UI Semibold',
                'align': 'center',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'font_size': 9
            },
            'bold_investment_fs9_underline': {
                'font': 'Segoe UI Semibold',
                'align': 'center',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'font_size': 9,
                'bottom': 1,
                'bottom_color': '#FFFFFF'
            },
            'bold_investment_fs9_wrap_vcenter': {
                'font': 'Segoe UI Semibold',
                'align': 'center',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'font_size': 9,
                'text_wrap': True,
                'valign': 'vcenter'
            },
            'regular': {
                'font': 'Segoe UI',
                'align': 'center'
            },
            'regular_number': {
                'font': 'Segoe UI',
                'align': 'center',
                'num_format': '0',
            },
            'regular_number_with_two_komma': {
                'font': 'Segoe UI',
                'align': 'center',
                'num_format': '0.00'
            },
            'wingdings': {
                'font': 'Wingdings',
                'align': 'center'
            },
            'regular_investment': {
                'font': 'Segoe UI',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'align': 'center'
            },
            'regular_investment_number': {
                'font': 'Segoe UI',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'align': 'center',
                'num_format': '0',
            },
            'regular_investment_number_with_two_komma': {
                'font': 'Segoe UI',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'align': 'center',
                'num_format': '0.00'
            },
            'wingdings_investment': {
                'font': 'Wingdings',
                'bg_color': '#1B2939',
                'color': '#FFFFFF',
                'align': 'center'
            },
            'city_heading': {
                'font': 'Segoe UI',
                'font_size': 40,
                'color': '#C8B058'
            },
            'page_heading': {
                'font': 'Segoe UI',
                'font_size': 40
            }
        },
        'pages': {
            'Competitors De': {
                'settings': {
                    'area': 'A1:K90',
                    'column_width': [
                        28.18, 13.73, 13.73, 13.73, 13.73, 13.73, 13.73, 13.73, 13.73, 13.73, 13.73
                    ],
                    'row_height': [
                        16.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 51.00, 51.00, 14.50,
                        14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50,
                        14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50,
                        14.50, 14.50, 14.50, 14.50, 14.50, 44.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50,
                        14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50, 14.50,
                        14.50
                    ]
                },
                'cell_content': {
                    'images': {
                        'A14': {
                            'file': 'img/test_map.png',
                            'settings': {
                                'y_offset': 10,
                                'y_scale': .8,
                                'x_scale': .8
                            }
                        }
                    },
                    'cells': {
                        'K1': {
                            'text': '1 | 3',
                            'format': 'bold_right'
                        },
                        'A11': {
                            'text': 'Berlin',
                            'format': 'city_heading'
                        },
                        'A12': {
                            'text': 'Student Living',
                            'format': 'page_heading'
                        },
                        'A44': {
                            'text': 'Comparable',
                            'format': 'bold_underline'
                        },
                        'A45': {
                            'text': 'Adresse',
                            'format': 'bold_vcenter'
                        },
                        'A46': {
                            'text': 'Anzahl der Apartments'
                        },
                        'A47': {
                            'text': 'Untere Mietspanne (in €)'
                        },
                        'A48': {
                            'text': 'Obere Mietspanne (in €)'
                        },
                        'A49': {
                            'text': 'Ø Miete / Apartment (in €)'
                        },
                        'A50': {
                            'text': 'Kleinstes Apartment (in m²)'
                        },
                        'A51': {
                            'text': 'Größtes Apartment (in m²)'
                        },
                        'A52': {
                            'text': 'Ø m² / Apartment'
                        },
                        'A53': {
                            'text': 'Ø Miete / m²'
                        },
                        'A54': {
                            'text': 'Möbliert'
                        },
                        'A55': {
                            'text': 'Küche'
                        },
                        'A56': {
                            'text': 'Balkon'
                        },
                        'A57': {
                            'text': 'Eigenes Bad'
                        },
                        'A58': {
                            'text': 'Gemeinschaftsräume'
                        },
                        'A59': {
                            'text': 'Services'
                        },
                        'A60': {
                            'text': 'Fitnessstudio'
                        },
                        'A61': {
                            'text': 'Medienlounge'
                        },
                        'A62': {
                            'text': 'Lern-Lounge'
                        },
                        'A63': {
                            'text': 'Waschraum'
                        },
                        'A64': {
                            'text': 'Veranstaltungsräume'
                        },
                        'A65': {
                            'text': 'Bar'
                        },
                        'A66': {
                            'text': 'Gemeinschaftliches Kochen'
                        }
                    },
                    'textboxes': {
                        'A1_A': {
                            'text': 'Capital Bay Group |',
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                }
                            }
                        },
                        'A1_B': {
                            'text': 'Comparables',
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semibold'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 132
                            }
                        },
                        'A1_C': {
                            'text': 'Micro Living',
                            'settings': {
                                'font': {
                                    'name': 'Segoe UI Semibold',
                                    'color': '#C8B058'
                                },
                                'line': {
                                    'none': True
                                },
                                'fill': {
                                    'none': True
                                },
                                'x_offset': 202
                            }
                        }
                    }
                }
            }
        }
    }