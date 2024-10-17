# services/plant_service.py
import logging
from models import Plant, session
from schemas import PlantSchema
from marshmallow import ValidationError
from services.perenual_service import fetch_plant_details_by_id, fetch_random_plant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plant_schema = PlantSchema()

# add a new plant to the database
def add_plant(data):
    try:
        # Validate incoming data
        validated_data = plant_schema.load(data)

        # Map validated data to the Plant model
        new_plant = Plant(**validated_data)

        # Add to session and commit to database
        session.add(new_plant)
        session.commit()

        logger.info(f"Successfully added plant: {new_plant.common_name}")
        return new_plant
    except ValidationError as e:
        logger.error(f"Validation error while adding plant: {e.messages}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error adding plant to database: {e}")
        raise

# find all plants with pagination
def find_all_plants_with_pagination(limit=10, offset=0, search_term=None, filters=None):
    try:
        query = session.query(Plant)

        #  search term if available
        if search_term:
            query = query.filter(Plant.common_name.ilike(f"%{search_term}%"))

        #  additional filters if available
        if filters:
            for key, value in filters.items():
                query = query.filter(getattr(Plant, key) == value)

        #  pagination
        total_count = query.count()
        plants = query.limit(limit).offset(offset).all()

        logger.info(f"Retrieved {len(plants)} plants with pagination.")
        return {'plants': [plant.__dict__ for plant in plants], 'count': total_count}
    except Exception as e:
        logger.error(f"Error retrieving plants with pagination: {e}")
        raise

# fetch plant by API ID from the database
def get_plant_by_any_id(plant_id):
    try:
        logger.info(f"Fetching plant with ID: {plant_id}")
        plant = session.query(Plant).filter(Plant.id == plant_id).first()

        if plant:
            logger.info(f"Plant found: {plant.common_name}")
            return plant
        else:
            logger.warning(f"Plant with ID {plant_id} not found.")
            return None
    except Exception as e:
        logger.error(f"Error fetching plant with ID {plant_id}: {e}")
        raise

# update plant details in the database
def update_plant_details(api_id, update_data):
    try:
        plant = get_plant_by_any_id(api_id)

        if not plant:
            raise ValueError(f"Plant with ID {api_id} not found.")

        validated_update_data = plant_schema.load(update_data, partial=True)

        for key, value in validated_update_data.items():
            if hasattr(plant, key):
                setattr(plant, key, value)

        session.commit()
        logger.info(f"Successfully updated plant with ID {api_id}")
        return plant
    except ValidationError as e:
        logger.error(f"Validation error while updating plant: {e.messages}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating plant with ID {api_id}: {e}")
        raise

# remove plant from the database
def remove_plant_from_db(api_id):
    try:
        plant = get_plant_by_any_id(api_id)

        if not plant:
            logger.warning(f"Plant with ID {api_id} not found for deletion.")
            return None

        session.delete(plant)
        session.commit()

        logger.info(f"Successfully removed plant with ID {api_id}")
        return plant
    except Exception as e:
        session.rollback()
        logger.error(f"Error removing plant with ID {api_id}: {e}")
        raise

# fetch a random plant and add to the database (example use case)
def add_random_plant():
    try:
        random_plant_data = fetch_random_plant()

        new_plant = add_plant(random_plant_data)
        return new_plant
    except Exception as e:
        logger.error(f"Error adding random plant to the database: {e}")
        raise
