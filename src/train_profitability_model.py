import pandas as pd
import numpy as np
import ast
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import QuantileRegressor # Using the ROI/Quantile model

# --- 1. Load the Final, Enriched Dataset ---
try:
    # Load the new CSV that contains the Google Trends "hype" data
    df = pd.read_csv('../data/tmdb_movies_with_hype.csv')
except FileNotFoundError:
    print("Error: tmdb_movies_with_hype.csv not found.")
    print("Please run the collect_full_dataset.py script first.")
    exit()

# Filter out movies with missing financial data
df = df[(df['budget'] > 1000) & (df['revenue'] > 1000)].copy()
print(f"Loaded and cleaned data. Shape is now: {df.shape}")

# --- 2. Feature Engineering ---
# This section remains the same, as it processes the loaded data
def parse_json_col(column_str, key_name):
    try:
        item_list = ast.literal_eval(str(column_str))
        if isinstance(item_list, list) and item_list:
            return item_list[0].get(key_name)
    except (ValueError, SyntaxError):
        return None
    return None

df['main_genre'] = df['genres'].apply(lambda x: parse_json_col(x, 'name'))
df['main_company'] = df['production_companies'].apply(lambda x: parse_json_col(x, 'name'))

# Select all numeric features, including the new hype data
numeric_features = df[['budget', 'popularity', 'runtime', 'average_hype']]
numeric_features = numeric_features.fillna(0) # Fill any potential NaN values from hype data

# Select all categorical features
categorical_feature_names = [
    'main_genre', 'main_company', 'original_language',
    'director', 'star1', 'star2', 'star3'
]
categorical_features = df[categorical_feature_names]
encoded_features = pd.get_dummies(categorical_features, dummy_na=True, dtype=int)

# Combine all features
X = pd.concat([numeric_features.reset_index(drop=True), encoded_features.reset_index(drop=True)], axis=1)

# Define ROI as the Target Variable
df['roi'] = df['revenue'] / df['budget']
y = df['roi']

# --- 3. Train the Quantile Models ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

quantiles = {
    'low': 0.1,
    'median': 0.5,
    'high': 0.9
}
models = {}
for name, q in quantiles.items():
    # Use the QuantileRegressor model
    model = QuantileRegressor(quantile=q, alpha=0.01, solver='highs-ds')
    print(f"Training {name} ROI model (quantile={q})...")
    model.fit(X_train, y_train)
    models[name] = model

print("\nAll models trained successfully!")

# --- 4. Save the Models and Supporting Files ---
joblib.dump(models, '../models/roi_quantile_models.pkl')
joblib.dump(list(X.columns), '../models/model_columns.pkl')

baseline_hype = {
    'average_hype': X['average_hype'].median()
}
joblib.dump(baseline_hype, '../models/baseline_hype.pkl')

print("ROI models, feature columns, and baseline hype values saved successfully.")