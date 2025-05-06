"""
Feature extraction utilities for fake job detection
"""

import re
import pandas as pd
import numpy as np

class FeatureExtractor:
    """Extract additional features from job postings"""
    
    def __init__(self):
        # Suspicious words that might indicate a fake job
        self.suspicious_words = [
            'unlimited income', 'unlimited earning', 'be your own boss',
            'work from home millionaire', 'get rich', 'earn thousands',
            'opportunity of a lifetime', 'no experience necessary',
            'payment required', 'fee required', 'investment required',
            'money back guarantee', 'multi-level marketing', 'mlm',
            'no risk', 'free money', 'quick money', 'easy money',
            'urgent hiring', 'immediate start', 'apply now',
            'start today', 'weekly pay', 'work from home position'
        ]
        
        # Red flag phrases
        self.red_flag_phrases = [
            'registration fee', 'training fee', 'starter kit',
            'certification fee', 'background check fee',
            'unlimited earning potential', 'make money fast',
            'earn while you sleep', 'financial freedom',
            'secret method', 'proven system', 'exclusive opportunity'
        ]
        
        # Common personal email domains
        self.personal_email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com',
            'outlook.com', 'aol.com', 'mail.com'
        ]
    
    def extract_features(self, job_data):
        """
        Extract numerical features from job data
        
        Args:
            job_data: Dictionary with job posting details
            
        Returns:
            Dictionary with extracted features
        """
        # Get text fields
        title = job_data.get('title', '')
        description = job_data.get('description', '')
        requirements = job_data.get('requirements', '')
        benefits = job_data.get('benefits', '')
        company_profile = job_data.get('company_profile', '')
        
        # Combine text for broader analysis
        combined_text = ' '.join([
            str(title), str(description), str(requirements), str(benefits), str(company_profile)
        ]).lower()
        
        # Extract features
        features = {
            # Text length features
            'title_length': len(str(title)),
            'description_length': len(str(description)),
            'requirements_length': len(str(requirements)),
            'benefits_length': len(str(benefits)),
            'company_profile_length': len(str(company_profile)),
            
            # Suspicious content features
            'suspicious_word_count': self._count_suspicious_words(combined_text),
            'red_flag_phrase_count': self._count_red_flag_phrases(combined_text),
            
            # Email related features
            'has_personal_email': self._has_personal_email(combined_text),
            'email_count': self._count_emails(combined_text),
            
            # Salary related features
            'has_salary': self._has_salary_information(combined_text),
            'has_specific_salary': self._has_specific_salary(combined_text),
            
            # Company related features
            'has_company_info': len(str(company_profile)) > 100,
            'has_company_website': self._has_company_website(combined_text),
            
            # Contact features
            'has_phone_number': self._has_phone_number(combined_text),
            'has_address': self._has_address(combined_text),
            
            # Linguistic features
            'exclamation_count': combined_text.count('!'),
            'all_caps_word_count': self._count_all_caps_words(combined_text),
            
            # Application process features
            'requests_personal_info': self._requests_personal_info(combined_text),
            'mentions_interview': 'interview' in combined_text,
        }
        
        return features
    
    def _count_suspicious_words(self, text):
        """Count occurrences of suspicious words"""
        count = 0
        for word in self.suspicious_words:
            if word in text:
                count += 1
        return count
    
    def _count_red_flag_phrases(self, text):
        """Count occurrences of red flag phrases"""
        count = 0
        for phrase in self.red_flag_phrases:
            if phrase in text:
                count += 1
        return count
    
    def _has_personal_email(self, text):
        """Check if the text contains personal email domains"""
        for domain in self.personal_email_domains:
            if f'@{domain}' in text:
                return 1
        return 0
    
    def _count_emails(self, text):
        """Count email addresses in the text"""
        emails = re.findall(r'[\w.-]+@[\w.-]+\.\w+', text)
        return len(emails)
    
    def _has_salary_information(self, text):
        """Check if the text mentions salary"""
        salary_keywords = ['salary', 'compensation', 'pay', 'wage', 'stipend', 'remuneration']
        for keyword in salary_keywords:
            if keyword in text:
                return 1
        return 0
    
    def _has_specific_salary(self, text):
        """Check if the text contains specific salary amounts"""
        # Look for currency symbols followed by numbers
        currency_patterns = [
            r'\$\s*\d+[\d,.]*',  # $50,000 or $50000 or $ 50,000
            r'\d+\s*k',          # 50k
            r'\d+[\d,.]*\s*per\s*(hour|year|month|week|annum)',  # 50,000 per year
            r'\d+[\d,.]*\s*-\s*\d+[\d,.]*',  # 40,000 - 50,000
        ]
        
        for pattern in currency_patterns:
            if re.search(pattern, text):
                return 1
        return 0
    
    def _has_company_website(self, text):
        """Check if the text contains a company website"""
        # Look for URLs that don't contain personal email domains
        urls = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z0-9-.]+', text)
        if not urls:
            return 0
        
        # Check if any URL is not a personal domain
        for domain in urls:
            if domain.lower() not in [d.split('.')[0] for d in self.personal_email_domains]:
                return 1
        return 0
    
    def _has_phone_number(self, text):
        """Check if the text contains a phone number"""
        phone_patterns = [
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',  # (123) 456-7890
            r'\d{3}[-.]?\d{3}[-.]?\d{4}',    # 123-456-7890 or 1234567890
            r'\+\d{1,3}\s*\d{3}[-.]?\d{3}[-.]?\d{4}'  # +1 123-456-7890
        ]
        
        for pattern in phone_patterns:
            if re.search(pattern, text):
                return 1
        return 0
    
    def _has_address(self, text):
        """Check if the text contains an address"""
        # This is a simplified check for address patterns
        address_patterns = [
            r'\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way)',
            r'(?:Suite|Ste|Unit|Apt)\s+\d+',
            r'\b[A-Z][a-z]+,\s+[A-Z]{2}\s+\d{5}\b'  # City, ST ZIP
        ]
        
        for pattern in address_patterns:
            if re.search(pattern, text):
                return 1
        return 0
    
    def _count_all_caps_words(self, text):
        """Count words in ALL CAPS"""
        words = text.split()
        all_caps_words = [word for word in words if word.isupper() and len(word) > 2]
        return len(all_caps_words)
    
    def _requests_personal_info(self, text):
        """Check if the text requests personal information"""
        personal_info_keywords = [
            'ssn', 'social security', 'bank account', 'credit card',
            'passport', 'driver license', 'driver\'s license', 'identity card',
            'birth certificate', 'date of birth', 'mother\'s maiden name',
            'tax id', 'personal documents'
        ]
        
        for keyword in personal_info_keywords:
            if keyword in text:
                return 1
        return 0