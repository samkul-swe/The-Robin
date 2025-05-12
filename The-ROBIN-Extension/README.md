# The-ROBIN: Fake Job Detection Chrome Extension

The-ROBIN (Real Or Bogus job posting INspector) is a Chrome extension that detects potentially fraudulent job postings using machine learning. It helps job seekers identify scams and fraudulent listings in real-time while browsing job boards.

## Features

- **Real-time Analysis**: Instantly analyze job postings on major job boards
- **Fraud Risk Score**: Get a clear percentage indicating how suspicious a job posting appears
- **Visual Indicators**: Color-coded badges and icons make it easy to identify risk levels
- **Detailed Analysis**: View comprehensive analysis and specific red flags
- **Multiple Job Boards**: Works on Indeed, LinkedIn, Glassdoor, Monster, and ZipRecruiter
- **Auto-Analyze**: Option to automatically analyze jobs as you browse
- **Development/Production Modes**: Easy switching between local development and production servers

## Technology Stack

- **Frontend**: JavaScript, HTML, CSS (Chrome Extension)
- **Backend**: Python, Flask, scikit-learn, NLTK
- **ML Models**: Ensemble model combining Logistic Regression, MLP, Random Forest, and SVM
- **Data Processing**: TF-IDF Vectorization, SMOTE for imbalanced data, One-Hot Encoding

## Installation

### Chrome Extension Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/The-ROBIN.git
   cd The-ROBIN/extension
   ```

2. Load the extension in Chrome:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in the top-right)
   - Click "Load unpacked" and select the `extension` directory

### Backend Setup

1. Set up the Python environment:
   ```
   cd The-ROBIN/backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Download the dataset and train models:
   ```
   python main.py --mode train --data data/fake_job_postings.csv
   ```

3. Start the Flask server:
   ```
   python main.py --mode serve
   ```

## Usage

1. **Browse to a job listing** on any supported job board (Indeed, LinkedIn, Glassdoor, Monster, ZipRecruiter)

2. **Click The-ROBIN icon** in your browser toolbar to open the extension popup

3. **Analyze the job** by clicking the "Analyze This Job" button or enable auto-analyze in settings

4. **View the fraud risk score** and verdict in the popup

5. **See detailed analysis** by clicking "View Details" for comprehensive red flags and explanations

6. **Configure settings** in the popup:
   - Toggle auto-analyze on/off
   - Switch between development and production servers

## Development

### Local Development Setup

1. The extension communicates with a local Flask server by default (http://localhost:5000)

2. Make sure the Flask server is running when testing locally:
   ```
   cd backend
   python main.py --mode serve
   ```

3. For API development, update the server URL in the extension settings or modify `background.js`

4. After making changes to extension files, refresh the extension in Chrome's extensions page

### Modifying ML Models

1. The machine learning models are defined in the `backend/models` directory

2. Modify model parameters in their respective files:
   - `logistic_regression_model.py`
   - `mlp_model.py`
   - `random_forest_model.py`
   - `svm_model.py`
   - `ensemble_model.py`

3. Retrain models after making changes:
   ```
   python main.py --mode train
   ```

## Architecture

### Extension Components

- **manifest.json**: Extension configuration
- **popup/**: User interface for the extension
- **background/**: Background scripts for handling extension events
- **content/**: Content scripts that run on supported job sites
- **icons/**: Extension icons and logo

### Backend Components

- **main.py**: Entry point for the application
- **models/**: Machine learning models implementation
- **data/**: Data loading and preprocessing
- **utils/**: Utility functions for text analysis and job scraping
- **ui/**: Flask web application for detailed analysis viewing

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset from Kaggle: "Real or Fake Job Posting Prediction"
- Icon design inspired by the European robin (Erithacus rubecula)
- Developed to help job seekers avoid scams and fraudulent listings

---

**Note**: This project was developed as a demonstration of applying machine learning to detect fraudulent job postings. The ML models should be considered educational rather than definitive fraud detection tools.
