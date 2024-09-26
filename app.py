# app.py
from flask import Flask
from routes import main_routes

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
