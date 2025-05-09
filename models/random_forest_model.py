"""
Random Forest model for fake job detection
"""

import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from imblearn.over_sampling import SMOTE

class RandomForestModel:
    """Random Forest model with one-hot encoding and SMOTE"""
    
    def __init__(self):
        self.model = RandomForestClassifier()
        self.is_trained = False
        
    def train(self, X_train, y_train, apply_smote=True):
        """
        Train the Random Forest model
        
        Args:
            X_train: One-hot encoded features for training
            y_train: Target labels
            apply_smote: Whether to apply SMOTE for handling class imbalance
        """
        if apply_smote:
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
            self.model.fit(X_resampled, y_resampled)
        else:
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
    
    def get_feature_importance(self):
        """Get feature importance scores"""
        if not self.is_trained:
            raise ValueError("Model has not been trained yet.")
        return self.model.feature_importances_
    
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
    
    def save(self, path='models/rf_model.pkl'):
        """Save model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model.")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
            
    def load(self, path='models/rf_model.pkl'):
        """Load model from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
            
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
            
        self.is_trained = True

def train_and_save_model(X_train, y_train, X_test, y_test, feature_names=None, model_path='models/rf_model.pkl'):
    """Train and save a Random Forest model"""
    model = RandomForestModel()
    model.train(X_train, y_train, apply_smote=True)
    
    # Evaluate the model
    evaluation = model.evaluate(X_test, y_test)
    print("Random Forest Model Evaluation:")
    print(f"Accuracy: {evaluation['accuracy']:.4f}")
    print(f"Precision: {evaluation['precision']:.4f}")
    print(f"Recall: {evaluation['recall']:.4f}")
    print(f"F1 Score: {evaluation['f1']:.4f}")
    print("\nClassification Report:")
    print(evaluation['report'])
    
    # Print feature importance if feature names are provided
    if feature_names is not None:
        importances = model.get_feature_importance()
        indices = np.argsort(importances)[::-1]
        
        print("\nFeature Importance:")
        for i in range(min(20, len(indices))):  # Print top 20 features
            print(f"{feature_names[indices[i]]}: {importances[indices[i]]:.4f}")
    
    # Save the model
    model.save(model_path)
    print(f"Model saved to {model_path}")
    
    return model