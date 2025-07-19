import pandas as pd
import os
import time
from tqdm import tqdm # Import tqdm

# Import functions
from tmdb_client import get_movie_titles_from_discover, get_movie_data

if __name__ == "__main__":
    #both popular and unpopular titles
    popular_titles = get_movie_titles_from_discover(sort_by="popularity.desc", pages=250)
    unpopular_titles = get_movie_titles_from_discover(sort_by="popularity.asc", pages=10)

    all_titles = list(set(popular_titles + unpopular_titles))

    print(f"\nFetching details for {len(all_titles)} unique movies...")
    all_movie_data = []
    for title in tqdm(all_titles):
        details = get_movie_data(title)
        if details:
            all_movie_data.append(details)
        else:
            # This print statement can clutter the progress bar,
            # so you might want to log failures to a file instead.
            # print(f"Could not fetch data for: {title}")
            pass

    if all_movie_data:
        print("\nConverting data to DataFrame and saving...")
        df = pd.DataFrame(all_movie_data)

        output_path = os.path.join('..', 'data', 'tmdb_movies.csv')
        df.to_csv(output_path, index=False)

        print(f"Successfully saved {len(df)} movies to {output_path}")