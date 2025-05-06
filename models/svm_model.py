"""
SVM model for fake job detection
"""

import os
import pickle
import numpy as np
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from imblearn.over_sampling import SMOTE

class SVMModel:
    """SVM model with SMOTE and TF-IDF"""
    
    def __init__(self):
        self.model = SVC(
            probability=True,
            random_state=42,
            class_weight='balanced'
        )
        self.is_trained = False
        
    def train(self, X_train, y_train, apply_smote=True):
        """
        Train the SVM model
        
        Args:
            X_train: TF-IDF features for training
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
    
    def save(self, path='models/svm_model.pkl'):
        """Save model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model.")
            
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
            
    def load(self, path='models/svm_model.pkl'):
        """Load model from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
            
        with open(path, 'rb') as f:
            self.model = pickle.load(f)
            
        self.is_trained = True

def train_and_save_model(X_train, y_train, X_test, y_test, model_path='models/svm_model.pkl'):
    """Train and save an SVM model"""
    model = SVMModel()
    model.train(X_train, y_train, apply_smote=True)
    
    # Evaluate the model
    evaluation = model.evaluate(X_test, y_test)
    print("SVM Model Evaluation:")
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