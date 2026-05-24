from flask import Blueprint, render_template
from app.models.product import Product
from app.models.category import Category
catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')
@catalog_bp.route('/')
def index():
    produtos = Product.query.filter(Product.estoque > 0).all()
    categorias = Category.query.all()
    return render_template('catalog/index.html', produtos=produtos, categorias=categorias)
