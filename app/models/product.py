from app.extensions import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    estoque = db.Column(db.Integer, default=0, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    def is_available(self):
        return self.estoque > 0