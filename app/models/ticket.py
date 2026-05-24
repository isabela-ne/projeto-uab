from app.extensions import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assunto = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='Aberto')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    mensagens = db.relationship('TicketMessage', backref='ticket', lazy=True)
    usuario = db.relationship('User', backref='tickets')

class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    autor = db.relationship('User')