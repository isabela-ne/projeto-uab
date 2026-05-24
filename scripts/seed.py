import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product

app = create_app()
with app.app_context():
    db.create_all()
    # Admin
    if not User.query.filter_by(email='admin@pokeshop.local').first():
        admin = User(nome='Administrador', email='admin@pokeshop.local', role='Administrador')
        admin.set_password('Admin@2026!')
        db.session.add(admin)
    # Categorias
    cats = ['Cartas', 'Action Figures', 'Vestuário', 'Acessórios']
    cat_objs = {}
    for c in cats:
        if not Category.query.filter_by(nome=c).first():
            obj = Category(nome=c); db.session.add(obj); cat_objs[c] = obj
        else:
            cat_objs[c] = Category.query.filter_by(nome=c).first()
    db.session.flush()
    # Produtos
    produtos = [
        ('Pikachu VMAX', 'Carta rara holográfica VMAX', 89.90, 15, 'Cartas'),
        ('Charizard GX', 'Carta ultra rara GX', 249.90, 5, 'Cartas'),
        ('Action Figure Mewtwo', 'Boneco articulado 15cm', 129.90, 8, 'Action Figures'),
        ('Camiseta Pokémon', 'Camiseta 100% algodão', 59.90, 20, 'Vestuário'),
        ('Mochila Pokeball', 'Mochila temática 30L', 149.90, 10, 'Acessórios'),
    ]
    for nome, desc, preco, estoque, cat in produtos:
        if not Product.query.filter_by(nome=nome).first():
            p = Product(nome=nome, descricao=desc, preco=preco,
                       estoque=estoque, categoria_id=cat_objs[cat].id)
            db.session.add(p)
    db.session.commit()
    print('Seed executado com sucesso!')