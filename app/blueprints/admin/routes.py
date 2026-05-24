from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Administrador':
            flash('Acesso restrito ao administrador.', 'danger')
            return redirect(url_for('catalog.index'))
        return f(*args, **kwargs)
    return decorated

# ── Dashboard ─────────────────────────────────────────────
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    total_produtos = Product.query.count()
    total_usuarios = User.query.count()
    return render_template('admin/dashboard.html',
                           total_produtos=total_produtos,
                           total_usuarios=total_usuarios)

# ── Produtos ──────────────────────────────────────────────
@admin_bp.route('/produtos')
@login_required
@admin_required
def produtos():
    lista = Product.query.all()
    return render_template('admin/produtos.html', produtos=lista)

@admin_bp.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def produto_novo():
    categorias = Category.query.all()
    if request.method == 'POST':
        nome      = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        preco     = float(request.form.get('preco', 0))
        estoque   = int(request.form.get('estoque', 0))
        cat_id    = int(request.form.get('categoria_id'))
        image_url = request.form.get('image_url', '').strip()
        if preco <= 0:
            flash('O preço deve ser maior que zero.', 'danger')
            return render_template('admin/produto_form.html', categorias=categorias)
        p = Product(nome=nome, descricao=descricao, preco=preco,
                    estoque=estoque, categoria_id=cat_id, image_url=image_url)
        db.session.add(p)
        db.session.commit()
        flash('Produto criado com sucesso!', 'success')
        return redirect(url_for('admin.produtos'))
    return render_template('admin/produto_form.html', categorias=categorias, produto=None)

@admin_bp.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def produto_editar(id):
    p = Product.query.get_or_404(id)
    categorias = Category.query.all()
    if request.method == 'POST':
        p.nome        = request.form.get('nome', '').strip()
        p.descricao   = request.form.get('descricao', '').strip()
        p.preco       = float(request.form.get('preco', 0))
        p.estoque     = int(request.form.get('estoque', 0))
        p.categoria_id= int(request.form.get('categoria_id'))
        p.image_url   = request.form.get('image_url', '').strip()
        if p.preco <= 0:
            flash('O preço deve ser maior que zero.', 'danger')
            return render_template('admin/produto_form.html', categorias=categorias, produto=p)
        db.session.commit()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('admin.produtos'))
    return render_template('admin/produto_form.html', categorias=categorias, produto=p)

@admin_bp.route('/produtos/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def produto_excluir(id):
    p = Product.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Produto excluído.', 'info')
    return redirect(url_for('admin.produtos'))

# ── Atendentes ────────────────────────────────────────────
@admin_bp.route('/atendentes')
@login_required
@admin_required
def atendentes():
    lista = User.query.filter_by(role='Atendente').all()
    return render_template('admin/atendentes.html', atendentes=lista)

@admin_bp.route('/atendentes/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def atendente_novo():
    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        if User.query.filter_by(email=email).first():
            flash('E-mail já cadastrado.', 'warning')
            return render_template('admin/atendente_form.html')
        u = User(nome=nome, email=email, role='Atendente')
        u.set_password(senha)
        db.session.add(u)
        db.session.commit()
        flash('Atendente criado com sucesso!', 'success')
        return redirect(url_for('admin.atendentes'))
    return render_template('admin/atendente_form.html')

@admin_bp.route('/atendentes/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def atendente_excluir(id):
    u = User.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash('Atendente removido.', 'info')
    return redirect(url_for('admin.atendentes'))