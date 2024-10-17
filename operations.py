# operations.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Plant

# Create an engine that stores data in the local directory's plants.db file.
engine = create_engine('sqlite:///plants.db')

# Create all tables in the engine.
Base.metadata.create_all(engine)

# Create a configured "Session" class.
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

# operations.py (continued)
def get_all_plants():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants;")
    rows = cursor.fetchall()
    # Convert rows to list of dicts
    plants = [dict(row) for row in rows]
    cursor.close()
    conn.close()
    return plants

def get_plant_by_id(plant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plants WHERE id = %s;", (plant_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return dict(row)
    else:
        return None

def update_plant(plant_id, update_fields):
    # Implement update logic
    pass

def delete_plant(plant_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM plants WHERE id = %s;", (plant_id,))
    conn.commit()
    cursor.close()
    conn.close()

def store_plant_in_db(plant_record):
    conn = get_connection()
    cursor = conn.cursor()
    # Insert plant data
    insert_query = """
        INSERT INTO plants (id, common_name, scientific_name, other_name, family, origin)
        VALUES (%(id)s, %(common_name)s, %(scientific_name)s, %(other_name)s, %(family)s, %(origin)s)
        ON CONFLICT (id) DO UPDATE SET
            common_name = EXCLUDED.common_name,
            scientific_name = EXCLUDED.scientific_name,
            other_name = EXCLUDED.other_name,
            family = EXCLUDED.family,
            origin = EXCLUDED.origin;
    """
    cursor.execute(insert_query, plant_record)
    conn.commit()
    cursor.close()
    conn.close()
