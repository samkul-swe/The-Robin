import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import joblib
import re
import string

###############################################################################
# Ensemble Wrapper
###############################################################################

class FakeJobDetectorEnsemble:
    def __init__(self):
        """
        Initialize the ensemble detector that uses multiple models
        for more robust fake job detection.
        """
        self.models = {
            'logistic': None,
            'mlp': None,
            'rf': None,
            'svm': None
        }
        
    def load_models(self, model_paths):
        """
        Load all pre-trained models.
        
        Args:
            model_paths (dict): Dictionary mapping model names to file paths
        """
        if 'logistic' in model_paths:
            self.models['logistic'] = joblib.load(model_paths['logistic'])
        
        if 'mlp' in model_paths:
            self.models['mlp'] = joblib.load(model_paths['mlp'])
            
        if 'rf' in model_paths:
            self.models['rf'] = joblib.load(model_paths['rf'])
            
        if 'svm' in model_paths:
            self.models['svm'] = joblib.load(model_paths['svm'])
    
    def predict(self, job_posting):
        """
        Get predictions from all models and provide a confidence analysis.
        
        Args:
            job_posting (dict): Job posting to analyze
                
        Returns:
            dict: Comprehensive analysis with all model predictions
        """
        results = {}
        
        # Get predictions from each model
        for name, model in self.models.items():
            if model is not None:
                results[name] = model.predict(job_posting)
        
        # Calculate consensus and confidence
        probabilities = [model_result['fraud_probability'] for model_result in results.values()]
        
        # Overall fraud probability (average of models)
        avg_probability = sum(probabilities) / len(probabilities)
        
        # Consensus (how many models agree it's fraudulent)
        fraud_votes = sum(1 for p in probabilities if p > 0.5)
        consensus_percent = (fraud_votes / len(probabilities)) * 100
        
        # Confidence (how close the models are to agreement)
        variance = sum((p - avg_probability) ** 2 for p in probabilities) / len(probabilities)
        confidence = 1.0 - min(1.0, variance * 4)  # Scale variance to a 0-1 confidence
        
        # Overall risk level
        if avg_probability < 0.3:
            risk_level = "low"
            color = "green"
        elif avg_probability < 0.7:
            risk_level = "medium"
            color = "orange"
        else:
            risk_level = "high"
            color = "red"
            
        # Get feature importance from RF if available
        top_features = []
        if 'rf' in self.models and self.models['rf'] is not None:
            try:
                top_features = self.models['rf'].get_feature_importance(job_posting)
            except:
                pass
                
        return {
            "individual_predictions": results,
            "consensus": {
                "fraud_probability": float(avg_probability),
                "agreement_percent": float(consensus_percent),
                "confidence": float(confidence),
                "risk_level": risk_level,
                "color_indicator": color,
                "is_fraudulent": avg_probability > 0.5
            },
            "top_fraud_indicators": top_features
        }
    
    def explain_prediction(self, job_posting):
        """
        Provide a comprehensive explanation of why the job posting might be fraudulent.
        
        Args:
            job_posting (dict): Job posting to analyze
                
        Returns:
            dict: Consolidated explanation with reasons from all models
        """
        # Get consensus prediction first
        prediction = self.predict(job_posting)
        
        # If it's not fraudulent, no need for detailed explanation
        if not prediction['consensus']['is_fraudulent']:
            return {
                "is_fraudulent": False,
                "explanation": ["This job posting appears to be legitimate."]
            }
        
        # Get explanations from each model
        all_reasons = []
        for name, model in self.models.items():
            if model is not None:
                model_reasons = model.explain_prediction(job_posting)
                all_reasons.extend(model_reasons)
        
        # Deduplicate reasons (some models might identify the same issues)
        unique_reasons = []
        for reason in all_reasons:
            # Simple deduplication - could be improved with semantic similarity
            if reason not in unique_reasons:
                unique_reasons.append(reason)
        
        # Sort reasons by frequency in the original list (more models agree = more important)
        reason_counts = {reason: all_reasons.count(reason) for reason in unique_reasons}
        sorted_reasons = sorted(unique_reasons, key=lambda r: reason_counts[r], reverse=True)
        
        # Add confidence context
        confidence_explanation = ""
        if prediction['consensus']['confidence'] > 0.8:
            confidence_explanation = "All detection models strongly agree this posting is suspicious."
        elif prediction['consensus']['confidence'] > 0.5:
            confidence_explanation = "Most detection models agree this posting contains fraud indicators."
        else:
            confidence_explanation = "Some fraud indicators were detected, but models don't fully agree."
        
        return {
            "is_fraudulent": True,
            "confidence": prediction['consensus']['confidence'],
            "confidence_explanation": confidence_explanation,
            "reasons": sorted_reasons[:5]  # Top 5 reasons
        }
    
    def save_models(self, directory):
        """
        Save all trained models to a directory.
        
        Args:
            directory (str): Directory to save models
        """
        import os
        os.makedirs(directory, exist_ok=True)
        
        for name, model in self.models.items():
            if model is not None:
                model.save_model(os.path.join(directory, f"{name}_model.joblib"))
    
    @classmethod
    def load_ensemble(cls, directory):
        """
        Load a complete ensemble from a directory.
        
        Args:
            directory (str): Directory containing saved models
                
        Returns:
            FakeJobDetectorEnsemble: Loaded ensemble
        """
        import os
        
        ensemble = cls()
        model_paths = {}
        
        for name in ['logistic', 'mlp', 'rf', 'svm']:
            path = os.path.join(directory, f"{name}_model.joblib")
            if os.path.exists(path):
                model_paths[name] = path
        
        ensemble.load_models(model_paths)
        return ensemble