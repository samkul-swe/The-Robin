# The-ROBIN: Fake Job Detection System

The-ROBIN (Reliable Online Background Investigation Network) is an advanced machine learning system designed to detect fraudulent job postings and help job seekers avoid scams.

## Features

- **Job Analysis**: Analyze job postings from URLs or manually entered details
- **Fraud Detection**: Uses advanced machine learning to identify suspicious job postings
- **Detailed Insights**: Provides confidence scores and specific reasons for flagging
- **Ensemble Approach**: Combines multiple machine learning models for better accuracy
- **Web Interface**: Easy-to-use web application for analyzing jobs

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```
git clone https://github.com/samkul-swe/The-ROBIN.git
cd The-ROBIN
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Download NLTK resources (if not automatically downloaded):
```python
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
```

### Usage
1. Training the models
First, train the machine learning models using the Kaggle fake job dataset:
```
python main.py --mode train --data path/to/fake_job_postings.csv
```
2. Starting the web application
Once the models are trained, start the web application:
```
python main.py --mode serve
```
This will start a development server at http://localhost:5000
3. Analyzing job postings
Access the web interface at http://localhost:5000
Either paste a job posting URL or enter job details manually
Click "Analyze Job" to get results

### How It Works
The-ROBIN uses an ensemble of machine learning models to analyze job postings:

Logistic Regression: Analyzes text patterns using TF-IDF
Multi-Layer Perceptron (MLP): Learns complex non-linear relationships
Random Forest: Examines categorical job features
Support Vector Machine (SVM): Provides precise classification

Each model is optimized for different aspects of job fraud detection:

Logistic Regression works best with SMOTE and TF-IDF
MLP works best without SMOTE and with TF-IDF
Random Forest works best with one-hot encoding and SMOTE
SVM works well with SMOTE and TF-IDF

Warning Signs of Fake Jobs
The-ROBIN looks for common red flags including:

- Requests for payment or fees
- Unrealistic salary promises
- Vague job descriptions
- Use of personal email domains
- Requests for sensitive personal information
- No formal interview process
- Urgent or high-pressure language

### Dataset
This project uses the "Real or Fake Job Posting Prediction" dataset from Kaggle, available at:
https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction

### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Acknowledgments
Kaggle for providing the dataset
Everyone who contributed to the libraries used in this project