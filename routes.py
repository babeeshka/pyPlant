# routes.py
from flask import Blueprint, request, jsonify
from services.plant_service import (
    add_plant,
    find_all_plants_with_pagination,
    get_plant_by_any_id,
    update_plant_details,
    remove_plant_from_db
)
from services.perenual_service import fetch_species_list, fetch_plant_details_by_id
import logging

api_routes = Blueprint('api', __name__)

logging.basicConfig(level=logging.DEBUG)  # Set logging level to DEBUG for troubleshooting
logger = logging.getLogger(__name__)

# Fetch plant data from Perenual API
@api_routes.route('/plants/fetch', methods=['GET'])
def api_fetch_species():
    page = request.args.get('page', 1, type=int)
    
    logger.debug(f"Request received to fetch species list for page: {page}")
    
    try:
        species_data = fetch_species_list(page)
        
        if species_data:
            logger.debug(f"Species Data Retrieved: {species_data}")
            return jsonify({'count': len(species_data), 'plants': species_data}), 200
        else:
            logger.error("No data retrieved or data was empty.")
            return jsonify({'error': 'No data found'}), 404
    except Exception as e:
        logger.error(f"Error in fetching species data: {e}")
        return jsonify({'error': str(e)}), 500

# Fetch plant by ID from the Perenual API only
@api_routes.route('/plants/perenual/<int:plant_id>', methods=['GET'])
def api_get_plant_from_api(plant_id):
    try:
        logger.info(f"Fetching plant details from Perenual API for ID: {plant_id}")
        plant_data = fetch_plant_details_by_id(plant_id)
        
        if plant_data:
            logger.info(f"Fetched plant data from Perenual API for ID: {plant_id}")
            return jsonify(plant_data), 200
        else:
            logger.error(f"Plant with ID {plant_id} not found in Perenual API.")
            return jsonify({'error': 'Plant not found in Perenual API'}), 404

    except Exception as e:
        logger.error(f"Error fetching plant by ID {plant_id} from Perenual API: {e}")
        return jsonify({'error': str(e)}), 500

# CRUD operations on plants
@api_routes.route('/plants', methods=['POST'])
def api_add_plant():
    data = request.json
    try:
        new_plant = add_plant(data)
        return jsonify({'message': 'Plant added successfully', 'plant': new_plant}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants', methods=['GET'])
def api_get_all_plants():
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    search_term = request.args.get('search', type=str)
    filters = request.args.get('filters', None)  # Assuming filters are passed as a JSON object in query params
    try:
        result = find_all_plants_with_pagination(limit=limit, offset=offset, search_term=search_term, filters=filters)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants/<int:plant_id>', methods=['GET'])
def api_get_plant(plant_id):
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
    data = request.json
    try:
        updated_plant = update_plant_details(plant_id, data)
        return jsonify({'message': 'Plant updated successfully', 'plant': updated_plant}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api_routes.route('/plants/<int:plant_id>', methods=['DELETE'])
def api_delete_plant(plant_id):
    try:
        deleted_plant = remove_plant_from_db(plant_id)
        if deleted_plant:
            return jsonify({'message': 'Plant deleted successfully', 'plant': deleted_plant}), 200
        else:
            return jsonify({'error': 'Plant not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400