# routes.py
from flask import Blueprint, request, jsonify
from functools import wraps
from marshmallow import ValidationError
from cachelib import SimpleCache
import time
from services.plant_service import (
    add_plant,
    find_all_plants_with_pagination,
    get_plant_by_any_id,
    update_plant_details,
    remove_plant_from_db
)
from services.perenual_service import (
    fetch_species_list,
    fetch_plant_details_by_id,
    fetch_plant_diseases,
    fetch_plant_guides,
    fetch_random_plant
)
import logging

# setup basic route config and logging
api_routes = Blueprint('api', __name__)
cache = SimpleCache()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# requests per IP address - adjust based on API tier
RATE_LIMIT = 100  # per minute
RATE_LIMIT_PERIOD = 60  # seconds

def rate_limit(func):
    """tracks and limits API requests per IP address using simple cache"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr
        key = f'rate_limit_{client_ip}'
        
        requests = cache.get(key) or []
        now = time.time()
        
        # remove expired timestamps
        requests = [req for req in requests if req > now - RATE_LIMIT_PERIOD]
        
        if len(requests) >= RATE_LIMIT:
            return create_error_response(
                'Rate limit exceeded. Please try again later.',
                429,
                {'X-RateLimit-Limit': RATE_LIMIT,
                 'X-RateLimit-Remaining': 0,
                 'X-RateLimit-Reset': int(min(requests) + RATE_LIMIT_PERIOD - now)}
            )
        
        requests.append(now)
        cache.set(key, requests, timeout=RATE_LIMIT_PERIOD)
        
        return func(*args, **kwargs)
    return wrapper

def validate_pagination_params(func):
    """ensures page and per_page params are within acceptable ranges"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if page < 1:
            return create_error_response('Page number must be greater than 0', 400)
        if per_page < 1 or per_page > 100:
            return create_error_response('Per page must be between 1 and 100', 400)
            
        return func(*args, **kwargs)
    return wrapper

def validate_id_param(func):
    """validates plant/species IDs are within valid range"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        plant_id = kwargs.get('plant_id') or kwargs.get('species_id')
        if plant_id and (plant_id < 1 or plant_id > 1000000):
            return create_error_response('Invalid ID value', 400)
        return func(*args, **kwargs)
    return wrapper

def create_error_response(message, status_code, headers=None):
    """standardizes error response format across all endpoints"""
    response = jsonify({
        'error': str(message),
        'status_code': status_code,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    })
    response.status_code = status_code
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response

def create_success_response(data, message=None, status_code=200):
    """standardizes success response format across all endpoints"""
    response = {
        'status_code': status_code,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'data': data
    }
    if message:
        response['message'] = message
    if isinstance(data, list):
        response['count'] = len(data)
    return jsonify(response), status_code

# perenual api routes

@api_routes.route('/plants/fetch', methods=['GET'])
@rate_limit
@validate_pagination_params
def api_fetch_species():
    """fetches paginated plant species list from perenual"""
    try:
        page = request.args.get('page', 1, type=int)
        logger.debug(f"Request received to fetch species list for page: {page}")
        
        species_data = fetch_species_list(page)
        
        if not species_data:
            return create_error_response('No data found', 404)
            
        return create_success_response({
            'count': len(species_data),
            'page': page,
            'plants': species_data
        })
        
    except Exception as e:
        logger.error(f"Error in fetching species data: {e}", exc_info=True)
        return create_error_response(str(e), 500)

@api_routes.route('/plants/perenual/<int:plant_id>', methods=['GET'])
@rate_limit
@validate_id_param
def api_get_plant_from_api(plant_id):
    """fetches detailed plant info by ID from perenual"""
    try:
        logger.info(f"Fetching plant details from Perenual API for ID: {plant_id}")
        plant_data = fetch_plant_details_by_id(plant_id)
        
        if not plant_data:
            return create_error_response(f'Plant with ID {plant_id} not found', 404)
            
        return create_success_response(plant_data)
        
    except ValidationError as e:
        logger.error(f"Validation error for plant ID {plant_id}: {e.messages}")
        return create_error_response(e.messages, 422)
    except Exception as e:
        logger.error(f"Error fetching plant by ID {plant_id}: {e}", exc_info=True)
        return create_error_response(str(e), 500)

@api_routes.route('/plants/perenual/<int:species_id>/diseases', methods=['GET'])
@rate_limit
@validate_id_param
def api_get_plant_diseases(species_id):
    """fetches disease information for a specific plant species"""
    try:
        logger.info(f"Fetching diseases for species ID: {species_id}")
        diseases_data = fetch_plant_diseases(species_id)
        
        return create_success_response({
            'species_id': species_id,
            'diseases': diseases_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching diseases for species ID {species_id}: {e}", exc_info=True)
        return create_error_response(str(e), 500)

@api_routes.route('/plants/perenual/<int:species_id>/guides', methods=['GET'])
@rate_limit
@validate_id_param
def api_get_plant_guides(species_id):
    """fetches care guides for a plant species, optionally filtered by guide type"""
    try:
        guide_type = request.args.get('type')
        if guide_type and guide_type not in ['watering', 'sunlight', 'pruning', 'fertilizer']:
            return create_error_response('Invalid guide type', 400)
            
        logger.info(f"Fetching guides for species ID: {species_id}, type: {guide_type}")
        guides_data = fetch_plant_guides(species_id, guide_type)
        
        return create_success_response({
            'species_id': species_id,
            'guide_type': guide_type,
            'guides': guides_data
        })
        
    except Exception as e:
        logger.error(f"Error fetching guides for species ID {species_id}: {e}", exc_info=True)
        return create_error_response(str(e), 500)

@api_routes.route('/plants/perenual/random', methods=['GET'])
@rate_limit
def api_get_random_plant():
    """fetches a random plant from perenual's database"""
    try:
        logger.info("Fetching random plant")
        plant_data = fetch_random_plant()
        
        if not plant_data:
            return create_error_response('Failed to fetch random plant', 404)
            
        return create_success_response(plant_data)
        
    except Exception as e:
        logger.error(f"Error fetching random plant: {e}", exc_info=True)
        return create_error_response(str(e), 500)

