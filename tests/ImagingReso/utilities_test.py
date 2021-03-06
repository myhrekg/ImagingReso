import unittest
import numpy as np
import os
import pprint
import pandas as pd

from ImagingReso.resonance import Resonance
from ImagingReso._utilities import *


class TestUtilities_1(unittest.TestCase):
    def test_is_element_in_database(self):
        """assert is_element_in_database works correctly for good and bad input elements"""

        # empty element
        _element = ''
        _answer = is_element_in_database(element=_element)
        self.assertFalse(_answer)

        # element not in database
        _element = 'Ne'
        _answer = is_element_in_database(element=_element)
        self.assertFalse(_answer)

        # element in database
        _element = 'Co'
        _answer = is_element_in_database(element=_element)
        self.assertTrue(_answer)

    def test_get_list_of_element_raise_error_if_wrong_database(self):
        """assert ValueError if wrong database passed to get_list_element_from_database"""
        _database_1 = 'do_not_exist'
        self.assertRaises(ValueError, get_list_element_from_database, database=_database_1)

    def test_checking_stack(self):
        """assert checking_stack_works in all good cases (1 or more stacks)"""

        # normal simple stack
        stack_1 = {'Ag': {'elements': ['Ag'],
                          'stoichiometric_ratio': [1],
                          'thickness': {'value': 0.025,
                                        'units': 'mm'},
                          },
                   }
        _result_1 = checking_stack(stack=stack_1)
        self.assertTrue(_result_1)

        # complex set of stacks
        stack_2 = {'Co': {'elements': ['Co'],
                          'stoichiometric_ratio': [1],
                          'thickness': {'value': 0.03,
                                        'units': 'mm'},
                          },
                   'GdEu': {'elements': ['Gd', 'Eu'],
                            'stoichiometric_ratio': [1, 1],
                            'thickness': {'value': 0.025,
                                          'units': 'mm'},
                            },
                   }
        _result_2 = checking_stack(stack=stack_2)
        self.assertTrue(_result_2)

    def test_checking_stack_raises_value_error_if_element_missing_from_database(self):
        """assert checking_stack raises an error if elements can not be found in database"""
        stack_2 = {'Ne': {'elements': ['Ne'],
                          'stoichiometric_ratio': [1],
                          'thickness': {'value': 0.03,
                                        'units': 'mm'},
                          },
                   'GdEu': {'elements': ['Gd', 'Eu'],
                            'stoichiometric_ratio': [1, 1],
                            'thickness': {'value': 0.025,
                                          'units': 'mm'},
                            },
                   }
        self.assertRaises(ValueError, checking_stack, stack=stack_2)

    def test_checking_stack_raises_value_error_if_thickness_has_wrong_format(self):
        """assert checking_stack raises an error if thickness is not a number"""
        stack_2 = {'Ag': {'elements': ['Ag'],
                          'stoichiometric_ratio': [1],
                          'thickness': {'value': '0.025',
                                        'units': 'mm'},
                          },
                   'GdEu': {'elements': ['Gd', 'Eu'],
                            'stoichiometric_ratio': [1, 1],
                            'thickness': {'value': 0.025,
                                          'units': 'mm'},
                            },
                   }
        self.assertRaises(ValueError, checking_stack, stack=stack_2)

    def test_raises_error_when_size_stoichiometric_ratio_is_different_from_elements(self):
        """assert checking_stack raises error if size of stoichiometric_ratio and elements do not match"""
        stack = {'Ag': {'elements': ['Ag'],
                        'stoichiometric_ratio': [1],
                        'thickness': {'value': 0.025,
                                      'units': 'mm'},
                        },
                 'GdEu': {'elements': ['Gd', 'Eu'],
                          'stoichiometric_ratio': [1],
                          'thickness': {'value': 0.025,
                                        'units': 'mm'},
                          },
                 }
        self.assertRaises(ValueError, checking_stack, stack=stack)

    def test_formula_to_dictionary_raises_error_when_unknow_element(self):
        """assert formula_to_dictionary raises error if element is unknown"""
        _formula = 'NeCo'
        self.assertRaises(ValueError, formula_to_dictionary, formula=_formula)

    def test_formula_to_dictionary_works_with_various_cases(self):
        """assert formulla_to_dictionary works in all cases"""

        # 'Ag'
        _formula_1 = 'Ag'
        _dict_returned = formula_to_dictionary(formula=_formula_1)
        _dict_expected = {'Ag': {'elements': ['Ag'],
                                 'stoichiometric_ratio': [1],
                                 'thickness': {'value': np.NaN, 'units': 'mm'},
                                 'density': {'value': np.NaN, 'units': 'g/cm3'},
                                 },
                          }
        self.assertEqual(_dict_returned, _dict_expected)

        # 'Ag2Co'
        _formula_2 = 'Ag2Co'
        _dict_returned = formula_to_dictionary(formula=_formula_2, thickness=10)
        _dict_expected = {'Ag2Co': {'elements': ['Ag', 'Co'],
                                    'stoichiometric_ratio': [2, 1],
                                    'thickness': {'value': 10, 'units': 'mm'},
                                    'density': {'value': np.NaN, 'units': 'g/cm3'},
                                    },
                          }
        self.assertEqual(_dict_returned, _dict_expected)

        # 'Ag2CoU3'
        _formula_3 = 'Ag2CoU3'
        _dict_returned = formula_to_dictionary(formula=_formula_3, density=20)
        _dict_expected = {'Ag2CoU3': {'elements': ['Ag', 'Co', 'U'],
                                      'stoichiometric_ratio': [2, 1, 3],
                                      'thickness': {'value': np.NaN, 'units': 'mm'},
                                      'density': {'value': 20, 'units': 'g/cm3'},
                                      },
                          }
        self.assertEqual(_dict_returned, _dict_expected)

        # 'Ag2Co' with thickness=0.025
        _formula_2 = 'Ag2Co'
        _dict_returned = formula_to_dictionary(formula=_formula_2, thickness=0.025)
        _dict_expected = {'Ag2Co': {'elements': ['Ag', 'Co'],
                                    'stoichiometric_ratio': [2, 1],
                                    'thickness': {'value': 0.025, 'units': 'mm'},
                                    'density': {'value': np.NaN, 'units': 'g/cm3'},
                                    },
                          }
        self.assertEqual(_dict_returned, _dict_expected)

    def test_get_isotope_dicts_returns_correct_dictionary(self):
        """assert get_isotope_dict works with typical entry element Ag"""
        _element = 'Ag'
        _dict_returned = get_isotope_dicts(element=_element)
        _dict_expected = {'density': {'value': 10.5,
                                      'units': 'g/cm3'},
                          'isotopes': {'list': ['107-Ag', '109-Ag', '110-Ag', '111-Ag'],
                                       'file_names': ['Ag-107.csv', 'Ag-109.csv', 'Ag-110.csv', 'Ag-111.csv'],
                                       'mass': {'value': [106.905093, 108.904756, 109.90611, 110.905295],
                                                'units': 'g/mol'},
                                       'density': {'value': [10.406, 10.600, 10.698, 10.795],
                                                   'units': 'g/cm3'},
                                       'isotopic_ratio': [0.51839, 0.481610, 0.0, 0.0]},
                          'molar_mass': {'value': 107.8682,
                                         'units': 'g/cm3'},
                          }

        # list of isotopes
        self.assertEqual(_dict_returned['isotopes']['list'], _dict_expected['isotopes']['list'])
        # names of isotopes
        self.assertEqual(_dict_returned['isotopes']['file_names'], _dict_expected['isotopes']['file_names'])
        # mass of isotopes
        self.assertEqual(_dict_returned['isotopes']['mass']['value'], _dict_expected['isotopes']['mass']['value'])
        # density of isotopes
        self.assertAlmostEqual(_dict_returned['isotopes']['density']['value'][0],
                               _dict_expected['isotopes']['density']['value'][0], delta=0.001)
        self.assertAlmostEqual(_dict_returned['isotopes']['density']['value'][1],
                               _dict_expected['isotopes']['density']['value'][1], delta=0.001)
        # atomic_ratio
        self.assertAlmostEqual(_dict_returned['isotopes']['isotopic_ratio'][0],
                               _dict_expected['isotopes']['isotopic_ratio'][0], delta=0.0001)
        self.assertAlmostEqual(_dict_returned['isotopes']['isotopic_ratio'][1],
                               _dict_expected['isotopes']['isotopic_ratio'][1], delta=0.0001)
        # density
        self.assertEqual(_dict_returned['density']['value'], _dict_expected['density']['value'])
        # molar mass
        self.assertEqual(_dict_returned['molar_mass']['value'], _dict_expected['molar_mass']['value'])

    def test_get_isotope_returns_empty_dict_if_missing_element(self):
        """assert get_isotopes_dict returns empty dict if element can not be found such as Xo"""
        _element = 'Xo'
        _dict_returned = get_isotope_dicts(element=_element)
        _dict_expected = {'isotopes': {'list': [],
                                       'file_names': [],
                                       'mass': {'value': [],
                                                'units': 'g/mol',
                                                },
                                       'density': {'value': [],
                                                   'units': 'g/cm3'},
                                       'isotopic_ratio': []},
                          'density': {'value': np.NaN,
                                      'units': 'g/cm3'},
                          'molar_mass': {'value': np.NaN,
                                         'units': 'g/mol',
                                         },
                          }
        self.assertEqual(_dict_returned, _dict_expected)

    def test_get_isotope_dicts_returns_correct_element(self):
        """assert get_isotopes_dict returns correct isotopes if element with single symbol such as C"""
        _element = 'C'
        _dict_returned = get_isotope_dicts(element=_element)
        _dict_expected = {'isotopes': {'list': ['12-C', '13-C'],
                                       'file_names': ['C-12.csv', 'C-13.csv'],
                                       'mass': {'value': [12.0, 13.0033548378],
                                                'units': 'g/mol',
                                                },
                                       'density': {'value': [2.0981291681583922, 2.27355983909181],
                                                   'units': 'g/cm3'},
                                       'isotopic_ratio': [0.9893000000000001, 0.010700000000000001]},
                          'density': {'value': 2.1,
                                      'units': 'g/cm3'},
                          'molar_mass': {'value': 12.0107,
                                         'units': 'g/mol',
                                         },
                          }

        self.assertEqual(_dict_returned, _dict_expected)

    def test_get_mass(self):
        """assert get_mass works for isotopes and elements"""
        _isotope = '107-Ag'
        _returned_mass = get_mass(_isotope)
        _expected_mass = 106.905093
        self.assertAlmostEqual(_returned_mass, _expected_mass, delta=0.00001)

        _element = 'Ag'
        _returned_mass = get_mass(_element)
        _expected_mass = 107.8682
        self.assertEqual(_returned_mass, _expected_mass)

    def test_get_density(self):
        """assert get_density works"""
        _element = 'Ag'
        _returned_density = get_density(_element)
        _expected_density = 10.5
        self.assertEqual(_returned_density, _expected_density)

    def test_get_compound_density(self):
        """assert the get_compound_density works"""
        list_ratio = [1, 2]
        list_density = [10, 20]
        _returned_compound_density = get_compound_density(list_density=list_density,
                                                          list_ratio=list_ratio)
        _expected_compound_density = (1 * 10) / 3. + (2 * 20) / 3.
        self.assertEqual(_returned_compound_density, _expected_compound_density)


