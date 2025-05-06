"""
MLP (Multi-Layer Perceptron) model for fake job detection
"""

import os
import pickle
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

class MLPModel:
    """MLP model with TF-IDF (no SMOTE)"""
    
    def __init__(self):
        self.model = MLPClassifier(
            hidden_layer_sizes=(100, 50),
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.1
        )
        self.is_trained = False
        
    def train(self, X_train, y_train):
        """
        Train the MLP model
        
        Args:
            X_train: TF-IDF features for training
            y_train: Target labels
        """
        # MLP works best without SMOTE
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
    def predict(self, X):
        """Predict class labels"""
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict(X)
    
    def predict_proba(self, X):
        """Predict class probabilities"""
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict_proba(X)
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance on test data"""
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
            
        y_pred = self.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')
        
        # Generate classification report
        report = classification_report(y_test, y_pred)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'report': report
        }
    
    def save(self, path='models/mlp_model.pkl'):
        """Save model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model.")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
            
    def load(self, path='models/mlp_model.pkl'):
        """Load model from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
            
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
            
        self.is_trained = True

def train_and_save_model(X_train, y_train, X_test, y_test, model_path='models/mlp_model.pkl'):
    """Train and save an MLP model"""
    model = MLPModel()
    model.train(X_train, y_train)
    
    # Evaluate the model
    evaluation = model.evaluate(X_test, y_test)
    print("MLP Model Evaluation:")
    print(f"Accuracy: {evaluation['accuracy']:.4f}")
    print(f"Precision: {evaluation['precision']:.4f}")
    print(f"Recall: {evaluation['recall']:.4f}")
    print(f"F1 Score: {evaluation['f1']:.4f}")
    print("\nClassification Report:")
    print(evaluation['report'])
    
    # Save the model
    model.save(model_path)
    print(f"Model saved to {model_path}")
    
    return model