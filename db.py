import snowflake.connector
from config import (
    SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
)

def get_connection():
    """
    Establish a connection to the Snowflake database using credentials from the config
    """
    try:
        ctx = snowflake.connector.connect(
            user=SNOWFLAKE_USER,
            password=SNOWFLAKE_PASSWORD,
            account=SNOWFLAKE_ACCOUNT,
            warehouse=SNOWFLAKE_WAREHOUSE,
            database=SNOWFLAKE_DATABASE,
            schema=SNOWFLAKE_SCHEMA
        )
        print("Successfully connected to Snowflake.")
        return ctx
    except Exception as e:
        print(f"Error establishing Snowflake connection: {e}")
        raise

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Drop the existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS plants")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY,
                common_name STRING NOT NULL,
                scientific_name ARRAY,
                other_name ARRAY,
                family STRING,
                origin ARRAY,
                type STRING,
                dimension STRING,
                dimensions OBJECT,
                cycle STRING,
                watering STRING,
                sunlight ARRAY,
                propagation ARRAY,
                hardiness OBJECT,
                hardiness_location OBJECT,
                growth_rate STRING,
                drought_tolerant BOOLEAN,
                salt_tolerant BOOLEAN,
                thorny BOOLEAN,
                invasive BOOLEAN,
                tropical BOOLEAN,
                indoor BOOLEAN,
                care_level STRING,
                pest_susceptibility ARRAY,
                flowers BOOLEAN,
                flowering_season STRING,
                flower_color STRING,
                cones BOOLEAN,
                fruits BOOLEAN,
                edible_fruit BOOLEAN,
                edible_fruit_taste_profile STRING,
                fruit_nutritional_value STRING,
                fruit_color ARRAY,
                harvest_season STRING,
                leaf BOOLEAN,
                leaf_color ARRAY,
                edible_leaf BOOLEAN,
                cuisine BOOLEAN,
                medicinal BOOLEAN,
                poisonous_to_humans BOOLEAN,
                poisonous_to_pets BOOLEAN,
                description STRING,
                default_image OBJECT,
                care_guides STRING,
                volume_water_requirement ARRAY,
                depth_water_requirement ARRAY,
                pruning_month ARRAY,
                pruning_count ARRAY,
                watering_period STRING,
                watering_general_benchmark OBJECT,
                maintenance STRING,
                plant_anatomy ARRAY,
                seeds INTEGER,
                other_images STRING
            );
        """)

        conn.commit()
        print("Successfully created tables.")

    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        create_tables()
    except Exception as e:
        print(f"Failed to create tables: {e}")