from app.extensions import db
from datetime import datetime

class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    desconto_pct = db.Column(db.Float, nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    validade = db.Column(db.DateTime)

    def is_valido(self):
        if not self.ativo:
            return False
        if self.validade and self.validade < datetime.utcnow():
            return False
        return True
