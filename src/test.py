import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

if not API_KEY:
    raise ValueError("TMDB_API_KEY broken")


url = "https://api.themoviedb.org/3/find/external_id?external_source="

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

response = requests.get(url, headers=headers)

print(response.text)