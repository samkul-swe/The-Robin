# The-ROBIN: Fake Job Detection Chrome Extension

The-ROBIN (Reliable Online Background Investigation Network) is a Chrome extension that detects potentially fraudulent job postings using machine learning. It helps job seekers identify scams and fraudulent listings in real-time while browsing job boards.

## Features

- **Real-time Analysis**: Instantly analyze job postings on major job boards
- **Fraud Risk Score**: Get a clear percentage indicating how suspicious a job posting appears
- **Visual Indicators**: Color-coded badges and icons make it easy to identify risk levels
- **Detailed Analysis**: View comprehensive analysis and specific red flags
- **Multiple Job Boards**: Works on Indeed, LinkedIn, Glassdoor, Monster, and ZipRecruiter
- **Auto-Analyze**: Option to automatically analyze jobs as you browse
- **Development/Production Modes**: Easy switching between local development and production servers

## Usage

1. **Browse to a job listing** on any supported job board (Indeed, LinkedIn, Glassdoor, Monster, ZipRecruiter)

2. **Click The-ROBIN icon** in your browser toolbar to open the extension popup

3. **Analyze the job** by clicking the "Analyze This Job" button or enable auto-analyze in settings

4. **View the fraud risk score** and verdict in the popup

5. **See detailed analysis** by clicking "View Details" for comprehensive red flags and explanations

6. **Configure settings** in the popup:
   - Toggle auto-analyze on/off
   - Switch between development and production servers

## Architecture

### Extension Components

- **manifest.json**: Extension configuration
- **popup/**: User interface for the extension
- **background/**: Background scripts for handling extension events
- **content/**: Content scripts that run on supported job sites
- **icons/**: Extension icons and logo

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dataset from Kaggle: "Real or Fake Job Posting Prediction"
- Icon design inspired by the European robin (Erithacus rubecula)
- Developed to help job seekers avoid scams and fraudulent listings

---