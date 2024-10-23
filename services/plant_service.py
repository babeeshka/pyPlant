import logging
import json
from db import get_connection
from schemas import PlantSchema
from marshmallow import ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plant_schema = PlantSchema()

def add_plant(data):
    try:
        validated_data = plant_schema.load(data)
        conn = get_connection()
        cursor = conn.cursor()

        # Fields that should be arrays in Snowflake
        array_fields = [
            "scientific_name", "other_name", "origin", "sunlight",
            "propagation", "pest_susceptibility", "fruit_color", 
            "leaf_color", "pruning_month", "pruning_count",
            "volume_water_requirement", "depth_water_requirement"
        ]

        # Fields that should be objects in Snowflake
        object_fields = [
            "hardiness", "hardiness_location", "dimensions",
            "default_image", "watering_general_benchmark", 
            "plant_anatomy"
        ]

        final_values = {}
        fields = []
        values = []

        for key, value in validated_data.items():
            fields.append(key)
            
            if key in array_fields:
                if value and len(value) > 0:
                    # Create named parameters for each array element
                    array_params = [f"%({key}_{i})s" for i in range(len(value))]
                    values.append(f"ARRAY_CONSTRUCT({','.join(array_params)})")
                    for i, item in enumerate(value):
                        final_values[f"{key}_{i}"] = item
                else:
                    values.append("ARRAY_CONSTRUCT()")
            elif key in object_fields:
                if value is None:
                    value = {}
                values.append(f"PARSE_JSON(%({key})s)")
                final_values[key] = json.dumps(value)
            else:
                values.append(f"%({key})s")
                final_values[key] = value

        sql = f"""
            INSERT INTO plants ({', '.join(fields)})
            VALUES ({', '.join(values)})
        """

        logger.debug(f"SQL Query: {sql}")
        logger.debug(f"Values: {final_values}")

        cursor.execute(sql, final_values)
        conn.commit()

        cursor.close()
        conn.close()

        return validated_data

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logger.error(f"Error adding plant: {str(e)}")
        raise e

# Find all plants with pagination
def find_all_plants_with_pagination(limit=10, offset=0, search_term=None, filters=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM plants"
        query_conditions = []
        query_params = {}

        # Search term if available
        if search_term:
            query_conditions.append("common_name ILIKE %(search_term)s")
            query_params['search_term'] = f"%{search_term}%"

        # Additional filters if available
        if filters:
            for key, value in filters.items():
                query_conditions.append(f"{key} = %({key})s")
                query_params[key] = value

        # Add conditions to the query
        if query_conditions:
            query += " WHERE " + " AND ".join(query_conditions)

        # Add pagination
        query += " LIMIT %(limit)s OFFSET %(offset)s"
        query_params['limit'] = limit
        query_params['offset'] = offset

        cursor.execute(query, query_params)
        rows = cursor.fetchall()
        plants = [dict(zip([desc[0] for desc in cursor.description], row))
                  for row in rows]

        # Count total
        cursor.execute("SELECT COUNT(*) FROM plants")
        total_count = cursor.fetchone()[0]

        logger.info(f"Retrieved {len(plants)} plants with pagination.")
        return {'plants': plants, 'count': total_count}

    except Exception as e:
        logger.error(f"Error retrieving plants with pagination: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Fetch plant by ID from the database
def get_plant_by_any_id(plant_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM plants WHERE id = %s", (plant_id,))
        row = cursor.fetchone()

        if row:
            plant_data = dict(zip([desc[0]
                              for desc in cursor.description], row))
            logger.info(f"Plant found: {plant_data['common_name']}")
            return plant_data
        else:
            logger.warning(f"Plant with ID {plant_id} not found.")
            return None

    except Exception as e:
        logger.error(f"Error fetching plant with ID {plant_id}: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Update plant details in the database
def update_plant_details(api_id, update_data):
    try:
        plant = get_plant_by_any_id(api_id)

        if not plant:
            raise ValueError(f"Plant with ID {api_id} not found.")

        validated_update_data = plant_schema.load(update_data, partial=True)

        conn = get_connection()
        cursor = conn.cursor()

        # Generate update statements dynamically
        update_statements = ", ".join(
            [f"{key} = %({key})s" for key in validated_update_data.keys()])
        validated_update_data['id'] = api_id

        cursor.execute(f"""
            UPDATE plants
            SET {update_statements}
            WHERE id = %(id)s;
        """, validated_update_data)

        conn.commit()
        logger.info(f"Successfully updated plant with ID {api_id}")
        return validated_update_data

    except ValidationError as e:
        logger.error(f"Validation error while updating plant: {e.messages}")
        raise
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logger.error(f"Error updating plant with ID {api_id}: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Remove plant from the database
def remove_plant_from_db(api_id):
    try:
        plant = get_plant_by_any_id(api_id)

        if not plant:
            logger.warning(f"Plant with ID {api_id} not found for deletion.")
            return None

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM plants WHERE id = %s", (api_id,))
        conn.commit()

        logger.info(f"Successfully removed plant with ID {api_id}")
        return plant

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        logger.error(f"Error removing plant with ID {api_id}: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# Fetch a random plant and add to the database (example use case)
def add_random_plant():
    try:
        random_plant_data = fetch_random_plant()
        new_plant = add_plant(random_plant_data)
        return new_plant
    except Exception as e:
        logger.error(f"Error adding random plant to the database: {e}")
        raise
