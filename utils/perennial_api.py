# utils/perennial_api.py
import requests

API_BASE_URL = 'https://api.perennial.com/v1'
API_KEY = 'your_api_key_here'

def fetch_plant_data(plant_name):
    headers = {'Authorization': f'Bearer {API_KEY}'}
    params = {'query': plant_name}
    response = requests.get(f"{API_BASE_URL}/plants", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
