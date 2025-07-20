import pandas as pd
from datetime import datetime, timedelta
import time
from pytrends.request import TrendReq
import os
import random
from tqdm import tqdm # For a visual progress bar

# --- Configuration ---
INPUT_CSV_PATH = '../data/tmdb_movies.csv'
OUTPUT_CSV_PATH = '../data/tmdb_movies_with_hype.csv'
BATCH_SIZE = 10

# --- Main Script ---
pytrends = TrendReq(hl='en-US', tz=360)

# Load the base movie data
df_input = pd.read_csv(INPUT_CSV_PATH)

if os.path.exists(OUTPUT_CSV_PATH):
    df_output = pd.read_csv(OUTPUT_CSV_PATH)
    processed_titles = df_output['title'].tolist()
    df_to_process = df_input[~df_input['title'].isin(processed_titles)].copy()
    print(f"Resuming script. {len(processed_titles)} movies already processed.")
else:
    df_output = pd.DataFrame()
    df_to_process = df_input.copy()

print(f"{len(df_to_process)} movies remaining to process.")
results_batch = []

for index, row in tqdm(df_to_process.iterrows(), total=df_to_process.shape[0]):
    movie_title = row['title']
    release_date_str = row.get('release_date')

    time.sleep(random.uniform(2, 5))

    peak_hype = 0
    average_hype = 0

    if pd.notna(release_date_str):
        try:
            release_date = datetime.strptime(str(release_date_str), '%Y-%m-%d')
            timeframe = f"{(release_date - timedelta(days=45)).strftime('%Y-%m-%d')} {(release_date - timedelta(days=1)).strftime('%Y-%m-%d')}"

            pytrends.build_payload(kw_list=[movie_title], timeframe=timeframe)
            interest_df = pytrends.interest_over_time()

            if not interest_df.empty and movie_title in interest_df.columns:
                peak_hype = interest_df[movie_title].max()
                average_hype = interest_df[movie_title].mean()

        except Exception as e:
            # If any error occurs, log it and move on. Don't stop the whole script.
            print(f"\nError processing '{movie_title}': {e}. Skipping.")

    # Add results to a temporary list
    row_data = row.to_dict()
    row_data['peak_hype'] = peak_hype
    row_data['average_hype'] = average_hype
    results_batch.append(row_data)

    # Save progress in batches
    if len(results_batch) >= BATCH_SIZE:
        batch_df = pd.DataFrame(results_batch)
        df_output = pd.concat([df_output, batch_df], ignore_index=True)
        # Use mode='a' and header=not os.path.exists() for cleaner appending
        df_output.to_csv(OUTPUT_CSV_PATH, index=False, mode='w', header=True)
        results_batch = [] # Clear the batch

# Save any remaining results after the loop finishes
if results_batch:
    batch_df = pd.DataFrame(results_batch)
    df_output = pd.concat([df_output, batch_df], ignore_index=True)
    df_output.to_csv(OUTPUT_CSV_PATH, index=False, mode='w', header=True)

print("\n--- Data collection complete. ---")