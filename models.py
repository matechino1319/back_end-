from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False, index=True)
    nationality = db.Column(db.String(80), nullable=True, index=True)
    position = db.Column(db.String(40), nullable=True, index=True)  # Arquero/Defensor/Mediocampista/Delantero
    club = db.Column(db.String(120), nullable=True, index=True)

    age = db.Column(db.Integer, nullable=True)
    preferred_foot = db.Column(db.String(20), nullable=True)        # Izquierdo/Derecho/Ambidiestro
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    matches = db.Column(db.Integer, nullable=True, default=0)
    goals = db.Column(db.Integer, nullable=True, default=0)
    assists = db.Column(db.Integer, nullable=True, default=0)
    minutes = db.Column(db.Integer, nullable=True, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "nationality": self.nationality,
            "position": self.position,
            "club": self.club,
            "age": self.age,
            "preferred_foot": self.preferred_foot,
            "active": self.active,
            "matches": self.matches,
            "goals": self.goals,
            "assists": self.assists,
            "minutes": self.minutes,
        }