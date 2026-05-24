import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_seed():
    from app.extensions import db
    from app.models.user import User
    from app.models.category import Category
    from app.models.product import Product

    from app.models.ticket import Ticket, TicketMessage

    db.create_all()

    if not User.query.filter_by(email='admin@pokeshop.local').first():
        admin = User(nome='Administrador', email='admin@pokeshop.local', role='Administrador')
        admin.set_password('Admin@2026!')
        db.session.add(admin)

    cats = ['Cartas', 'Action Figures', 'Vestuário', 'Acessórios']
    cat_objs = {}
    for c in cats:
        if not Category.query.filter_by(nome=c).first():
            obj = Category(nome=c)
            db.session.add(obj)
            cat_objs[c] = obj
        else:
            cat_objs[c] = Category.query.filter_by(nome=c).first()
    db.session.flush()

    produtos = [
        ('Pikachu VMAX', 'Carta rara holográfica VMAX — HP310, Investida Trovão G-Max 120+', 89.90, 15, 'Cartas',
         '/static/img/pikachu-vmax.jpg'),
        ('Charizard GX', 'Carta ultra rara GX — PS250, Destruição Devastadora', 249.90, 5, 'Cartas',
         '/static/img/charizard-gx.png'),
        ('Mewtwo Luxo c/ Luz', 'Figura colecionável Mewtwo 35cm com efeitos de luz — Sunny', 231.00, 8, 'Action Figures',
         '/static/img/mewtwo-luxo.png'),
        ('Action Figure Pikachu', 'Boneco colecionável Pikachu na Árvore — Pokémon', 219.00, 12, 'Action Figures',
         '/static/img/action-pikachu.jpg'),
        ('Camiseta Pokémon', 'Camiseta manga curta 100% algodão — 3 a 16 anos', 155.00, 20, 'Vestuário',
         '/static/img/camiseta-pokemon.jpg'),
        ('Mochila Pokeball', 'Mochila Pokeball 18" com rodinhas — Rayuela', 235.00, 10, 'Acessórios',
         '/static/img/mochila-pokeball.jpg'),
        ('Boné Equipe Rocket', 'Boné preto bordado Equipe Rocket R — ajuste flexível', 170.00, 15, 'Vestuário',
         '/static/img/bone-rocket.jpg'),
        ('Caneca Gengar', 'Caneca de porcelana Gengar 330ml', 40.00, 25, 'Acessórios',
         '/static/img/caneca-gengar.jpg'),
    ]

    for nome, desc, preco, estoque, cat, img in produtos:
        p = Product.query.filter_by(nome=nome).first()
        if p:
            p.image_url = img
        else:
            p = Product(nome=nome, descricao=desc, preco=preco,
                       estoque=estoque, categoria_id=cat_objs[cat].id,
                       image_url=img)
            db.session.add(p)

    db.session.commit()
    print('Seed executado!')

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        run_seed()