from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from dotenv import load_dotenv
import os, logging

load_dotenv()
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if os.path.exists(UPLOAD_FOLDER) and not os.path.isdir(UPLOAD_FOLDER):
    logging.warning(f"'{UPLOAD_FOLDER}' exists and is not a directory. Removing it.")
    os.remove(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client['image_analysis']
    collection = db['results']
except Exception as e:
    logging.error(f"MongoDB connection failed: {e}")
    collection = None

@app.route('/')
def home():
    return "Server running!"

@app.route('/analyze', methods=['POST'])
def analyze():
    print("Received request at /analyze")
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']
    filename = secure_filename(file.filename)
    if not filename:
        return jsonify({'error': 'Invalid filename'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    result = {"filename": filename, "message": "Analysis complete!"}
    if collection:
        collection.insert_one(result)

    return jsonify(result), 200
