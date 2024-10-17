# services/perenual_service.py
import os
import requests
import logging
from dotenv import load_dotenv
from marshmallow import ValidationError
from schemas import PlantSchema

load_dotenv()

API_BASE_URL = 'https://perenual.com/api'
API_KEY = os.getenv('PERENUAL_API_KEY')

logging.basicConfig(level=logging.DEBUG)  #  DEBUG to capture all logs
logger = logging.getLogger(__name__)

plant_schema = PlantSchema()

# species-list paginated
def fetch_species_list(page=1):
    try:
        params = {
            'key': API_KEY,
            'page': page
        }
        
        logger.debug(f"Fetching species list with URL: {API_BASE_URL}/species-list, params: {params}")
        
        response = requests.get(f"{API_BASE_URL}/species-list", params=params)
        
        logger.debug(f"Response Status Code: {response.status_code}")
        
        logger.debug(f"Response Content: {response.text}")
        
        response.raise_for_status()
        
        data = response.json()
        
        logger.debug(f"Parsed Data: {data}")
        
        if 'data' in data and data['data']:
            logger.debug(f"Species Data: {data['data']}")
            return data['data']
        else:
            logger.error("Unexpected response structure: Missing 'data' key or 'data' is empty.")
            return []
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching species list: {e}")
        return None

# fetch plant details by ID from Perenual API
def fetch_plant_details_by_id(plant_id):
    try:
        logger.info(f"Fetching plant details from Perenual API for plant ID: {plant_id}")
        response = requests.get(f"{API_BASE_URL}/species/details/{plant_id}", params={'key': API_KEY})
        
        logger.debug(f"Response Status Code: {response.status_code}")
        response.raise_for_status()  # This will raise an exception for HTTP errors
        
        logger.debug(f"Response Content: {response.text}")
        plant_data = response.json()

        try:
            validated_data = plant_schema.load(plant_data)
            return validated_data
        except ValidationError as e:
            logger.error(f"Validation error while fetching plant data: {e.messages}")
            return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching plant details from Perenual API for plant ID {plant_id}: {e}")
        return None

# plant disease by plant ID
def fetch_plant_diseases(species_id):
    try:
        response = requests.get(f"{API_BASE_URL}/pest-disease-list", params={'key': API_KEY, 'id': species_id})
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching diseases for species ID {species_id}: {e}")
        raise

# plant guides by plant ID
def fetch_plant_guides(species_id, guide_type=None):
    params = {'key': API_KEY, 'species_id': species_id}
    if guide_type:
        params['type'] = guide_type
    try:
        response = requests.get(f"{API_BASE_URL}/species-care-guide-list", params=params)
        response.raise_for_status()
        return response.json().get('data', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching plant guides for species ID {species_id}: {e}")
        raise

# random plant from perenual
def fetch_random_plant():
    import random
    random_id = random.randint(1, 10102)
    logger.info(f"Fetching random plant details for ID: {random_id}")
    try:
        response = requests.get(f"{API_BASE_URL}/species/details/{random_id}", params={'key': API_KEY})
        response.raise_for_status()
        try:
            validated_data = plant_schema.load(response.json())
            return validated_data
        except ValidationError as e:
            logger.error(f"Validation error while fetching random plant data: {e.messages}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching random plant details for ID {random_id}: {e}")
        raise