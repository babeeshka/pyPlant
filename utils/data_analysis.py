# utils/data_analysis.py
import pandas as pd
from models import Plant

def get_plant_data():
    # Query all plants
    plants = Plant.query.all()
    # Convert to DataFrame
    data = [{
        'common_name': plant.common_name,
        'watering_frequency': plant.watering_frequency,
        'sunlight_requirements': plant.sunlight_requirements
    } for plant in plants]
    df = pd.DataFrame(data)
    return df

def analyze_watering_frequency():
    df = get_plant_data()
    analysis = df['watering_frequency'].describe()
    return analysis
