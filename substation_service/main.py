from flask import Flask, request, jsonify
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST
import threading
import time

app = Flask(__name__)

#prometheus metric for active charging sessions
current_load_gauge = Gauge('substation_current_load', 'Current EV charging load at substation')

active_vehicles = []
lock = threading.Lock()

CHARGING_DURATION = 30

@app.route('/')
def home():
    return "Substation Service Running", 200

#handling vehicle charging request
@app.route('/charge', methods=['POST'])
def charge_vehicle():
    data = request.get_json()
    vehicle_id = data.get('vehicle_id', 'unknown')

    def simulate_charging():
        with lock:
            active_vehicles.append(vehicle_id)
            current_load_gauge.inc()

        time.sleep(CHARGING_DURATION)

        with lock:
            active_vehicles.remove(vehicle_id)
            current_load_gauge.dec()

    threading.Thread(target=simulate_charging).start()
    return jsonify({"status": "charging started", "vehicle_id": vehicle_id}), 202

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
