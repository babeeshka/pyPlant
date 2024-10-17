# utils/perenual_api.py
import requests
import os

API_KEY = os.getenv('PERENUAL_API_KEY')
API_BASE_URL = 'https://perenual.com/api/v1'

def get_plant_data(query):
    endpoint = f"{API_BASE_URL}/plants"
    headers = {
        'Authorization': f'Token {API_KEY}',
    }
    params = {
        'q': query,
        'page': 1,
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()
