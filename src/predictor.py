import pandas as pd
import joblib

class SimpleRevenuePredictor:
    """Predicts a single raw revenue value."""
    def __init__(self, model_path, columns_path):
        self.model = joblib.load(model_path)
        self.model_columns = joblib.load(columns_path)

    def prepare_features(self, movie_data):
        df = pd.DataFrame([movie_data])
        categorical_cols = [
            'main_genre', 'main_company', 'original_language',
            'director', 'star1', 'star2', 'star3'
        ]
        # Only encode columns that exist in the input dataframe
        cols_to_encode = [col for col in categorical_cols if col in df.columns]
        df_encoded = pd.get_dummies(df, columns=cols_to_encode)
        df_aligned = df_encoded.reindex(columns=self.model_columns, fill_value=0)
        return df_aligned

    def predict(self, movie_data):
        prepared_df = self.prepare_features(movie_data)
        prediction = self.model.predict(prepared_df)
        return prediction[0]


class AdvancedROIPredictor:
    """Predicts a range of ROI values and incorporates hype features."""
    def __init__(self, model_path, columns_path):
        self.models = joblib.load(model_path)
        self.model_columns = joblib.load(columns_path)

    def prepare_features(self, movie_data):
        df = pd.DataFrame([movie_data])
        categorical_cols = [
            'main_genre', 'main_company', 'original_language',
            'director', 'star1', 'star2', 'star3'
        ]
        cols_to_encode = [col for col in categorical_cols if col in df.columns]
        df_encoded = pd.get_dummies(df, columns=cols_to_encode)
        df_aligned = df_encoded.reindex(columns=self.model_columns, fill_value=0)
        return df_aligned

    def predict(self, movie_data):
        prepared_df = self.prepare_features(movie_data)
        predictions = {}
        for name, model in self.models.items():
            predictions[name] = model.predict(prepared_df)[0]
        return predictions