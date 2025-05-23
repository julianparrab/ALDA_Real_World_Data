import unittest
import pandas as pd
import numpy as np
import tempfile
import os
import re
from unittest.mock import patch
from io import StringIO
from src.parser import load_dataset, _initial_cleaning, _validate_data, _process_columns

class TestVehicleDataset(unittest.TestCase):
    def setUp(self):
        """Create a sample DataFrame for testing"""
        self.sample_data = {
            'id': [1, 2, 3, 4],
            'plate_number': ['ABC123', 'XYZ789', 'INVALID', 'DEF456'],
            'brand': ['Toyota', 'Ford', 'BMW', 'Chevrolet'],
            'model': ['Corolla', 'F-150', 'X5', 'Spark'],
            'year': [2015, 2018, 2020, 2016],
            'color': ['Red', 'Blue', 'Black', 'White'],
            'fuel_Type': ['Gasoline', 'Diesel', 'Invalid', 'Electric'],
            'transmission_type': ['Automatic', 'Manual', 'Automatic', 'Invalid'],
            'odometer_reading': [45000.5, 78000.0, 12000.0, 65000.0],
            'owner_id': ['ID100', 'ID200', 'ID300', None],
            'vehicle_status': ['IN_USE', 'SELLING', 'MAINTENANCE', 'INVALID'],
            'engine_size': ['1.8L', '2.5L', '3.0L', '1.4L'],
            'registration_date': ['2020-01-15', '2019-05-20', '2021-02-10', '2018-11-30']
        }
        
        # Create a temporary CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        pd.DataFrame(self.sample_data).to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up temporary files"""
        os.unlink(self.temp_file.name)
    
    def test_load_dataset_success(self):
        """Test successful loading of dataset"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            df = load_dataset(self.temp_file.name)
            
            # Basic checks
            self.assertIsInstance(df, pd.DataFrame)
            self.assertFalse(df.empty)
            self.assertIn('DataFrame loaded successfully', fake_out.getvalue())
            
            # Check column normalization
            self.assertIn('fuel_type', df.columns)  # Should be lowercase
            
    def test_empty_dataframe(self):
        """Test handling of empty CSV file"""
        empty_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        empty_file.close()
        
        with patch('sys.stdout', new=StringIO()) as fake_out:
            df = load_dataset(empty_file.name)
            self.assertTrue(df.empty)
            self.assertIn('The DataFrame is empty', fake_out.getvalue())
        os.unlink(empty_file.name)
    
    def test_initial_cleaning(self):
        """Test the _initial_cleaning function"""
        test_df = pd.DataFrame({' ID ': [1], '  Value  ': [10]})
        cleaned_df = _initial_cleaning(test_df)
        
        self.assertEqual(list(cleaned_df.columns), ['id', 'value'])
        self.assertEqual(len(cleaned_df), 1)
    
    def test_validate_data(self):
        """Test data validation functions"""
        test_df = pd.DataFrame({
            'plate_number': ['ABC123', 'INVALID', 'XYZ789'],
            'fuel_type': ['Gasoline', 'Invalid', 'Diesel'],
            'transmission_type': ['Automatic', 'Manual', 'Invalid'],
            'vehicle_status': ['IN_USE', 'SELLING', 'INVALID'],
            'owner_id': ['ID1', 'ID2', None]
        })
        
        pattern = re.compile(r'^[A-Z]{3}[0-9]{3}$')
        validated_df = _validate_data(
            test_df, 
            pattern, 
            valid_fuels={'Gasoline', 'Diesel'},
            valid_status={'IN_USE', 'SELLING'},
            valid_transmission={'Automatic', 'Manual'}
        )
        
        # Should only keep first row
        self.assertEqual(len(validated_df), 1)
        self.assertEqual(validated_df.iloc[0]['plate_number'], 'ABC123')
    
    def test_process_columns(self):
        """Test column processing functions"""
        test_df = pd.DataFrame({
            'engine_size': ['1.8L', '2.5L', '3.0L'],
            'year': ['2015', '2018', '2020'],
            'odometer_reading': ['45000.5', '78000.0', '12000.0'],
            'registration_date': ['2020-01-15', '2019-05-20', '2021-02-10']
        })
        
        processed_df = _process_columns(test_df)
        
        # Check engine size conversion
        self.assertTrue(pd.api.types.is_float_dtype(processed_df['engine_size']))
        self.assertEqual(processed_df['engine_size'].iloc[0], 1.8)
        
        # Check numeric conversion
        self.assertTrue(pd.api.types.is_integer_dtype(processed_df['year']))
        
        # Check date conversion
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(processed_df['registration_date']))
    
    def test_plate_number_validation(self):
        """Test plate number validation"""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            df = load_dataset(self.temp_file.name)
            # Should keep ABC123, XYZ789, DEF456 and remove INVALID
            self.assertEqual(len(df), 3)
            self.assertNotIn('INVALID', df['plate_number'].values)
            self.assertIn('Removing 1 records with invalid plates', fake_out.getvalue())
    
    def test_fuel_type_validation(self):
        """Test fuel type validation"""
        df = load_dataset(self.temp_file.name)
        valid_fuels = {'Gasoline', 'Diesel', 'Electric', 'Hybrid'}
        self.assertTrue(all(fuel in valid_fuels for fuel in df['fuel_type'].unique()))
    
    def test_transmission_validation(self):
        """Test transmission type validation"""
        df = load_dataset(self.temp_file.name)
        valid_transmissions = {'Automatic', 'Manual'}
        self.assertTrue(all(trans in valid_transmissions for trans in df['transmission_type'].unique()))
    
    def test_owner_id_validation(self):
        """Test owner ID validation (should remove nulls)"""
        df = load_dataset(self.temp_file.name)
        self.assertFalse(df['owner_id'].isnull().any())
    
    def test_vehicle_status_validation(self):
        """Test vehicle status validation"""
        df = load_dataset(self.temp_file.name)
        valid_status = {'IN_USE', 'SELLING', 'MAINTENANCE'}
        self.assertTrue(all(status in valid_status for status in df['vehicle_status'].unique()))

if __name__ == '__main__':
    unittest.main()