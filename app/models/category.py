from app.extensions import db

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    produtos = db.relationship('Product', backref='categoria', lazy=True)