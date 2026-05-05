from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import requests

# Initialize Firebase
cred = credentials.Certificate('esr-solar-data-firebase-adminsdk-fbsvc-650d2bf69f.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/location', methods=['POST'])
def location():
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # Reverse geocode to get address
    address = None
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
        response = requests.get(url, headers={'User-Agent': 'FlaskApp/1.0'})
        if response.status_code == 200:
            result = response.json()
            address = result.get('display_name')
    except Exception as e:
        print(f"Error geocoding: {e}")
    
    # Store in Firebase
    doc_ref = db.collection('locations').document()
    doc_ref.set({
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'timestamp': datetime.datetime.now()
    })
    print(f"Location stored: Latitude {latitude}, Longitude {longitude}, Address: {address}")
    return jsonify({'status': 'success', 'address': address})

if __name__ == '__main__':
    app.run(debug=True)