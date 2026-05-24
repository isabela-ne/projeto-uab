from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app.extensions import db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Administrador':
            flash('Acesso restrito ao administrador.', 'danger')
            return redirect(url_for('catalog.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/')
@login_required
@admin_required
def index():
    total_produtos = Product.query.count()
    total_usuarios = User.query.count()
    total_pedidos = Order.query.count()
    pedidos_pendentes = Order.query.filter_by(status='aguardando_pagamento').count()
    estoque_critico = Product.query.filter(Product.estoque <= 5).count()
    receita = db.session.query(db.func.sum(Order.total)).filter(
        Order.status.in_(['pago', 'enviado', 'entregue'])).scalar() or 0
    return render_template('admin/dashboard.html',
        total_produtos=total_produtos,
        total_usuarios=total_usuarios,
        total_pedidos=total_pedidos,
        pedidos_pendentes=pedidos_pendentes,
        estoque_critico=estoque_critico,
        receita=receita)

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

@admin_bp.route('/produtos/<int:produto_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def produto_editar(produto_id):
    p = Product.query.get_or_404(produto_id)
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

@admin_bp.route('/produtos/<int:produto_id>/excluir', methods=['POST'])
@login_required
@admin_required
def produto_excluir(produto_id):
    p = Product.query.get_or_404(produto_id)
    db.session.delete(p)
    db.session.commit()
    flash('Produto excluído.', 'info')
    return redirect(url_for('admin.produtos'))

# ── Usuários/Atendentes ───────────────────────────────────
@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    atendentes = User.query.filter_by(role='Atendente').all()
    clientes = User.query.filter_by(role='Cliente').all()
    return render_template('admin/usuarios.html', atendentes=atendentes, clientes=clientes)

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
        return redirect(url_for('admin.usuarios'))
    return render_template('admin/atendente_form.html')

@admin_bp.route('/atendentes/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def atendente_excluir(id):
    u = User.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash('Atendente removido.', 'info')
    return redirect(url_for('admin.usuarios'))

# ── Pedidos ───────────────────────────────────────────────
@admin_bp.route('/pedidos')
@login_required
@admin_required
def pedidos():
    status = request.args.get('status', '')
    if status:
        lista = Order.query.filter_by(status=status).order_by(Order.created_at.desc()).all()
    else:
        lista = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/pedidos.html', pedidos=lista, status_filtro=status)

@admin_bp.route('/pedidos/<int:id>')
@login_required
@admin_required
def pedido_detalhe(id):
    pedido = Order.query.get_or_404(id)
    return render_template('admin/pedido_detalhe.html', pedido=pedido)

@admin_bp.route('/pedidos/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def pedido_status(id):
    pedido = Order.query.get_or_404(id)
    novo_status = request.form.get('status')
    status_validos = ['aguardando_pagamento','pago','em_separacao','enviado','entregue','cancelado']
    if novo_status in status_validos:
        pedido.status = novo_status
        db.session.commit()
        flash(f'Status atualizado para "{novo_status}".', 'success')
    return redirect(url_for('admin.pedido_detalhe', id=id))

# ── Relatórios ────────────────────────────────────────────
@admin_bp.route('/relatorios')
@login_required
@admin_required
def relatorios():
    from app.models.order import OrderItem
    estoque_critico = Product.query.filter(Product.estoque <= 5).order_by(Product.estoque).all()
    pedidos_status = db.session.query(
        Order.status, db.func.count(Order.id)
    ).group_by(Order.status).all()
    receita_total = db.session.query(db.func.sum(Order.total)).filter(
        Order.status.in_(['pago','enviado','entregue'])).scalar() or 0
    total_pedidos = Order.query.count()
    return render_template('admin/relatorios.html',
        estoque_critico=estoque_critico,
        pedidos_status=pedidos_status,
        receita_total=receita_total,
        total_pedidos=total_pedidos)
@admin_bp.route('/cupons')
@login_required
@admin_required
def cupons():
    from app.models.coupon import Coupon
    cupons = Coupon.query.all()
    return render_template('admin/cupons.html', cupons=cupons)

@admin_bp.route('/cupons/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def cupom_novo():
    from app.models.coupon import Coupon
    from datetime import datetime
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip().upper()
        desconto_pct = float(request.form.get('desconto_pct', 0))
        validade_str = request.form.get('validade', '')
        validade = datetime.strptime(validade_str, '%Y-%m-%d') if validade_str else None
        c = Coupon(codigo=codigo, desconto_pct=desconto_pct, validade=validade)
        db.session.add(c)
        db.session.commit()
        flash('Cupom criado!', 'success')
        return redirect(url_for('admin.cupons'))
    return render_template('admin/cupom_form.html')

@admin_bp.route('/cupons/<int:cupom_id>/toggle', methods=['POST'])
@login_required
@admin_required
def cupom_toggle(cupom_id):
    from app.models.coupon import Coupon
    cupom = Coupon.query.get_or_404(cupom_id)
    cupom.ativo = not cupom.ativo
    db.session.commit()
    flash('Cupom atualizado!', 'success')
    return redirect(url_for('admin.cupons'))
