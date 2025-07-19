import pandas as pd
import joblib

class MovieRevenuePredictor:
    def __init__(self, model_path, columns_path):
        """
        Loads the pre-trained model and the list of feature columns.
        """
        self.model = joblib.load(model_path)
        self.model_columns = joblib.load(columns_path)

    def prepare_features(self, movie_data):
        """
        Prepares the input data for prediction by one-hot encoding
        and aligning columns with the training data.
        """
        df = pd.DataFrame([movie_data])

        # Define all possible categorical columns
        categorical_columns = [
            'main_genre',
            'main_company',
            'original_language',
            'director',
            'star1',
            'star2',
            'star3'
        ]

        # One-hot encode the categorical features present in the input
        df_encoded = pd.get_dummies(df, columns=categorical_columns)

        # Align columns with the model's training columns. This is the key step
        # that handles all features correctly.
        df_aligned = df_encoded.reindex(columns=self.model_columns, fill_value=0)

        return df_aligned

    def predict(self, movie_data):
        """
        Takes a dictionary of movie data and returns the predicted revenue.
        """
        prepared_df = self.prepare_features(movie_data)
        prediction = self.model.predict(prepared_df)
        return prediction[0]