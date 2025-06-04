from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Estimate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100))
    project_address = db.Column(db.String(200))
    labor_cost = db.Column(db.Float)
    materials = db.relationship('Material', backref='estimate', lazy=True)
    signature = db.Column(db.Text, nullable=True)  # Store base64 signature data
    signature_date = db.Column(db.DateTime, nullable=True)
    project_title = db.Column(db.String(200), nullable=True)
    project_manager = db.Column(db.String(100), nullable=True)
    project_location = db.Column(db.String(200), nullable=True)
    additional_costs = db.relationship('AdditionalCost', backref='estimate', lazy=True)
    estimate_date = db.Column(db.DateTime, default=datetime.now)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    estimate_id = db.Column(db.Integer, db.ForeignKey('estimate.id'))
    types = db.relationship('MaterialType', backref='material', lazy=True)

class MaterialType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(50))
    type = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    unit_price = db.Column(db.Float)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'))

class AdditionalCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200))
    amount = db.Column(db.Float)
    estimate_id = db.Column(db.Integer, db.ForeignKey('estimate.id'))