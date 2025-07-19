import pandas as pd
import numpy as np
import ast
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

# --- 1. Load and Clean the Data ---
try:
    df = pd.read_csv('../data/tmdb_movies.csv')
except FileNotFoundError:
    print("Error: tmdb_movies.csv not found. Make sure it's in the 'data' folder.")
    exit()

df = df[(df['budget'] > 1000) & (df['revenue'] > 1000)].copy()

# --- 2. Feature Engineering ---
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

# 1. Select your original numeric features
numeric_features = df[['budget', 'popularity', 'runtime']]
categorical_feature_names = [
    'main_genre',
    'main_company',
    'original_language',
    'director',
    'star1',
    'star2',
    'star3'
]
categorical_features = df[categorical_feature_names]

encoded_features = pd.get_dummies(categorical_features, dummy_na=True, dtype=int)
# 3. Combine the numeric and new encoded features
X = pd.concat([numeric_features.reset_index(drop=True), encoded_features.reset_index(drop=True)], axis=1)
y = df['revenue']

# --- 3. Train the Model ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
print("\nModel trained successfully!")

# --- NEW: Save the Model and Columns ---
joblib.dump(model, '../models/profitability_model.pkl')
joblib.dump(list(X.columns), '../models/model_columns.pkl')

print("Model and feature columns saved successfully.")