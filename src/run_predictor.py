import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time
from pytrends.request import TrendReq

# Use the correct ROI predictor class
from predictor import AdvancedROIPredictor
from tmdb_client import get_movie_data, parse_json_col

# Mapping of major studios to their parent company stock tickers
ticker_map = {
    "Walt Disney Pictures": "DIS", "Pixar": "DIS", "Marvel Studios": "DIS",
    "Warner Bros. Pictures": "WBD", "Universal Pictures": "CMCSA",
    "Paramount": "PARA", "Columbia Pictures": "SONY"
}

if __name__ == "__main__":
    # 1. Initialize the correct ROI predictor
    predictor = AdvancedROIPredictor(
        model_path='../models/roi_quantile_models.pkl',
        columns_path='../models/model_columns.pkl'
    )
    pytrends = TrendReq(hl='en-US', tz=360)

    # 2. Get a movie title from the user
    movie_title = input("Enter a movie title to predict its ROI and stock impact: ")

    # 3. Fetch the movie's data from the TMDB API
    print(f"\nSearching for '{movie_title}' on TMDB...")
    raw_data = get_movie_data(movie_title)

    # 4. Prepare the data and make a prediction
    if raw_data and raw_data.get('budget', 0) > 0:
        # --- NEW: Fetch live Google Trends data ---
        peak_hype = 0
        average_hype = 0
        release_date_str = raw_data.get('release_date')
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, '%Y-%m-%d')
                timeframe = f"{(release_date - timedelta(days=30)).strftime('%Y-%m-%d')} {release_date.strftime('%Y-%m-%d')}"
                pytrends.build_payload(kw_list=[movie_title], timeframe=timeframe)
                interest_df = pytrends.interest_over_time()
                if not interest_df.empty:
                    peak_hype = interest_df[movie_title].max()
                    average_hype = interest_df[movie_title].mean()
            except Exception as e:
                print(f"Could not fetch Google Trends data: {e}")

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
            'star3': raw_data.get('star3'),
            'peak_hype': peak_hype,
            'average_hype': average_hype
        }

        # Get the dictionary of ROI predictions
        roi_predictions = predictor.predict(new_movie_features)

        # --- Stock Impact Calculation ---
        company = new_movie_features['main_company']
        ticker_symbol = ticker_map.get(company)

        print("\n--- ROI Prediction Analysis ---")
        print(f"Movie Title: {raw_data.get('title')}")
        print(f"Median Predicted ROI: {roi_predictions.get('median', 0):.2f}x")

        if ticker_symbol:
            company_stock = yf.Ticker(ticker_symbol)
            company_revenue = company_stock.financials.loc['Total Revenue'].iloc[0]
            predicted_profit = (roi_predictions.get('median', 1) - 1) * new_movie_features['budget']
            impact_ratio = predicted_profit / company_revenue

            print("\n--- Stock Impact Analysis ---")
            print(f"Parent Company: {company} ({ticker_symbol})")
            print(f"Predicted Movie Profit: ${predicted_profit:,.2f}")
            print(f"Impact Ratio (vs Annual Revenue): {impact_ratio:.4%}")

            if impact_ratio > 0.02:
                print("Prediction: POSITIVE sentiment for stock price.")
            elif impact_ratio < -0.01:
                print("Prediction: NEGATIVE sentiment for stock price.")
            else:
                print("Prediction: NEUTRAL/LOW impact on stock price.")
        else:
            print(f"\nNo stock ticker mapped for '{company}'.")
    else:
        print(f"Could not find sufficient data for '{movie_title}'.")