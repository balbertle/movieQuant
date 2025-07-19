import requests
import os
from dotenv import load_dotenv
import time

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3/"
if not API_KEY:
    raise ValueError("TMDB_API_KEY broken")


def parse_json_col(column_data, key_name):
    """
    Parses a list of dictionaries (from a JSON response)
    and extracts the value for a specific key from the first item.
    """
    if isinstance(column_data, list) and column_data:
        return column_data[0].get(key_name)
    return None

def get_movie_data(movie_title):
    """
    Fetches detailed movie data from TMDB by title.
    """
    # Search to get ID
    url = f"https://api.themoviedb.org/3/search/movie?query={movie_title}&include_adult=false&language=en-US&page=1"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.get(url, headers=headers)
        search_data = response.json()

        # Get the ID of the first search result
        if not search_data.get('results'):
            return None
        movie_id = search_data['results'][0]['id']
        #print(f"Found movie ID for '{movie_title}': {movie_id}")

        # --- 2. Use the ID to get movie info ---
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        response = requests.get(url, headers=headers)

        movie_details = response.json()


        creditURL = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
        creditResponse = requests.get(creditURL, headers=headers)
        credits = creditResponse.json()

        director_name = None
        for member in credits.get('crew', []):
            if member.get('job') == 'Director':
                director_name = member.get('name')
                break #

        stars = []
        cast = credits.get('cast', [])
        for i in range(min(3, len(cast))):
            stars.append(cast[i].get('name'))

        movie_details['director'] = director_name
        movie_details['star1'] = stars[0] if len(stars) > 0 else None
        movie_details['star2'] = stars[1] if len(stars) > 1 else None
        movie_details['star3'] = stars[2] if len(stars) > 2 else None

        return movie_details

    except requests.exceptions.RequestException as e:
        print(f"An API request error occurred: {e}")
        return None



def get_movie_titles_from_discover(sort_by="popularity.desc", pages=5):
    """Gets a list of movie titles from the TMDB /discover endpoint."""
    titles = []
    discover_url = f"{BASE_URL}/discover/movie"
    print(f"\nFetching movies sorted by {sort_by}...")

    # Define the headers, just like in your other function
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    for page in range(1, pages + 1):
        # Define parameters WITHOUT the api_key
        params = {
            'sort_by': sort_by,
            'page': page,
            'include_adult': 'false',
            'language': 'en-US'
        }
        try:
            # Pass both headers and params to the request
            response = requests.get(discover_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            for movie in data.get('results', []):
                titles.append(movie['title'])
            time.sleep(0.05)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

    print(f"Found {len(titles)} titles.")
    return titles