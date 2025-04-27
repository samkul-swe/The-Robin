import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import joblib

###############################################################################
# Random Forest Classifier
###############################################################################

class FakeJobDetectorRF:
    def __init__(self):
        """
        Initialize the Fake Job Detector with Random Forest classifier.
        Based on your research, Random Forest performs best with one-hot encoding + SMOTE.
        """
        # Define the pipeline with optimal parameters
        self.pipeline = Pipeline([
            ('vectorizer', CountVectorizer(binary=True, max_features=5000)),  # One-hot encoding
            ('clf', RandomForestClassifier(
                n_estimators=100,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1  # Use all available cores
            ))
        ])
        
        self.smote = SMOTE(random_state=42)
        self.model_trained = False
        
    def preprocess_text(self, job_posting):
        """
        Extract and combine text features from job posting.
        
        Args:
            job_posting (dict): Dictionary containing job posting data
                
        Returns:
            str: Combined text for processing
        """
        text_fields = ['title', 'description', 'requirements', 'benefits', 'company_profile']
        combined_text = ""
        
        for field in text_fields:
            if field in job_posting and job_posting[field]:
                combined_text += " " + str(job_posting[field])
                
        return combined_text.lower()
    
    def extract_features(self, job_postings):
        """
        Extract features from job postings.
        
        Args:
            job_postings (list): List of job posting dictionaries
                
        Returns:
            list: List of text features for each job posting
        """
        return [self.preprocess_text(job) for job in job_postings]
    
    def train(self, job_postings, labels):
        """
        Train the model with SMOTE applied to the training data.
        
        Args:
            job_postings (list): List of job posting dictionaries
            labels (list): Binary labels (1 for fraudulent, 0 for legitimate)
                
        Returns:
            self: Trained model
        """
        X_text = self.extract_features(job_postings)
        y = np.array(labels)
        
        # Transform the text to binary features before applying SMOTE
        X_features = self.pipeline.named_steps['vectorizer'].fit_transform(X_text)
        
        # Apply SMOTE to balance classes
        X_resampled, y_resampled = self.smote.fit_resample(X_features, y)
        
        # Train the classifier on the resampled data
        self.pipeline.named_steps['clf'].fit(X_resampled, y_resampled)
        
        self.model_trained = True
        return self
    
    def predict(self, job_posting):
        """
        Predict if a job posting is fraudulent.
        
        Args:
            job_posting (dict): Job posting to classify
                
        Returns:
            dict: Prediction results with probability and risk level
        """
        if not self.model_trained:
            raise ValueError("Model has not been trained yet!")
        
        X_text = [self.preprocess_text(job_posting)]
        
        # Get probability of fraudulent class
        fraud_probability = self.pipeline.predict_proba(X_text)[0][1]
        
        # Determine risk level
        if fraud_probability < 0.3:
            risk_level = "low"
            color = "green"
        elif fraud_probability < 0.7:
            risk_level = "medium"
            color = "orange"
        else:
            risk_level = "high"
            color = "red"
        
        return {
            "fraud_probability": float(fraud_probability),
            "risk_level": risk_level,
            "color_indicator": color,
            "is_fraudulent": fraud_probability > 0.5
        }
    
    def get_feature_importance(self, job_posting, top_n=5):
        """
        Get the most important features for this prediction.
        
        Args:
            job_posting (dict): Job posting to analyze
            top_n (int): Number of top features to return
                
        Returns:
            list: Top features and their importance scores
        """
        if not self.model_trained:
            raise ValueError("Model has not been trained yet!")
            
        # Get feature names
        feature_names = self.pipeline.named_steps['vectorizer'].get_feature_names_out()
        
        # Get feature importances
        importances = self.pipeline.named_steps['clf'].feature_importances_
        
        # Sort features by importance
        indices = np.argsort(importances)[::-1]
        
        # Get top features
        top_features = []
        for i in range(min(top_n, len(indices))):
            idx = indices[i]
            if idx < len(feature_names):  # Safety check
                top_features.append({
                    "feature": feature_names[idx],
                    "importance": float(importances[idx])
                })
        
        return top_features
    
    def explain_prediction(self, job_posting):
        """
        Provide an explanation of why the job posting might be fraudulent.
        
        Args:
            job_posting (dict): Job posting to analyze
                
        Returns:
            list: Explanation reasons sorted by importance
        """
        # Get basic prediction first
        prediction = self.predict(job_posting)
        
        # If it's not fraudulent, no need for detailed explanation
        if not prediction['is_fraudulent']:
            return ["This job posting appears to be legitimate."]
        
        # Common suspicious patterns to check for
        reasons = []
        
        # Check for suspicious text patterns
        text = self.preprocess_text(job_posting)
        
        # Check for overly generous salary/benefits
        salary_keywords = ["excellent salary", "top salary", "unbelievable pay", "lucrative", 
                           "competitive salary", "high paying"]
        if any(keyword in text for keyword in salary_keywords):
            reasons.append("Suspicious salary claims that seem too good to be true")
        
        # Check for urgency or pressure tactics
        urgency_keywords = ["immediate start", "urgent", "apply now", "don't delay", 
                            "immediate opening", "apply today", "positions filling fast"]
        if any(keyword in text for keyword in urgency_keywords):
            reasons.append("Creates false urgency to pressure quick applications")
        
        # Check for vague job description
        if 'description' in job_posting and job_posting['description']:
            word_count = len(job_posting['description'].split())
            if word_count < 100:
                reasons.append("Unusually short or vague job description")
        
        # Check for grammar/spelling errors
        error_indicators = ["ur ", " u ", "4 u", "thankyou", "ur experience", "ur resume"]
        if any(indicator in text for indicator in error_indicators):
            reasons.append("Contains unprofessional language or grammar errors")
        
        # Check for unusual contact methods
        contact_keywords = ["whatsapp", "telegram", "personal email", "text us", 
                           "message us", "personal phone"]
        if any(keyword in text for keyword in contact_keywords):
            reasons.append("Requests contact through unusual channels outside the job platform")
        
        # Check for requests for personal/financial information
        sensitive_keywords = ["bank details", "ssn", "social security", "passport", 
                             "identity card", "credit card", "payment details"]
        if any(keyword in text for keyword in sensitive_keywords):
            reasons.append("Requests sensitive personal or financial information")
        
        # Random Forest-specific explanations
        try:
            top_features = self.get_feature_importance(job_posting)
            for feature in top_features:
                if feature["feature"] in text:
                    reasons.append(f"Contains suspicious term: '{feature['feature']}'")
        except:
            pass
        
        # If we couldn't find specific reasons, add a generic explanation
        if not reasons:
            reasons.append("Multiple small inconsistencies that together indicate a suspicious posting")
            reasons.append("Matches patterns seen in previously identified fraudulent job listings")
        
        return reasons
    
    def save_model(self, filepath):
        """
        Save the trained model to disk.
        
        Args:
            filepath (str): Path to save the model
        """
        joblib.dump(self, filepath)
    
    @classmethod
    def load_model(cls, filepath):
        """
        Load a trained model from disk.
        
        Args:
            filepath (str): Path to the saved model
                
        Returns:
            FakeJobDetectorRF: Loaded model
        """
        return joblib.load(filepath)