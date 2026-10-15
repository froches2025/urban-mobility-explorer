from flask_cors import CORS
from flask import Flask, jsonify, request
from spatial_utils import filter_zones_by_radius
from db import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/api/trips', methods=['GET'])
def get_trips():
    conn = get_db_connection()
    query = "SELECT * FROM trips WHERE 1=1"
    params = []
    
    min_dist = request.args.get('min_distance')
    if min_dist:
        query += " AND distance >= ?"
        params.append(float(min_dist))
        
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

@app.route('/api/zones/nearby', methods=['GET'])
def get_nearby_zones():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    radius = request.args.get('radius', 5)  # Default radius is 5
    
    if not all([lat, lon, radius]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    lat = float(lat)
    lon = float(lon)
    radius = float(radius)
    
    conn = get_db_connection()
    cursor = conn.execute("SELECT id, name, latitude as lat, longitude as lon FROM taxi_zone_lookup")
    zones = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    filtered_zones = filter_zones_by_radius(zones, lat, lon, radius)
    return jsonify(filtered_zones)

if __name__ == '__main__':
    app.run(debug=True, port=5000)