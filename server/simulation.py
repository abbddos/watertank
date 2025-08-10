import requests 
import time 
import json 
import random 

API_URL = "http://127.0.0.1:5000/data"
API_URL_LATEST = "http://127.0.0.1:5000/data/latest"

UPDATE_INTERVAL = 5 
FILL_AMOUNT = 5
EMPTY_AMOUNT = 2
current_level = random.uniform(20.0, 80.0)

def send_data(level):
    """Sends the simulated water level data to the Flask API."""
    data = {"level_pct": level}
    try:
        response = requests.post(API_URL, json = data)
        response.raise_for_status() 
        
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to API: {e}")
        
        
def get_latest_data():
    """Fetches the latest data from the API and returns it."""
    try:
        response = requests.get(API_URL_LATEST)
        response.raise_for_status() # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching latest data from API: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing data from API: Missing key {e}")
        return None
        
        
def simulate_flow(current_level):
    """
    Simulates water level changes based on the pump status from the API.
    """
    latest_data = get_latest_data()
    
    if latest_data and 'pump_status' in latest_data:
        pump_status = latest_data["pump_status"]
        print(f"Latest API data: Level={latest_data['level_pct']:.2f}%, Pump Status={pump_status}  @ {latest_data['timestamp']}")
        
        if pump_status == "on":
            new_level = current_level + FILL_AMOUNT
        else:
            new_level = current_level - EMPTY_AMOUNT
            
        if new_level >= 100:
            new_level = 100
        elif new_level <= 0:
            new_level = 0
            
        send_data(new_level)
        return new_level
    
    else:
        # If API is not reachable or no data, just decrease level to simulate usage
        print("API not reachable or no data, simulating tank emptying.")
        new_level = current_level - EMPTY_AMOUNT
        if new_level <= 0:
            new_level = 0
            
        send_data(new_level)
        return new_level
    
    
if __name__ == "__main__":
    print("Water Tank Simulator V2")
    print("--------------------")
    print("This script will now simulate a continuous water level change.")
    print("It will check the API's pump status to decide whether to fill or empty.")
    
    # We now handle the KeyboardInterrupt gracefully
    try:
        while True:
            current_level = simulate_flow(current_level)
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
        