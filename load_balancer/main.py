from flask import Flask, request, jsonify
import threading
import time
import requests
import re

app = Flask(__name__)

#substations endpoints
SUBSTATIONS = {
    "substation1": "http://substation1:5001",
    "substation2": "http://substation2:5001",
    "substation3": "http://substation3:5001"
}

#current load for each substation in a shared dict.
substation_loads = {name: float('inf') for name in SUBSTATIONS}
lock = threading.Lock()

#parsing the metric 
LOAD_METRIC_NAME = "substation_current_load"
metric_pattern = re.compile(rf'{LOAD_METRIC_NAME}.*\s+(\d+\.?\d*)')

#backround thread to poll /metrics from substations
def poll_metrics():
    while True:
        with lock:
            for name, url in SUBSTATIONS.items():
                try:
                    res = requests.get(f"{url}/metrics", timeout=2)
                    match = metric_pattern.search(res.text)
                    if match:
                        substation_loads[name] = float(match.group(1))
                    else:
                        substation_loads[name] = float('inf')
                except:
                    substation_loads[name] = float('inf')
        time.sleep(5)

@app.route('/')
def home():
    return "Load Balancer Running", 200

#routing incoming requests to the least loaded substation
@app.route('/route', methods=['POST'])
def route_request():
    data = request.get_json()
    vehicle_id = data.get("vehicle_id")

    with lock:
        best_substation = min(substation_loads, key=substation_loads.get)
        target_url = f"{SUBSTATIONS[best_substation]}/charge"

    try:
        forward_res = requests.post(target_url, json={"vehicle_id": vehicle_id}, timeout=3)
        return jsonify({
            "routed_to": best_substation,
            "response": forward_res.json()
        }), forward_res.status_code
    except Exception as e:
        return jsonify({"error": "Failed to forward request", "details": str(e)}), 500

if __name__ == '__main__':
    threading.Thread(target=poll_metrics, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