# error handlers
@api_routes.errorhandler(404)
def not_found_error(error):
    return create_error_response('Resource not found', 404)

@api_routes.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return create_error_response('Internal server error', 500)

@api_routes.errorhandler(400)
def bad_request_error(error):
    return create_error_response('Bad request', 400)

@api_routes.errorhandler(429)
def rate_limit_error(error):
    return create_error_response('Too many requests', 429)

# local db crud routes

@api_routes.route('/plants', methods=['POST'])
def api_add_plant():
    """adds a new plant to local database"""
    data = request.json
    try:
        new_plant = add_plant(data)
        return jsonify({'message': 'Plant added successfully', 'plant': new_plant}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants', methods=['GET'])
def api_get_all_plants():
    """retrieves plants from local db with optional filtering and search"""
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    search_term = request.args.get('search', type=str)
    filters = request.args.get('filters', None)  # json object in query params
    try:
        result = find_all_plants_with_pagination(limit=limit, offset=offset, search_term=search_term, filters=filters)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants/<int:plant_id>', methods=['GET'])
def api_get_plant(plant_id):
    """retrieves a specific plant from local database"""
    try:
        plant = get_plant_by_any_id(plant_id)
        if plant:
            return jsonify(plant), 200
        else:
            return jsonify({'error': 'Plant not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants/<int:plant_id>', methods=['PUT'])
def api_update_plant(plant_id):
    """updates an existing plant in local database"""
    data = request.json
    try:
        updated_plant = update_plant_details(plant_id, data)
        return jsonify({'message': 'Plant updated successfully', 'plant': updated_plant}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants/<int:plant_id>', methods=['DELETE'])
def api_delete_plant(plant_id):
    """removes a plant from local database"""
    try:
        deleted_plant = remove_plant_from_db(plant_id)
        if deleted_plant:
            return jsonify({'message': 'Plant deleted successfully', 'plant': deleted_plant}), 200
        else:
            return jsonify({'error': 'Plant not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400