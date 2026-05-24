import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
import os

@pytest.fixture
def app():
    # Garantir que estamos em modo de teste
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test_secret"
    })

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, setup_data):
    """Retorna um cliente que já fez login."""
    with client.session_transaction() as sess:
        # Flask-Login espera que o ID do usuário esteja na sessão como _user_id
        sess['_user_id'] = str(setup_data['cliente'].id)
        sess['_fresh'] = True
    return client

@pytest.fixture
def admin_client(client, setup_data):
    """Retorna um cliente admin logado."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(setup_data['admin'].id)
        sess['_fresh'] = True
    return client

@pytest.fixture
def db_session(app):
    return _db.session

@pytest.fixture
def setup_data(db_session):
    # Limpar qualquer dado residual (embora :memory: deva estar limpo)
    _db.session.query(Product).delete()
    _db.session.query(Category).delete()
    _db.session.query(User).delete()
    _db.session.commit()

    # Criar categorias
    c1 = Category(nome="TCG")
    c2 = Category(nome="Acessórios")
    db_session.add_all([c1, c2])
    db_session.commit()

    # Criar produtos
    p1 = Product(nome="Pikachu VMAX", preco=150.0, estoque=10, categoria_id=c1.id)
    p2 = Product(nome="Escudo Protetor", preco=50.0, estoque=0, categoria_id=c2.id)
    db_session.add_all([p1, p2])
    db_session.commit()

    # Criar usuários
    admin = User(nome="Admin", email="admin@pokeshop.com", role="Administrador")
    admin.set_password("admin123")
    
    cliente = User(nome="Cliente", email="cliente@pokeshop.com", role="Cliente")
    cliente.set_password("cliente123")
    
    db_session.add_all([admin, cliente])
    db_session.commit()

    return {
        "admin": admin,
        "cliente": cliente,
        "produtos": {"disponivel": p1, "esgotado": p2}
    }
