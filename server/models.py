from database import db 
import datetime 

class WaterLevel(db.Model):
    __tablename__ = 'water_level'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    level_pct = db.Column(db.Float, nullable=False)
    pump_status = db.Column(db.String, default = "off", nullable = False)
    
    def __init__(self, level_pct, pump_status):
        self.level_pct = level_pct 
        self.pump_status = pump_status
        
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'level_pct': self.level_pct,
            'pump_status': self.pump_status
        }
        
    def __repr__(self):
        return f'<WaterLevel: Reading:{self.id} at: {self.timestamp} is {self.level_pct}>'