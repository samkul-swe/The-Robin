"""
Data loader for fake job detection
"""

import os
import pandas as pd
import numpy as np

class DataLoader:
    """Data loader for loading and processing the dataset"""
    
    def load_data(self, file_path):
        """
        Load data from a CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            pandas DataFrame with the loaded data
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")
            
        # Load the data
        df = pd.read_csv(file_path)
        
        # Check if required columns exist
        required_columns = ['fraudulent']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in the dataset.")
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        return df
    
    def _handle_missing_values(self, df):
        """
        Handle missing values in the DataFrame
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with missing values handled
        """
        # Fill missing values in text columns with empty string
        text_columns = ['title', 'company_profile', 'description', 'requirements', 'benefits']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        
        # Fill missing values in categorical columns with 'Unknown'
        categorical_columns = ['employment_type', 'required_experience', 'required_education', 'industry', 'function']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')
        
        # Fill missing values in location columns
        if 'location' in df.columns:
            df['location'] = df['location'].fillna('Unknown')
        
        # Fill missing values in salary columns
        salary_columns = ['salary_range', 'salary']
        for col in salary_columns:
            if col in df.columns:
                df[col] = df[col].fillna('Not specified')
        
        return df