"""
Ensemble model for fake job detection combining multiple models
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from models.logistic_regression_model import LogisticRegressionModel
from models.mlp_model import MLPModel
from models.random_forest_model import RandomForestModel
from models.svm_model import SVMModel
from data.data_loader import DataLoader
from data.preprocessor import Preprocessor
from utils.reason_generator import ReasonGenerator

class EnsembleModel:
    """Ensemble model combining predictions from multiple models"""
    
    def __init__(self):
        self.models = {
            'logistic_regression': LogisticRegressionModel(),
            'mlp': MLPModel(),
            'random_forest': RandomForestModel(),
            'svm': SVMModel()
        }
        
        # Default weights for each model
        self.weights = {
            'logistic_regression': 0.25,
            'mlp': 0.25,
            'random_forest': 0.25,
            'svm': 0.25
        }
        
        self.preprocessor = None
        self.reason_generator = ReasonGenerator()
        self.is_trained = False
        
    def set_weights(self, weights):
        """
        Set custom weights for the models
        
        Args:
            weights: Dictionary of model weights
        """
        if weights and isinstance(weights, dict):
            self.weights = {**self.weights, **weights}
            
            # Normalize weights to ensure they sum to 1
            total = sum(self.weights.values())
            if total != 1:
                for model in self.weights:
                    self.weights[model] /= total
    
    def train(self, data_path):
        """
        Train all models in the ensemble
        
        Args:
            data_path: Path to the dataset CSV file
        """
        # Load and preprocess the data
        data_loader = DataLoader()
        df = data_loader.load_data(data_path)
        
        # Initialize the preprocessor
        self.preprocessor = Preprocessor()
        
        # Preprocess the data
        X_tfidf, X_onehot, y, feature_names = self.preprocessor.preprocess_data(df)
        
        # Split the data
        X_tfidf_train, X_tfidf_test, X_onehot_train, X_onehot_test, y_train, y_test = train_test_split(
            X_tfidf, X_onehot, y, test_size=0.2, random_state=42
        )
        
        # Train each model with its optimal preprocessing
        print("Training Logistic Regression model...")
        self.models['logistic_regression'].train(X_tfidf_train, y_train, apply_smote=True)
        
        print("Training MLP model...")
        self.models['mlp'].train(X_tfidf_train, y_train)  # No SMOTE for MLP
        
        print("Training Random Forest model...")
        self.models['random_forest'].train(X_onehot_train, y_train, apply_smote=True)
        
        print("Training SVM model...")
        self.models['svm'].train(X_tfidf_train, y_train, apply_smote=True)
        
        # Evaluate each model
        print("\nEvaluating individual models:")
        for name, model in self.models.items():
            X_test = X_tfidf_test if name != 'random_forest' else X_onehot_test
            evaluation = model.evaluate(X_test, y_test)
            print(f"\n{name.upper()} Model:")
            print(f"Accuracy: {evaluation['accuracy']:.4f}")
            print(f"Precision: {evaluation['precision']:.4f}")
            print(f"Recall: {evaluation['recall']:.4f}")
            print(f"F1 Score: {evaluation['f1']:.4f}")
        
        # Save the models
        self.save_models()
        
        # Save the preprocessor
        self.save_preprocessor()
        
        self.is_trained = True
        
    def predict(self, job_data):
        """
        Predict if a job posting is fake
        
        Args:
            job_data: Dictionary with job posting details
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_trained:
            self.load_models()
            self.load_preprocessor()
            
        # Preprocess the job data
        features = self.preprocessor.preprocess_job_data(job_data)
        
        # Get predictions from each model
        lr_prob = self.models['logistic_regression'].predict_proba(features['tfidf'])[0][1]
        mlp_prob = self.models['mlp'].predict_proba(features['tfidf'])[0][1]
        rf_prob = self.models['random_forest'].predict_proba(features['onehot'])[0][1]
        svm_prob = self.models['svm'].predict_proba(features['tfidf'])[0][1]
        
        # Calculate weighted ensemble probability
        ensemble_prob = (
            self.weights['logistic_regression'] * lr_prob +
            self.weights['mlp'] * mlp_prob +
            self.weights['random_forest'] * rf_prob +
            self.weights['svm'] * svm_prob
        )
        
        # Calculate confidence score (0-100)
        confidence_score = ensemble_prob * 100
        
        # Generate reasons for the prediction
        reasons = self.reason_generator.generate_reasons(
            job_data,
            confidence_score,
            {
                'logistic_regression': lr_prob,
                'mlp': mlp_prob,
                'random_forest': rf_prob,
                'svm': svm_prob
            }
        )
        
        # Return the prediction results
        return {
            'is_fake': ensemble_prob > 0.5,
            'confidence_score': confidence_score,
            'reasons': reasons,
            'model_probabilities': {
                'logistic_regression': lr_prob,
                'mlp': mlp_prob,
                'random_forest': rf_prob,
                'svm': svm_prob
            }
        }
    
    def save_models(self, base_path='models'):
        """Save all models to disk"""
        os.makedirs(base_path, exist_ok=True)
        
        for name, model in self.models.items():
            model_path = os.path.join(base_path, f"{name}_model.pkl")
            model.save(model_path)
            
        # Save weights
        weights_path = os.path.join(base_path, "ensemble_weights.pkl")
        with open(weights_path, 'wb') as f:
            pickle.dump(self.weights, f)
    
    def load_models(self, base_path='models'):
        """Load all models from disk"""
        for name, model in self.models.items():
            model_path = os.path.join(base_path, f"{name}_model.pkl")
            try:
                model.load(model_path)
            except FileNotFoundError:
                print(f"Warning: Model file not found: {model_path}")
                continue
        
        # Load weights if available
        weights_path = os.path.join(base_path, "ensemble_weights.pkl")
        if os.path.exists(weights_path):
            with open(weights_path, 'rb') as f:
                self.weights = pickle.load(f)
                
        self.is_trained = True
    
    def save_preprocessor(self, path='models/preprocessor.pkl'):
        """Save preprocessor to disk"""
        if self.preprocessor is None:
            raise ValueError("Preprocessor has not been initialized.")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.preprocessor, f)
    
    def load_preprocessor(self, path='models/preprocessor.pkl'):
        """Load preprocessor from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Preprocessor file not found: {path}")
            
        with open(path, 'rb') as f:
            self.preprocessor = pickle.load(f)

def train_ensemble_model(data_path):
    """Train the ensemble model"""
    ensemble = EnsembleModel()
    ensemble.train(data_path)
    return ensemble