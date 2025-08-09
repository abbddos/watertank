from database import db 
import datetime 

class WaterLevel(db.Model):
    __tablename__ = 'water_level'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    level_pct = db.Column(db.Float, nullable=False)
    
    def __init__(self, level_pct):
        self.level_pct = level_pct 
        
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'level_pct': self.level_pct
        }
        
    def __repr__(self):
        return f'<WaterLevel: Reading:{self.id} at: {self.timestamp} is {self.level_pct}>'