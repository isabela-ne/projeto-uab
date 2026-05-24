from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models.product import Product
from app.models.order import Order, OrderItem

checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')

@checkout_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    carrinho = session.get('cart', {})
    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('cart.view'))

    # Valida estoque de todos os itens antes de mostrar o checkout
    for pid, item in carrinho.items():
        produto = Product.query.get(int(pid))
        if not produto or produto.estoque < item['quantidade']:
            flash(f'Estoque insuficiente para "{item["nome"]}".', 'danger')
            return redirect(url_for('cart.view'))

    total = sum(v['preco'] * v['quantidade'] for v in carrinho.values())
    return render_template('checkout/checkout.html', carrinho=carrinho, total=total)

@checkout_bp.route('/finalizar', methods=['POST'])
@login_required
def finalizar():
    carrinho = session.get('cart', {})
    if not carrinho:
        flash('Seu carrinho está vazio.', 'warning')
        return redirect(url_for('cart.view'))

    # Dados do formulário
    rua      = request.form.get('rua', '').strip()
    numero   = request.form.get('numero', '').strip()
    bairro   = request.form.get('bairro', '').strip()
    cidade   = request.form.get('cidade', '').strip()
    estado   = request.form.get('estado', '').strip()
    cep      = request.form.get('cep', '').strip()
    pagamento = request.form.get('pagamento', '').strip()

    # Validações básicas
    if not all([rua, numero, bairro, cidade, estado, cep, pagamento]):
        flash('Preencha todos os campos.', 'danger')
        return redirect(url_for('checkout.index'))

    if pagamento not in ['cartao', 'pix', 'boleto']:
        flash('Método de pagamento inválido.', 'danger')
        return redirect(url_for('checkout.index'))

    # Valida estoque novamente no servidor antes de criar o pedido
    for pid, item in carrinho.items():
        produto = Product.query.get(int(pid))
        if not produto or produto.estoque < item['quantidade']:
            flash(f'Estoque insuficiente para "{item["nome"]}".', 'danger')
            return redirect(url_for('cart.view'))

    # Calcula total no servidor — nunca confia no valor do cliente
    total = sum(
        Product.query.get(int(pid)).preco * item['quantidade']
        for pid, item in carrinho.items()
    )

    # Cria o pedido
    pedido = Order(
        user_id=current_user.id,
        status='aguardando_pagamento',
        payment_method=pagamento,
        total=total,
        endereco_rua=rua,
        endereco_numero=numero,
        endereco_bairro=bairro,
        endereco_cidade=cidade,
        endereco_estado=estado.upper(),
        endereco_cep=cep,
    )
    db.session.add(pedido)
    db.session.flush()  # gera o pedido.id antes de adicionar os itens

    # Cria os itens e decrementa estoque
    for pid, item in carrinho.items():
        produto = Product.query.get(int(pid))
        oi = OrderItem(
            order_id=pedido.id,
            product_id=produto.id,
            quantity=item['quantidade'],
            unit_price=produto.preco,  # preço real do banco, não da sessão
        )
        produto.estoque -= item['quantidade']
        db.session.add(oi)

    db.session.commit()

    # Limpa o carrinho
    session.pop('cart', None)

    flash('Pedido realizado com sucesso!', 'success')
    return redirect(url_for('orders.detalhe', id=pedido.id))