from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.product import Product
from app.models.category import Category
from app.models.user import User
from app.models.order import Order

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Administrador':
            flash('Acesso negado.', 'danger')
            return redirect(url_for('catalog.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_produtos = Product.query.count()
    total_usuarios = User.query.count()
    estoque_critico = Product.query.filter(Product.estoque <= 5).all()
    return render_template('admin/index.html',
        total_produtos=total_produtos,
        total_usuarios=total_usuarios,
        estoque_critico=estoque_critico)

@admin_bp.route('/produtos')
@login_required
@admin_required
def produtos():
    produtos = Product.query.all()
    return render_template('admin/produtos.html', produtos=produtos)

@admin_bp.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def produto_novo():
    categorias = Category.query.all()
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        preco = float(request.form.get('preco', 0))
        estoque = int(request.form.get('estoque', 0))
        categoria_id = int(request.form.get('categoria_id', 0))
        image_url = request.form.get('image_url', '').strip()
        p = Product(nome=nome, descricao=descricao, preco=preco,
                   estoque=estoque, categoria_id=categoria_id, image_url=image_url)
        db.session.add(p)
        db.session.commit()
        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('admin.produtos'))
    return render_template('admin/produto_form.html', produto=None, categorias=categorias)

@admin_bp.route('/produtos/<int:produto_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def produto_editar(produto_id):
    produto = Product.query.get_or_404(produto_id)
    categorias = Category.query.all()
    if request.method == 'POST':
        produto.nome = request.form.get('nome', '').strip()
        produto.descricao = request.form.get('descricao', '').strip()
        produto.preco = float(request.form.get('preco', 0))
        produto.estoque = int(request.form.get('estoque', 0))
        produto.categoria_id = int(request.form.get('categoria_id', 0))
        produto.image_url = request.form.get('image_url', '').strip()
        db.session.commit()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('admin.produtos'))
    return render_template('admin/produto_form.html', produto=produto, categorias=categorias)

@admin_bp.route('/produtos/<int:produto_id>/excluir', methods=['POST'])
@login_required
@admin_required
def produto_excluir(produto_id):
    produto = Product.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído!', 'success')
    return redirect(url_for('admin.produtos'))

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = User.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)
