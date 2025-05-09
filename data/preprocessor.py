"""
Data preprocessor for fake job detection
"""

import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources if needed
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt')

class Preprocessor:
    """Preprocessor for text and categorical features"""
    
    def __init__(self):
        # TF-IDF Vectorizer
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            min_df=5,
            max_df=0.5,
            max_features=5000
        )
        
        # One-Hot Encoder
        self.onehot_encoder = OneHotEncoder(
            sparse_output=False,
            handle_unknown='ignore'
        )
        
        # Lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        # Stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Flags to track if encoders have been fitted
        self.tfidf_fitted = False
        self.onehot_fitted = False
        
        # Feature names
        self.tfidf_feature_names = None
        self.onehot_feature_names = None
        self.categorical_columns = None
    
    def preprocess_data(self, df):
        """
        Preprocess the dataset for training
        
        Args:
            df: pandas DataFrame with the dataset
            
        Returns:
            TF-IDF features, one-hot encoded features, target labels, and feature names
        """
        # Extract text features
        text_features = self._extract_text_features(df)
        
        # Combine text features
        combined_text = text_features['combined_text']
        
        # Extract categorical features
        categorical_features = self._extract_categorical_features(df)
        
        # Get target variable
        y = df['fraudulent'].values
        
        # Fit and transform TF-IDF features
        X_tfidf = self.tfidf_vectorizer.fit_transform(combined_text)
        self.tfidf_fitted = True
        self.tfidf_feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # Fit and transform categorical features
        if categorical_features is not None:
            X_onehot = self.onehot_encoder.fit_transform(categorical_features)
            self.onehot_fitted = True
            self.onehot_feature_names = self.onehot_encoder.get_feature_names_out()
            self.categorical_columns = categorical_features.columns.tolist()
        else:
            X_onehot = None
            self.onehot_feature_names = []
            self.categorical_columns = []
        
        # Combine feature names
        feature_names = {
            'tfidf': self.tfidf_feature_names,
            'onehot': self.onehot_feature_names,
            'categorical': self.categorical_columns
        }
        
        return X_tfidf, X_onehot, y, feature_names
    
    def preprocess_job_data(self, job_data):
        """
        Preprocess a job posting for prediction
        
        Args:
            job_data: Dictionary with job posting details
            
        Returns:
            Dictionary with processed features
        """
        if not self.tfidf_fitted or not self.onehot_fitted:
            raise ValueError("Preprocessor has not been fitted yet.")
        
        # Extract text features
        text_features = self._extract_text_from_job_data(job_data)
        
        # Extract categorical features
        categorical_features = self._extract_categorical_from_job_data(job_data)
        
        # Transform TF-IDF features
        tfidf_features = self.tfidf_vectorizer.transform([text_features['combined_text']])
        
        # Transform categorical features
        if self.categorical_columns and categorical_features is not None:
            # Ensure all expected columns are present
            for col in self.categorical_columns:
                if col not in categorical_features:
                    categorical_features[col] = 'Unknown'
            
            # Reorder columns to match the order used during training
            categorical_features = categorical_features[self.categorical_columns]
            
            # Transform to one-hot encoding
            onehot_features = self.onehot_encoder.transform(categorical_features.values.reshape(1, -1))
        else:
            # Create an empty array with the correct shape if no categorical features
            onehot_features = np.zeros((1, len(self.onehot_feature_names)))
        
        return {
            'tfidf': tfidf_features,
            'onehot': onehot_features,
            'text': text_features,
            'categorical': categorical_features
        }
    
    def _extract_text_features(self, df):
        """
        Extract and clean text features from the DataFrame
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dictionary with processed text features
        """
        # Define text columns to use
        text_columns = ['title', 'company_profile', 'description', 'requirements', 'benefits']
        text_columns = [col for col in text_columns if col in df.columns]
        
        # Clean and preprocess text columns
        processed_columns = {}
        for col in text_columns:
            processed_columns[col] = df[col].apply(self._clean_text)
        
        # Combine all text columns
        combined_text = df[text_columns].fillna('').apply(
            lambda row: ' '.join([self._clean_text(str(row[col])) for col in text_columns]),
            axis=1
        )
        
        # Add combined text to processed columns
        processed_columns['combined_text'] = combined_text
        
        return processed_columns
    
    def _extract_categorical_features(self, df):
        """
        Extract categorical features from the DataFrame
        
        Args:
            df: pandas DataFrame
            
        Returns:
            pandas DataFrame with categorical features
        """
        # Define categorical columns to use
        categorical_columns = ['employment_type', 'required_experience', 'industry', 'function', 'location']
        categorical_columns = [col for col in categorical_columns if col in df.columns]
        
        if not categorical_columns:
            return None
        
        # Extract categorical columns
        categorical_features = df[categorical_columns].copy()
        
        # Fill missing values with 'Unknown'
        categorical_features = categorical_features.fillna('Unknown')
        
        return categorical_features
    
    def _extract_text_from_job_data(self, job_data):
        """
        Extract and clean text features from job data dictionary
        
        Args:
            job_data: Dictionary with job posting details
            
        Returns:
            Dictionary with processed text features
        """
        # Define text fields to use
        text_fields = ['title', 'company_profile', 'description', 'requirements', 'benefits']
        
        # Clean and preprocess text fields
        processed_fields = {}
        for field in text_fields:
            text = job_data.get(field, '')
            processed_fields[field] = self._clean_text(text)
        
        # Combine all text fields
        combined_text = ' '.join([processed_fields[field] for field in text_fields if field in processed_fields])
        
        # Add combined text to processed fields
        processed_fields['combined_text'] = combined_text
        
        return processed_fields
    
    def _extract_categorical_from_job_data(self, job_data):
        """
        Extract categorical features from job data dictionary
        
        Args:
            job_data: Dictionary with job posting details
            
        Returns:
            pandas DataFrame with categorical features
        """
        # Define categorical fields to use
        categorical_fields = ['employment_type', 'required_experience', 'industry', 'function']
        
        # Extract categorical fields
        categorical_data = {}
        for field in categorical_fields:
            categorical_data[field] = job_data.get(field, 'Unknown')
        
        # Convert to DataFrame
        categorical_features = pd.DataFrame([categorical_data])
        
        return categorical_features
    
    def _clean_text(self, text):
        """
        Clean and normalize text
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ''
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' ', text)
        
        # Remove non-alphanumeric characters
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Normalize white spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Lemmatize words
        words = nltk.word_tokenize(text)
        lemmatized_words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        
        return ' '.join(lemmatized_words)