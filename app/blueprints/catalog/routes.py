from flask import Blueprint, render_template, request
from app.models.product import Product
from app.models.category import Category

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')

@catalog_bp.route('/')
def index():
    categoria_id = request.args.get('categoria', type=int)
    busca = request.args.get('q', '').strip()
    query = Product.query.filter(Product.estoque > 0)
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    if busca:
        query = query.filter(Product.nome.ilike(f'%{busca}%'))
    produtos = query.all()
    categorias = Category.query.all()
    return render_template('catalog/index.html',
        produtos=produtos, categorias=categorias,
        categoria_id=categoria_id, busca=busca)

@catalog_bp.route('/produto/<int:id>')
def detalhe(id):
    produto = Product.query.get_or_404(id)
    relacionados = Product.query.filter(
        Product.categoria_id == produto.categoria_id,
        Product.id != produto.id,
        Product.estoque > 0
    ).limit(4).all()
    return render_template('catalog/detalhe.html',
        produto=produto, relacionados=relacionados)

from flask_login import login_required, current_user
from app.extensions import db
from app.models.review import Review

@catalog_bp.route('/produto/<int:id>/avaliar', methods=['POST'])
@login_required
def avaliar(id):
    from flask import request, redirect, url_for, flash
    produto = Product.query.get_or_404(id)
    nota = int(request.form.get('nota', 0))
    comentario = request.form.get('comentario', '').strip()

    if nota < 1 or nota > 5:
        flash('Nota inválida.', 'danger')
        return redirect(url_for('catalog.detalhe', id=id))

    ja_avaliou = Review.query.filter_by(
        product_id=id, usuario_id=current_user.id).first()

    if ja_avaliou:
        flash('Você já avaliou este produto.', 'warning')
        return redirect(url_for('catalog.detalhe', id=id))

    review = Review(
        product_id=id,
        usuario_id=current_user.id,
        nota=nota,
        comentario=comentario
    )
    db.session.add(review)
    db.session.commit()
    flash('Avaliação enviada!', 'success')
    return redirect(url_for('catalog.detalhe', id=id))
