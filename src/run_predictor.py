from predictor import MovieRevenuePredictor
from tmdb_client import get_movie_data, parse_json_col

if __name__ == "__main__":
    # 1. Initialize the predictor
    predictor = MovieRevenuePredictor(
        model_path='../models/profitability_model.pkl',
        columns_path='../models/model_columns.pkl'
    )

    # 2. Get a movie title from the user
    movie_title = input("Enter a movie title to predict its revenue: ")

    # 3. Fetch the movie's data from the TMDB API
    print(f"Searching for '{movie_title}' on TMDB...")
    raw_data = get_movie_data(movie_title)

    # 4. Prepare the data and make a prediction
    if raw_data:
        # Transform the raw API data into the dictionary our model needs
        new_movie_features = {
            'budget': raw_data.get('budget', 0),
            'popularity': raw_data.get('popularity', 0),
            'runtime': raw_data.get('runtime', 0),
            'main_genre': parse_json_col(raw_data.get('genres', []), 'name'),
            'main_company': parse_json_col(raw_data.get('production_companies', []), 'name'),
            'original_language': raw_data.get('original_language', ''),
            'director': raw_data.get('director'),
            'star1': raw_data.get('star1'),
            'star2': raw_data.get('star2'),
            'star3': raw_data.get('star3')
        }

        # Get the prediction
        predicted_revenue = predictor.predict(new_movie_features)

        print("\n--- Prediction Result ---")
        print(f"Movie Title: {raw_data.get('title')}")
        print(f"Predicted Revenue: ${predicted_revenue:,.2f}")
    else:
        print(f"Could not find movie data for '{movie_title}'.")