from flask import Flask, request, jsonify
from flask_cors import CORS 
from models import WaterLevel 
from database import db, init_db 
from config import Config 
import json 
import paho.mqtt.client as mqtt 
from datetime import datetime
import os 
import threading 

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

CORS(app, resources={r"/*": {"origins": Config.CORS_ORIGINS}})

mqtt_client = mqtt.Client(client_id="FlaskAPI") 


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the broker."""
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Failed to connect, return code {rc}\n")
        
        
mqtt_client.on_connect = on_connect
mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_start()


@app.route('/data', methods = ['POST'])
def receive_data():
    """
    Receives water level data from the simulator via HTTP POST,
    stores it in the database, and publishes a command if needed.
    """
    
    data = request.get_json()
    if not data or 'level_pct' not in data:
        return jsonify({"error":"Invalid data format"}), 400 
    
    try: 
        level = data['level_pct']
        latest_entry = WaterLevel.query.order_by(WaterLevel.timestamp.desc()).first()
        last_pump_status = latest_entry.pump_status if latest_entry else "off"
        
        pump_command  = None
        current_pump_status = last_pump_status
        
        if level <= 50 and last_pump_status != "on":
            pump_command = {"action":"on"}
            current_pump_status = "on"
            
        elif level >= 100 and last_pump_status !="off":
            pump_command = {"action":"off"}
            current_pump_status = "off"
               
        if pump_command:
            mqtt_client.publish("water_tank/pump_control", json.dumps(pump_command))
            
        new_entry = WaterLevel(level_pct = level, pump_status = current_pump_status)
        db.session.add(new_entry)
        db.session.commit()
            
        return jsonify(new_entry.to_dict()), 200
    
    except Exception as e:
        db.session.rollback()
        print(f'Error processing data: {str(e)}')
        return jsonify({"error": str(e)}), 500 
    
    
@app.route('/data/latest', methods = ['GET'])
def get_latest_data():
    """
    Returns the most recent water level reading for the front-end to display.
    """
    
    latest_entry = WaterLevel.query.order_by(WaterLevel.timestamp.desc()).first()
    if latest_entry:
        return jsonify(latest_entry.to_dict()), 200
    else:
        return jsonify({"message":"data not found"}), 404 
    
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)