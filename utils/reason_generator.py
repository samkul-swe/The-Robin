"""
Reason generator for fake job detection
"""

import re
import logging

logger = logging.getLogger(__name__)

class ReasonGenerator:
    """Generate human-readable reasons for job fraud prediction"""
    
    def __init__(self):
        # Define suspicious patterns and their explanations
        self.suspicious_patterns = {
            # Title patterns
            'title_patterns': {
                'unlimited income': 'Job title promises "unlimited income" (common in scams)',
                'opportunity of a lifetime': 'Job titled as "opportunity of a lifetime" (suspicious phrasing)',
                'urgent': 'Urgency in job title creates pressure to apply quickly (common scam tactic)',
                'no experience': 'Job title indicates "no experience" needed despite high pay',
                'immediate start': 'Job title emphasizes "immediate start" (creates artificial urgency)'
            },
            
            # Description patterns
            'description_patterns': {
                'fee': 'Requests payment or fees from applicants',
                'investment': 'Asks for an "investment" or startup costs',
                'training fee': 'Requires payment for training materials',
                'background check fee': 'Charges for background check (legitimate employers cover this)',
                'registration fee': 'Requests a registration fee to apply',
                'starter kit': 'Requires purchase of a "starter kit" to begin work',
                'certification fee': 'Charges for job-specific certifications',
                'unlimited earning': 'Promises "unlimited earning potential" (unrealistic)',
                'unlimited income': 'Claims "unlimited income" is possible (unrealistic)',
                'quick money': 'Promises "quick money" or fast wealth',
                'earn thousands': 'Guarantees unrealistic earnings like "thousands per week"',
                'millionaire': 'Suggests you can become a millionaire quickly',
                'easy money': 'Promotes "easy money" with minimal effort',
                'work from home millionaire': 'Claims you can become rich working from home',
                'be your own boss': 'Emphasizes "be your own boss" without business details',
                'no risk': 'Claims there is "no risk" involved (unrealistic)',
                'money back guarantee': 'Offers "money back guarantee" (unusual for legitimate jobs)',
                'secret': 'Mentions a "secret" method or system for making money',
                'financial freedom': 'Promises vague "financial freedom" instead of concrete salary'
            },
            
            # Company red flags
            'company_patterns': {
                'no company name': 'Job posting doesn\'t include a company name',
                'vague company': 'Company information is unusually vague or generic',
                'no website': 'No company website provided for verification',
                'no address': 'No physical address for the company is provided',
                'no phone': 'No company phone number provided'
            },
            
            # Contact information red flags
            'contact_patterns': {
                'personal email': 'Uses personal email (Gmail, Yahoo, etc.) instead of company domain',
                'generic email': 'Uses generic email address not linked to a company',
                'multiple emails': 'Lists multiple different email addresses for contact',
                'no contact info': 'Lacks proper contact information',
                'unusual contact method': 'Requests contact through unusual channels',
                'whatsapp only': 'Only provides WhatsApp or messaging apps for contact'
            },
            
            # Application process red flags
            'application_patterns': {
                'personal info upfront': 'Requests excessive personal information before interview',
                'ssn': 'Asks for Social Security Number before formal hiring',
                'bank account': 'Requests bank account details during application process',
                'credit card': 'Asks for credit card information',
                'financial info': 'Solicits financial information prematurely',
                'personal documents': 'Requests copies of personal documents before job offer',
                'immediate job offer': 'Offers job immediately without proper interview process',
                'no interview': 'No formal interview process mentioned'
            }
        }
        
        # Personal email domains
        self.personal_email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 
            'outlook.com', 'aol.com', 'mail.com'
        ]
    
    def generate_reasons(self, job_data, confidence_score, model_probabilities=None):
        """
        Generate human-readable reasons for why a job posting may be fake
        
        Args:
            job_data: Dictionary with job posting details
            confidence_score: Confidence score from the ensemble model (0-100)
            model_probabilities: Dictionary with individual model probabilities
            
        Returns:
            List of reasons why the job posting may be fake
        """
        reasons = []
        
        try:
            # Only generate detailed reasons if confidence score is significant
            if confidence_score < 25:
                reasons.append('No significant warning signs detected.')
                return reasons
            
            # Check title for suspicious patterns
            title = job_data.get('title', '').lower()
            for pattern, explanation in self.suspicious_patterns['title_patterns'].items():
                if pattern in title:
                    reasons.append(explanation)
            
            # Check description for suspicious patterns
            description = job_data.get('description', '').lower()
            for pattern, explanation in self.suspicious_patterns['description_patterns'].items():
                if pattern in description:
                    reasons.append(explanation)
            
            # Check company information
            if not job_data.get('company') or len(str(job_data.get('company', ''))) < 2:
                reasons.append('Company name is missing or unusually vague.')
            
            if not job_data.get('company_profile') or len(str(job_data.get('company_profile', ''))) < 100:
                reasons.append('Posting lacks specific company information or history.')
            
            # Check contact information
            contact_info = job_data.get('contact_info', {})
            emails = contact_info.get('emails', [])
            
            # Check for personal email domains
            for email in emails:
                for domain in self.personal_email_domains:
                    if email.lower().endswith('@' + domain):
                        reasons.append('Uses personal email domain instead of company email.')
                        break
            
            # Check if multiple email addresses
            if len(emails) > 1:
                reasons.append('Lists multiple different email addresses for contact.')
            
            # Check salary information
            if 'salary' not in description.lower():
                reasons.append('No salary information provided.')
            
            # Add reasons based on model-specific signals
            if model_probabilities:
                self._add_model_specific_reasons(model_probabilities, reasons)
            
            # If we still have no reasons but high confidence, add a generic reason
            if not reasons and confidence_score > 50:
                reasons.append('Multiple suspicious elements detected in this posting.')
            
            # Limit to top reasons if there are too many
            if len(reasons) > 10:
                reasons = reasons[:10]
            
            return reasons
            
        except Exception as e:
            logger.error(f"Error generating reasons: {str(e)}")
            if confidence_score > 50:
                return ['This job posting contains several red flags common in fraudulent listings.']
            else:
                return ['No specific warning signs identified.']
    
    def _add_model_specific_reasons(self, model_probabilities, reasons):
        """Add reasons based on which models contributed most to the prediction"""
        
        # If Logistic Regression has high confidence (text-based model)
        if model_probabilities.get('logistic_regression', 0) > 0.8:
            reasons.append('Text analysis shows language patterns common in fraudulent listings.')
        
        # If Random Forest has high confidence (categorical features)
        if model_probabilities.get('random_forest', 0) > 0.8:
            reasons.append('Job characteristics match known patterns of fake job postings.')
        
        # If most models agree with high confidence
        high_confidence_count = sum(1 for prob in model_probabilities.values() if prob > 0.7)
        if high_confidence_count >= 3:
            reasons.append('Multiple detection methods flagged this posting as suspicious.')