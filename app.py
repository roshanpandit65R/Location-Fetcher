from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import requests
import os
import json

app = Flask(__name__)

# 🔥 Load Firebase from ENV (Render compatible)
firebase_json = os.environ.get("FIREBASE_CONFIG")

if not firebase_json:
    raise Exception("FIREBASE_CONFIG not found in environment variables")

cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/location', methods=['POST'])
def location():
    try:
        data = request.get_json()

        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not latitude or not longitude:
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

        # 🌍 Reverse Geocoding (OpenStreetMap)
        address = None
        try:
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                "format": "json",
                "lat": latitude,
                "lon": longitude
            }
            response = requests.get(
                url,
                params=params,
                headers={'User-Agent': 'FlaskApp/1.0'}
            )

            if response.status_code == 200:
                result = response.json()
                address = result.get('display_name')

        except Exception as e:
            print(f"Geocoding error: {e}")

        # 🔥 Store in Firebase
        doc_ref = db.collection('locations').document()
        doc_ref.set({
            'latitude': latitude,
            'longitude': longitude,
            'address': address,
            'timestamp': datetime.datetime.utcnow()
        })

        print(f"Stored: {latitude}, {longitude}")

        return jsonify({
            'status': 'success',
            'address': address
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ✅ Health check (important for Render)
@app.route('/health')
def health():
    return "OK", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
