"""
The-ROBIN: Fake Job Detection System
Main module to run the application
"""

import argparse
import os
import sys
import logging
from ui.app import create_app

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("robin.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='The-ROBIN: Fake Job Detection System')
    parser.add_argument('--mode', choices=['train', 'serve'], default='serve',
                      help='Mode to run: train (train models) or serve (run web app)')
    parser.add_argument('--data', type=str, default='data/fake_job_postings.csv',
                      help='Path to the dataset CSV file')
    parser.add_argument('--port', type=int, default=5000,
                      help='Port for the web application')
    parser.add_argument('--debug', action='store_true',
                      help='Run in debug mode')
    
    return parser.parse_args()

def main():
    """Main entry point for the application"""
    args = parse_arguments()
    
    if args.mode == 'train':
        logger.info("Starting model training...")
        from models.ensemble_model import train_ensemble_model
        train_ensemble_model(args.data)
        logger.info("Model training completed.")
    
    elif args.mode == 'serve':
        logger.info("Starting web application...")
        app = create_app()
        app.run(host='0.0.0.0', port=args.port, debug=args.debug)

if __name__ == "__main__":
    main()