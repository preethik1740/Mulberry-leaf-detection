from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import psycopg2
import os

app = Flask(__name__)

# Load your trained model
MODEL_PATH = "leaf_disease_model.h5"
model = load_model(MODEL_PATH)

# Define your image classes (adjust these based on your training)
CLASS_NAMES = ["Healthy", "Leaf Rust", "Leaf Spot"]

# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="sericulture",
        user="postgres",
        password="password"
    )

@app.route('/')
def home():
    return "Sericulture API is running 🚀"

# 1️⃣ Leaf disease prediction
@app.route('/predict', methods=['POST'])
def predict_leaf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'})

    file = request.files['file']
    file_path = os.path.join('static/uploads', file.filename)
    file.save(file_path)

    # Preprocess image
    img = image.load_img(file_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    predictions = model.predict(img_array)
    predicted_class = CLASS_NAMES[np.argmax(predictions)]

    return jsonify({'prediction': predicted_class})

# 2️⃣ Fetch cocoon price data
@app.route('/prices', methods=['GET'])
def get_prices():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cocoon_prices ORDER BY date DESC LIMIT 50;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    prices = []
    for row in rows:
        prices.append({
            'date': str(row[0]),
            'district': row[1],
            'price': row[2]
        })
    return jsonify(prices)

if __name__ == "__main__":
    os.makedirs('static/uploads', exist_ok=True)
    app.run(debug=True)
