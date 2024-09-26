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

def add_plant(name, species, age):
    new_plant = Plant(name=name, species=species, age=age)
    session.add(new_plant)
    session.commit()

def get_plants():
    return session.query(Plant).all()

def update_plant(plant_id, **kwargs):
    plant = session.query(Plant).filter(Plant.id == plant_id).first()
    if plant:
        for key, value in kwargs.items():
            setattr(plant, key, value)
        session.commit()
        print("Plant updated successfully!")
    else:
        print(f"No plant found with ID {plant_id}.")

def delete_plant(plant_id):
    plant = session.query(Plant).filter(Plant.id == plant_id).first()
    if plant:
        session.delete(plant)
        session.commit()
        print("Plant deleted successfully!")
    else:
        print(f"No plant found with ID {plant_id}.")
