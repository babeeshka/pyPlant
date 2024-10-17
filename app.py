# app.py
from flask import Flask
from routes import api_routes

app = Flask(__name__)

#  register the API routes blueprint
app.register_blueprint(api_routes, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)

