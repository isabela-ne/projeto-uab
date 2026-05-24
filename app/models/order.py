from app.extensions import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = 'orders'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status       = db.Column(db.String(30), default='aguardando_pagamento', nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    total        = db.Column(db.Float, nullable=False)

    # Endereço
    endereco_rua     = db.Column(db.String(200), nullable=False)
    endereco_numero  = db.Column(db.String(20), nullable=False)
    endereco_bairro  = db.Column(db.String(100), nullable=False)
    endereco_cidade  = db.Column(db.String(100), nullable=False)
    endereco_estado  = db.Column(db.String(2), nullable=False)
    endereco_cep     = db.Column(db.String(9), nullable=False)

    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    items        = db.relationship('OrderItem', backref='order', lazy=True)
    user         = db.relationship('User', backref='orders')

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    product    = db.relationship('Product')