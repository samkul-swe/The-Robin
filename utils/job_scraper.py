"""
Job scraper utilities for fake job detection
"""

import re
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class JobScraper:
    """Scrape job postings from various job boards"""
    
    def __init__(self):
        self.job_board_selectors = {
            # Indeed
            'indeed.com': {
                'title': '.jobsearch-JobInfoHeader-title',
                'company': '.jobsearch-InlineCompanyRating-companyName',
                'location': '.jobsearch-JobInfoHeader-subtitle .jobsearch-JobInfoHeader-locationName',
                'description': '#jobDescriptionText',
                'company_profile': '.jobsearch-CompanyReview',
                'job_type': '.jobsearch-JobMetadataHeader-item'
            },
            
            # LinkedIn
            'linkedin.com': {
                'title': '.top-card-layout__title',
                'company': '.topcard__org-name-link',
                'location': '.topcard__flavor--bullet',
                'description': '.description__text',
                'company_profile': '.topcard__company-info',
                'job_type': '.job-criteria__item--type .job-criteria__text'
            },
            
            # Monster
            'monster.com': {
                'title': '.job-title',
                'company': '.company-name',
                'location': '.location-section',
                'description': '.job-description',
                'company_profile': '.about-company',
                'job_type': '.specifications .specification-list'
            },
            
            # ZipRecruiter
            'ziprecruiter.com': {
                'title': '.job_title',
                'company': '.hiring_company_text',
                'location': '.hiring_location',
                'description': '#job_description',
                'company_profile': '.company_description',
                'job_type': '.job_details li'
            },
            
            # Glassdoor
            'glassdoor.com': {
                'title': '[data-test="job-title"]',
                'company': '[data-test="employer-name"]',
                'location': '[data-test="location"]',
                'description': '[data-test="description"]',
                'company_profile': '.empBasicInfo',
                'job_type': '[data-test="employment-type"]'
            }
        }
        
        # Generic selectors as fallback
        self.generic_selectors = {
            'title': [
                'h1.job-title', 'h1.posting-title', 'h1.title', 
                'h1 span[title]', 'h1 span.title',
                '.job-title h1', '.posting-headline h1',
                'h1[data-testid="jobTitle"]',
                'h1'
            ],
            'company': [
                '.company-name', '.employer-name', '.posting-company',
                '[data-testid="company-name"]', '.company',
                '.employer', '.organization-name',
                'h2.company', 'span.company'
            ],
            'location': [
                '.job-location', '.location', '.posting-location',
                '[data-testid="location"]', '#job-location',
                '.location-name', '.job-info .location'
            ],
            'description': [
                '.job-description', '.description', '.posting-description',
                '[data-testid="jobDescriptionText"]', '#job-description',
                '.details', '.job-details', '.posting-details'
            ],
            'requirements': [
                '.job-requirements', '.requirements', '.qualifications',
                '[data-testid="jobRequirements"]', '#job-requirements',
                '.job-qualifications', '#qualifications'
            ],
            'benefits': [
                '.job-benefits', '.benefits', '.perks',
                '[data-testid="jobBenefits"]', '#job-benefits',
                '.compensation', '.perks'
            ],
            'company_profile': [
                '.company-profile', '.about-company', '.company-info',
                '[data-testid="companyInfo"]', '#company-profile',
                '.about-employer', '.employer-info'
            ]
        }
    
    def scrape_job_posting(self, url):
        """
        Scrape a job posting from a URL
        
        Args:
            url: URL of the job posting
            
        Returns:
            Dictionary with scraped job data
        """
        try:
            # Send a GET request to the URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Determine which selectors to use based on domain
            selectors = self._get_selectors_for_url(url)
            
            # Extract job data
            job_data = {
                'title': self._extract_text(soup, selectors['title']),
                'company': self._extract_text(soup, selectors['company']),
                'location': self._extract_text(soup, selectors['location']),
                'description': self._extract_text(soup, selectors['description']),
                'requirements': self._extract_text(soup, selectors.get('requirements', [])),
                'benefits': self._extract_text(soup, selectors.get('benefits', [])),
                'company_profile': self._extract_text(soup, selectors.get('company_profile', [])),
                'job_type': self._extract_text(soup, selectors.get('job_type', [])),
                'url': url,
                'contact_info': self._extract_contact_info(soup)
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error scraping job posting from {url}: {str(e)}")
            return None
    
    def _get_selectors_for_url(self, url):
        """Get the appropriate selectors for a given URL"""
        for domain, selectors in self.job_board_selectors.items():
            if domain in url:
                # Merge specific selectors with fallback generic selectors
                merged_selectors = {
                    field: selector if field in selectors else self.generic_selectors.get(field, [])
                    for field, selector in self.generic_selectors.items()
                }
                merged_selectors.update(selectors)
                return merged_selectors
        
        # Use generic selectors as fallback
        return self.generic_selectors
    
    def _extract_text(self, soup, selectors):
        """Extract text from HTML using a list of selectors"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.text.strip():
                return element.text.strip()
        
        return ''
    
    def _extract_contact_info(self, soup):
            """Extract contact information from the page"""
            page_text = soup.get_text()
            
            # Extract email addresses
            email_regex = r'[\w.-]+@[\w.-]+\.\w+'
            emails = re.findall(email_regex, page_text)
            
            # Extract phone numbers
            phone_regex = r'(\+\d{1,3})?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}'
            phones = re.findall(phone_regex, page_text)
            
            # Combine contact information
            contact_info = {
                'emails': emails,
                'phones': phones
            }
            
            return contact_info