import os
import pandas as pd
from data_preprocessing.preprocessing import preprocess_text
from sklearn.model_selection import train_test_split

# Classifiers
from classifiers.logistic_regression import LogisticRegressionModel
from classifiers.naive_bayes_model import NaiveBayesModel
from classifiers.mlp_classifier import MLPModel
from classifiers.knn_classifier import KNNModel
from classifiers.decision_tree import DecisionTreeModel
from classifiers.random_forest import RandomForestModel
from classifiers.support_vector_classifier import SVCModel
from data_preprocessing.smote_handler import SMOTEHandler

# Encoders
from data_preprocessing.one_hot_encode import one_hot_encode
from data_preprocessing.tf_idf_encode import tf_idf_encode

def load_model(model_name):
    if model_name == 'logistic_regression':
        return LogisticRegressionModel()
    elif model_name == 'naive_bayes':
        return NaiveBayesModel()
    elif model_name == 'mlp':
        return MLPModel()
    elif model_name == 'knn':
        return KNNModel()
    elif model_name == 'decision_tree':
        return DecisionTreeModel()
    elif model_name == 'random_forest':
        return RandomForestModel()
    elif model_name == 'svc':
        return SVCModel()
    else:
        raise ValueError("Invalid model name.")

def save_results(results, filename='results/model_results.csv'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    results_df = pd.DataFrame(results)
    if os.path.exists(filename):
        results_df.to_csv(filename, mode='a', header=False, index=False)
    else:
        results_df.to_csv(filename, index=False)

def preprocess_and_save(input_file, preprocessed_file):
    if os.path.exists(preprocessed_file):
        print("Loading preprocessed data...")
        df = pd.read_csv(preprocessed_file)
    else:
        print("Loading dataset...")
        df = pd.read_csv(input_file)
        print("Dataset loaded...")

        # Preprocess text
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        df.fillna('', inplace=True)
        print("NaN values handled before preprocessing.")
        df = preprocess_text(df, text_columns)

        # Save preprocessed data
        print("Saving preprocessed data...")
        df.to_csv(preprocessed_file, index=False)
    
    return df

def save_encoded_data(df, encoding_method, encoded_file):
    print(f"Saving encoded data using {encoding_method}...")
    df.to_csv(encoded_file, index=False)

def main(input_file, preprocessed_file, encoding_method, model_name, use_smote=False):
    results = []

    # Determine encoded file name
    encoded_file = f'encoded_data_{encoding_method}.csv'

    # Check if the encoded dataset exists
    if os.path.exists(encoded_file):
        print("Loading encoded data...")
        df = pd.read_csv(encoded_file)
    else:
        # Load and preprocess data
        df = preprocess_and_save(input_file, preprocessed_file)

        # Encoding
        print("Starting feature encoding...")
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        if encoding_method == 'one_hot':
            df = one_hot_encode(df, text_columns)
        elif encoding_method == 'tf_idf':
            df = tf_idf_encode(df, text_columns)
        else:
            raise ValueError("Invalid encoding method.")

        # Save encoded data
        save_encoded_data(df, encoding_method, encoded_file)

    X = df.drop(columns=['fraudulent'], errors='ignore')
    y = df.get('fraudulent')

    if X.isnull().any().any() or y.isnull().any():
        raise ValueError("Input X or y contains NaN values after encoding.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if use_smote:
        print("SMOTE started")
        smote_handler = SMOTEHandler()
        X_train, y_train = smote_handler.apply_smote(X_train, y_train)
        print("SMOTE applied to the training data.")

    print("Loading model...")
    model = load_model(model_name)

    print("Starting model training...")
    try:
        model.train(X_train, y_train)
        print("Model training completed.")
    except Exception as e:
        print("Error during model training:")
        print(e)
        return

    try:
        accuracy, f1, kappa, mse, auc_roc, auc_pr = model.evaluate(X_test, y_test)

        # Collect results
        result_entry = {
            'input_file': input_file,
            'encoding_method': encoding_method,
            'model_name': model_name,
            'use_smote': use_smote,
            'accuracy': accuracy,
            'f1_score': f1,
            'cohen_kappa': kappa,
            'mean_squared_error': mse,
            'roc_auc': auc_roc,
            'precision_recall_auc': auc_pr
        }
        results.append(result_entry)

    except Exception as e:
        print("Error during model evaluation:")
        print(e)

    # Save results to CSV
    if results:
        save_results(results)

if __name__ == "__main__":
    input_file = 'fake_job_postings.csv'
    preprocessed_file = 'preprocessed_data.csv'

    models = ['logistic_regression', 'naive_bayes', 'mlp', 'knn', 'decision_tree', 'random_forest', 'svc']
    encodings = ['one_hot', 'tf_idf']
    use_smote_options = [True, False]

    for model in models:
        for encoding in encodings:
            for use_smote in use_smote_options:
                main(input_file, preprocessed_file, encoding, model, use_smote)