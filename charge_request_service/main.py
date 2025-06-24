from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

#docker url for load balancer
LOAD_BALANCER_URL = "http://load_balancer:5000/route"

@app.route('/')
def home():
    return "Charge request available", 200

#charge request to load balancer
@app.route('/charge', methods=['POST'])
def forward_charge_request():
    data = request.get_json()
    try:
        res = requests.post(LOAD_BALANCER_URL, json=data, timeout=3)
        return jsonify(res.json()), res.status_code
    except Exception as e:
        return jsonify({"error": "Load balancer not reachable", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
