from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Correct configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return "Welcome to the Quiz App"


if __name__ == "__main__":
    app.run(debug=True)
