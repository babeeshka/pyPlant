# db.py
import snowflake.connector
from config import (
    SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT,
    SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
)

def get_connection():
    ctx = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    return ctx

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    # Create plants table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plants (
            id INTEGER PRIMARY KEY,
            common_name STRING,
            scientific_name STRING,
            other_name ARRAY,
            family STRING,
            origin STRING,
            -- Add more columns as needed
        );
    """)
    # Create care_instructions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS care_instructions (
            plant_id INTEGER,
            watering STRING,
            sunlight STRING,
            soil STRING,
            FOREIGN KEY (plant_id) REFERENCES plants(id)
        );
    """)
    # Commit and close
    conn.commit()
    cursor.close()
    conn.close()
