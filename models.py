from app import db
from datetime import datetime
from enum import Enum

class CardCondition(Enum):
    MINT = "Mint"
    NEAR_MINT = "Near Mint"
    EXCELLENT = "Excellent"
    GOOD = "Good"
    PLAYED = "Played"
    POOR = "Poor"

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tcg_id = db.Column(db.String(50), nullable=False)
    page = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    condition = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'tcg_id': self.tcg_id,
            'page': self.page,
            'position': self.position,
            'condition': self.condition,
            'notes': self.notes
        }