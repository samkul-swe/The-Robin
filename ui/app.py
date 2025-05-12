"""
Web application for The-ROBIN fake job detection system
"""

import json
from flask import Flask, render_template, request, jsonify, url_for, redirect
import logging

from models.ensemble_model import EnsembleModel
from utils.job_scraper import JobScraper

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Initialize models
    ensemble_model = EnsembleModel()
    try:
        ensemble_model.load_models()
        ensemble_model.load_preprocessor()
        model_loaded = True
    except Exception as e:
        logger.error(f"Error loading models: {str(e)}")
        model_loaded = False
    
    # Initialize job scraper
    job_scraper = JobScraper()
    
    @app.route('/')
    def index():
        """Render the home page"""
        return render_template('index.html', model_loaded=model_loaded)
    
    @app.route('/analyze', methods=['POST'])
    def analyze():
        """Analyze a job posting"""
        if not model_loaded:
            return jsonify({
                'error': 'Models not loaded. Please train the models first.'
            }), 400
        
        try:
            # Check if URL or text data was provided
            if 'job_url' in request.form and request.form['job_url']:
                # Scrape job posting from URL
                job_url = request.form['job_url']
                job_data = job_scraper.scrape_job_posting(job_url)
                
                if not job_data:
                    return jsonify({
                        'error': 'Could not scrape job posting from the provided URL.'
                    }), 400
            
            elif 'job_title' in request.form and 'job_description' in request.form:
                # Use provided text data
                job_data = {
                    'title': request.form['job_title'],
                    'company': request.form.get('company_name', ''),
                    'description': request.form['job_description'],
                    'requirements': request.form.get('job_requirements', ''),
                    'benefits': request.form.get('job_benefits', ''),
                    'company_profile': request.form.get('company_profile', ''),
                    'location': request.form.get('job_location', ''),
                    'contact_info': {
                        'emails': request.form.get('contact_email', '').split(','),
                        'phones': request.form.get('contact_phone', '').split(',')
                    }
                }
            else:
                return jsonify({
                    'error': 'No job data provided. Please enter a URL or job details.'
                }), 400
            
            # Analyze the job posting
            result = ensemble_model.predict(job_data)
            
            # Ensure all values are JSON serializable
            result['is_fake'] = bool(result['is_fake'])
            result['confidence_score'] = float(result['confidence_score'])
            
            if 'model_probabilities' in result:
                for key in result['model_probabilities']:
                    result['model_probabilities'][key] = float(result['model_probabilities'][key])
            
            # Add job data to result
            result['job_data'] = job_data
            
            # Return the result
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"Error analyzing job posting: {str(e)}")
            return jsonify({
                'error': 'An error occurred during analysis.'
            }), 500
    
    @app.route('/results')
    def results():
        """Render the results page"""
        # Get result data from query parameters
        result_json = request.args.get('result')
        
        if not result_json:
            return redirect(url_for('index'))
        
        try:
            # Parse the JSON result
            result = json.loads(result_json)
            
            return render_template('results.html', result=result)
        
        except Exception as e:
            logger.error(f"Error rendering results: {str(e)}")
            return redirect(url_for('index'))
    
    @app.route('/about')
    def about():
        """Render the about page"""
        return render_template('about.html')
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        logger.error(f"Server error: {str(e)}")
        return render_template('500.html'), 500
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'message': 'The-ROBIN API is running'
    })
    
    return app