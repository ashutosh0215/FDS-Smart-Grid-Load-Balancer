import requests
import time
import random

URL = "http://localhost:4000/charge"

#simulating 'rush hour' charging requests
def simulate_charging():
    while True:
        try:
            payload = {"ev_id": f"EV{random.randint(1000, 9999)}"}
            response = requests.post(URL, json=payload)
            print(f"[SENT] {payload} → {response.status_code}: {response.text}")
        except Exception as e:
            print(f"[ERROR] {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    simulate_charging()
