# routes.py
from flask import Blueprint, request, render_template, redirect, url_for
from models import db, Plant
from utils.perennial_api import fetch_plant_data

main_routes = Blueprint('main', __name__)

@main_routes.route('/fetch_plant', methods=['GET', 'POST'])
def fetch_plant():
    if request.method == 'POST':
        plant_name = request.form['plant_name']
        data = fetch_plant_data(plant_name)
        if data:
            # Assuming data contains a list of plants
            for plant_info in data['plants']:
                plant = Plant(
                    common_name=plant_info.get('common_name'),
                    scientific_name=plant_info.get('scientific_name'),
                    watering_frequency=plant_info.get('watering').get('frequency'),
                    sunlight_requirements=plant_info.get('sunlight')
                )
                db.session.add(plant)
            db.session.commit()
            return redirect(url_for('main.view_plants'))
        else:
            return "Error fetching data from Perennial API", 500
    return render_template('fetch_plant.html')

# routes.py (continued)

@main_routes.route('/plants')
def view_plants():
    plants = Plant.query.all()
    return render_template('view_plants.html', plants=plants)

@main_routes.route('/plant/<int:plant_id>')
def view_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    return render_template('view_plant.html', plant=plant)

@main_routes.route('/plant/<int:plant_id>/edit', methods=['GET', 'POST'])
def edit_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    if request.method == 'POST':
        plant.common_name = request.form['common_name']
        plant.scientific_name = request.form['scientific_name']
        plant.watering_frequency = request.form['watering_frequency']
        plant.sunlight_requirements = request.form['sunlight_requirements']
        db.session.commit()
        return redirect(url_for('main.view_plant', plant_id=plant.id))
    return render_template('edit_plant.html', plant=plant)

@main_routes.route('/plant/<int:plant_id>/delete', methods=['POST'])
def delete_plant(plant_id):
    plant = Plant.query.get_or_404(plant_id)
    db.session.delete(plant)
    db.session.commit()
    return redirect(url_for('main.view_plants'))

# routes.py (continued)
import io
import base64
import matplotlib.pyplot as plt
from flask import Response

@main_routes.route('/analytics')
def analytics():
    df = get_plant_data()
    img = io.BytesIO()
    plt.figure(figsize=(10,6))
    df['watering_frequency'].hist()
    plt.title('Watering Frequency Distribution')
    plt.xlabel('Watering Frequency')
    plt.ylabel('Number of Plants')
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('analytics.html', plot_url=plot_url)