class TestUtilities_2(unittest.TestCase):
    def setUp(self):
        _file_path = os.path.dirname(__file__)
        self.database_path = os.path.abspath(os.path.join(_file_path, '../../ImagingReso/reference_data/ENDF_VIII'))

    def test_get_database_name_raises_error_if_wrong_file(self):
        """assert IOError is raised if get_database has wrong file name passed in"""
        file_name = 'do_not_exist'
        self.assertRaises(IOError, get_database_data, file_name=file_name)

    def test_get_database_works(self):
        """assert get_database returns correct pandas object"""
        file_name = os.path.join(self.database_path, 'Ag-107.csv')
        df = get_database_data(file_name=file_name)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_interpolated_data(self):
        """assert get_interpolated_data returns the correct dictionary of x_axis and y_axis"""
        file_name = os.path.join(self.database_path, 'Ag-107.csv')
        df = get_database_data(file_name=file_name)
        E_min = 300
        E_max = 600
        _dict = get_interpolated_data(df=df, E_min=E_min, E_max=E_max, E_step=10)

        # first value
        x_axis_0_returned = _dict['x_axis'][0]
        y_axis_0_returned = _dict['y_axis'][0]
        x_axis_0_expected = 300
        y_axis_0_expected = 4.101356
        self.assertEqual(x_axis_0_expected, x_axis_0_returned)
        self.assertAlmostEqual(y_axis_0_expected, y_axis_0_returned, delta=0.001)

        # last value
        x_axis_last_returned = _dict['x_axis'][-1]
        y_axis_last_returned = _dict['y_axis'][-1]
        x_axis_last_expected = 600
        y_axis_last_expected = 7.237503
        self.assertEqual(x_axis_last_expected, x_axis_last_returned)
        self.assertAlmostEqual(y_axis_last_expected, y_axis_last_returned, delta=0.00001)

    def test_get_sigma(self):
        """assert get_sigma returns the correct dictionary of energy and sigma keys"""
        file_name = os.path.join(self.database_path, 'Ag-107.csv')
        _dict_returned = get_sigma(database_file_name=file_name, E_min=300,
                                   E_max=600,
                                   E_step=10)

        # first value
        energy_0_returned = _dict_returned['energy_eV'][0]
        sigma_0_returned = _dict_returned['sigma_b'][0]
        energy_0_expected = 300
        sigma_0_expected = 4.101356
        self.assertEqual(energy_0_expected, energy_0_returned)
        self.assertAlmostEqual(sigma_0_expected, sigma_0_returned, delta=0.001)

        # last value
        energy_last_returned = _dict_returned['energy_eV'][-1]
        sigma_last_returned = _dict_returned['sigma_b'][-1]
        energy_last_expected = 600
        sigma_last_expected = 7.2375030
        self.assertEqual(energy_last_expected, energy_last_returned)
        self.assertAlmostEquals(sigma_last_expected, sigma_last_returned, delta=0.0001)

    def test_get_atoms_per_cm3_of_layer(self):
        """assert get_atoms_per_cm3_of_layer works"""
        _stack = {'CoAg': {'elements': ['Co', 'Ag'],
                           'stoichiometric_ratio': [1, 1],
                           'thickness': {'value': 0.025,
                                         'units': 'mm'},
                           'density': {'value': 9.8,
                                       'units': 'g/cm3'},
                           },
                  'Ag': {'elements': ['Ag'],
                         'stoichiometric_ratio': [1],
                         'thickness': {'value': 0.03,
                                       'units': 'mm'},
                         },
                  }
        o_reso = Resonance(stack=_stack)
        _stack_returned = o_reso.stack
        _atoms_per_cm3 = get_atoms_per_cm3_of_layer(compound_dict=_stack['CoAg'])
        self.assertAlmostEqual(_atoms_per_cm3['Ag'], 3.5381585765227393e22, delta=1)

    def test_calculate_transmission(self):
        """assert calculate_transmission works"""
        thickness = 10  # cm
        atoms_per_cm3 = 8.9e22
        sigma_b = np.linspace(1, 10, 10)
        transmission_returned = calculate_transmission(thickness_cm=thickness,
                                                       atoms_per_cm3=atoms_per_cm3,
                                                       sigma_b=sigma_b)
        transmission_expected = np.array([np.exp(-thickness * 1e-24 * _b * atoms_per_cm3) for _b in sigma_b])
        self.assertTrue((transmission_expected == transmission_returned).all())

    def test_set_distance_units(self):
        """asset set_distance_units works"""
        # cm -> mm
        value = 10
        from_units = 'cm'
        to_units = 'mm'
        new_value = set_distance_units(value=value,
                                       from_units=from_units,
                                       to_units=to_units)
        self.assertEqual(new_value, 100)

        # mm -> cm
        value = 10
        from_units = 'mm'
        to_units = 'cm'
        new_value = set_distance_units(value=value,
                                       from_units=from_units,
                                       to_units=to_units)
        self.assertEqual(new_value, 1)

    def test_energy_to_lambda(self):
        """assert energy_to_lambda works"""
        energy_ev = np.linspace(1, 10, 10)
        energy_lambda = ev_to_angstroms(array=energy_ev)

        expected_energy_lambda_0 = 0.28598427
        expected_energy_lambda_1 = 0.20222141
        expected_energy_lambda_2 = 0.16511309
        expected_energy_lambda_3 = 0.14299213
        self.assertAlmostEquals(expected_energy_lambda_0, energy_lambda[0], delta=0.0001)
        self.assertAlmostEquals(expected_energy_lambda_1, energy_lambda[1], delta=0.0001)
        self.assertAlmostEquals(expected_energy_lambda_2, energy_lambda[2], delta=0.0001)
        self.assertAlmostEquals(expected_energy_lambda_3, energy_lambda[3], delta=0.0001)


