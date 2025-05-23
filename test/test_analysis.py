import unittest
from unittest.mock import patch, mock_open
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from src.analysis import ( 
    plot_categories,
    plot_vehicles_map,
    plot_accident_history,
    plot_status_vs_value
)

class TestVisualizationFunctions(unittest.TestCase):
    def setUp(self):
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'city': ['Bogotá', 'Medellín', 'Bogotá', 'Cali', 'Medellín'],
            'department': ['Cundinamarca', 'Antioquia', 'Cundinamarca', 'Valle', 'Antioquia'],
            'brand': ['Toyota', 'Chevrolet', 'Toyota', 'Renault', 'Mazda'],
            'estimated_market_value': [50000, 30000, 45000, 55000, 35000],
            'accident_history': ['True', 'False', 'True', 'False', 'True'],
            'category1': ['A', 'B', 'A', 'C', 'B'],
            'category2': ['X', 'Y', 'X', 'Z', 'Y']
        })
        
        # Create test plots directory if it doesn't exist
        os.makedirs("plots", exist_ok=True)

    def tearDown(self):
        # Clean up any created files
        for f in os.listdir("plots"):
            if f.endswith(".png"):
                os.remove(os.path.join("plots", f))

    def test_plot_categories(self):
        """Test plot_categories function with valid inputs"""
        columns = ['category1', 'category2']
        plot_categories(self.sample_data, columns, 1, 2, "test_categories.png")
        
        # Verify file was created
        self.assertTrue(os.path.exists("plots/test_categories.png"))
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        with self.assertRaises(KeyError):
            plot_categories(empty_df, columns, 1, 2, "should_not_exist.png")
        
        # Test with invalid column names
        with self.assertRaises(KeyError):
            plot_categories(self.sample_data, ['nonexistent'], 1, 1, "should_not_exist.png")

    @patch('plotly.express.density_mapbox')
    def test_plot_vehicles_map(self, mock_density_mapbox):
        """Test plot_vehicles_map function"""
        plot_vehicles_map(self.sample_data)
        
        # Verify the function tried to create a map
        self.assertTrue(mock_density_mapbox.called)
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame(columns=['city'])
        with self.assertRaises(KeyError):
            plot_vehicles_map(empty_df)

    @patch('matplotlib.pyplot.savefig')
    def test_plot_accident_history(self, mock_savefig):
        """Test plot_accident_history function"""
        plot_accident_history(self.sample_data)
        
        # Verify the function tried to save the figure
        self.assertTrue(mock_savefig.called)
        
        # Test with DataFrame containing no accident history
        no_accidents_df = self.sample_data.copy()
        no_accidents_df['accident_history'] = 'False'
        plot_accident_history(no_accidents_df)  # Should not raise errors

if __name__ == '__main__':
    unittest.main()