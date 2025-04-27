# CS5100 Project Repository

## Foundations of AI

### Requirements
- **Python**: Version 3.9 and above

To install all required packages for this project, run:
```bash
pip install -r requirements.txt
```

### Usage

#### Dataset
- **Full Dataset**: Please use the data from Kaggle: [Real or Fake Job Posting Prediction](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction).
  
- **Part Dataset**: To create the training and testing datasets, run the following command:
```bash
python dataset_creator/train_test_split.py
```
This will generate `train_set.csv` and `test_set.csv`.

#### Configuration
Modify the following parameters based on your requirements:
```python
dataset_type = 'full'  # or 'part'
input_file = 'fake_job_postings.csv'  # or 'train_set.csv'
encoding_method = 'one_hot'  # or 'tf_idf'
model_name = 'mlp_classifier'  # or 'logistic_regression', 'naive_bayes'
use_smote = False  # Set to True to apply SMOTE
```

### Running the Script
Execute the script using Python:
```bash
python main.py
```

### Supported Models
The script supports the following models:
- **Logistic Regression**: `logistic_regression`
- **Multi-Layer Perceptron**: `mlp_classifier`
- **Naive Bayes**: `naive_bayes`

### Encoding Methods
You can choose between two encoding methods:
- **One-Hot Encoding**: `one_hot`
- **TF-IDF Encoding**: `tf_idf`

### SMOTE
You can apply SMOTE (Synthetic Minority Over-sampling Technique) to balance the training dataset by setting `use_smote` to `True`.