class TestUtilities_xaxis_convertor(unittest.TestCase):
    def test_complains_if_wrong_units(self):
        """assert ValueError raised if wrong units given"""
        _from_units = 'eV'
        _to_units = 'unknown'
        _array = np.linspace(1, 10)
        self.assertRaises(ValueError, convert_x_axis, array=_array, from_units=_from_units,
                          to_units=_to_units)

        _to_units = 'eV'
        _from_units = 'unknown'
        _array = np.linspace(1, 10)
        self.assertRaises(ValueError, convert_x_axis, array=_array, from_units=_from_units,
                          to_units=_to_units)

    def test_units_not_case_sensitivie(self):
        """assert from and to units are not case sensitives """
        _from_units = 'EV'
        _to_units = 'Angstroms'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        self.assertTrue(isinstance(_array_returned, np.ndarray))

        _from_units = 'EV'
        _to_units = 'anGSTRoms'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        self.assertTrue(isinstance(_array_returned, np.ndarray))

        _from_units = 'angStrOms'
        _to_units = 'eV'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        self.assertTrue(isinstance(_array_returned, np.ndarray))

        _from_units = 'angStrOms'
        _to_units = 's'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units,
                                         offset_us=1,
                                         source_to_detector_m=1)
        self.assertTrue(isinstance(_array_returned, np.ndarray))

    def test_array_not_changed_if_same_units_before_and_after(self):
        """assert array untouched if from_units is identical to to_units"""
        _from_units = 'ev'
        _to_units = 'ev'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        self.assertTrue((_array_returned == _array).all())

        _from_units = 'angstroms'
        _to_units = 'angstroms'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        self.assertTrue((_array_returned == _array).all())

        _from_units = 's'
        _to_units = 's'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        self.assertTrue((_array_returned == _array).all())

        # from eV to Angstroms

    def test_conversion_from_ev_to_angstroms_works(self):
        """assert conversion from eV to Angstroms works"""
        _from_units = 'ev'
        _to_units = 'angstroms'
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units)
        _array_expected = []
        for _value in _array:
            _tmp = 81.787 / (np.float(_value) * 1000.)
            _array_expected.append(np.sqrt(_tmp))

        self.assertTrue((_array_expected == _array_returned).all())

    # from eV to time
    def test_conversion_from_ev_to_time_works(self):
        """assert conversion from eV to time works"""
        _from_units = 'ev'
        _to_units = 's'
        _array = np.linspace(1, 10)

        # error raised if source_detector missing
        _offset_us = 5
        self.assertRaises(ValueError, convert_x_axis, array=_array,
                          from_units=_from_units,
                          to_units=_to_units)

        _source_to_detector_m = 15
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units,
                                         offset_us=_offset_us,
                                         source_to_detector_m=_source_to_detector_m)

        time_s = np.sqrt(81.787 / (_array * 1000.)) * _source_to_detector_m / 3956.
        time_record_s = time_s - _offset_us * 1e-6
        _array_expected = time_record_s
        self.assertTrue((_array_expected == _array_returned).all())

    # from angstroms to ev
    def test_conversion_from_angstroms_to_ev(self):
        """assert conversion from angstroms to ev works"""
        _from_units = 'angstroms'
        _to_units = 'ev'
        _array = np.linspace(1, 10)

        _array_returned = convert_x_axis(array=_array, from_units=_from_units, to_units=_to_units)
        _array_expected = (81.787 / (1000. * _array ** 2))
        self.assertTrue((_array_expected == _array_returned).all())

    # from eV to anstroms and back to eV
    def test_double_conversion_from_ev_to_ev_via_angstroms(self):
        """assert double conversion from eV to eV via Anstroms return same array"""
        _array = np.linspace(1, 10)
        _array_angsroms = convert_x_axis(array=_array, from_units='ev',
                                         to_units='Angstroms')
        _array_ev = convert_x_axis(array=_array_angsroms, from_units='angstroms',
                                   to_units='ev')
        # checking one by one every element of the array
        for _index in np.arange(len(_array)):
            self.assertAlmostEqual(_array[_index], _array_ev[_index], delta=0.0001)

    def test_conversion_from_s_to_ev(self):
        """assert conversion from s to ev works"""
        _from_units = 's'
        _to_units = 'ev'
        _offset_us = 1
        _source_to_detector_m = 15.0
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units,
                                         offset_us=_offset_us,
                                         source_to_detector_m=_source_to_detector_m)
        lambda_a = 3956. * (_array + _offset_us * 1e-6) / _source_to_detector_m
        _array_expected = (81.787 / pow(lambda_a, 2)) / 1000.
        # checking one by one every element of the array
        for _index in np.arange(len(_array)):
            self.assertAlmostEqual(_array_returned[_index], _array_expected[_index], delta=0.0001)

    def test_conversion_from_angstroms_to_s(self):
        """assert conversion from angstroms to s works"""
        _from_units = 'angstroms'
        _to_units = 's'
        _offset_us = 1
        _source_to_detector_m = 15.0
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units,
                                         offset_us=_offset_us,
                                         source_to_detector_m=_source_to_detector_m)

        _array_expected = (_source_to_detector_m * _array / 3956) + _offset_us * 1e-6
        # checking one by one every element of the array
        for _index in np.arange(len(_array)):
            self.assertAlmostEqual(_array_returned[_index], _array_expected[_index], delta=0.0001)

    def test_conversion_from_s_to_angstroms(self):
        """assert conversion from s to angstroms works"""
        _from_units = 's'
        _to_units = 'angstroms'
        _offset_us = 1
        _source_to_detector_m = 15.0
        _array = np.linspace(1, 10)
        _array_returned = convert_x_axis(array=_array,
                                         from_units=_from_units,
                                         to_units=_to_units,
                                         offset_us=_offset_us,
                                         source_to_detector_m=_source_to_detector_m)

        _array_expected = 3956. * (_array + _offset_us * 1e-6) / _source_to_detector_m
        # checking one by one every element of the array
        for _index in np.arange(len(_array)):
            self.assertAlmostEqual(_array_returned[_index], _array_expected[_index], delta=0.0001)



            # def test_conversion_from_angstroms_to_ev_works(self):
            # """assert conversion from Angsroms to eV works"""
            # _from_units = 'angstroms'
            # _to_units = 'ev'
            # _array = np.linspace(1,10)
            # _array_returned = convert_x_axis(array=_array, 
            # from_units=_from_units, 
            # to_units=_to_units)        
            # _array_expected = []
            # for _value in _array:
            # _tmp = 81.787 / np.float(_value)**2
            # _array_expected.append(_tmp / 1000.)

            # self.assertEqual(_array_expected, _array_returned)
