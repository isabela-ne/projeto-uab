from flask import Blueprint, session, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models.product import Product

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/view')
@login_required
def view():
    carrinho = session.get('cart', {})
    total = sum(v['preco'] * v['quantidade'] for v in carrinho.values())
    return render_template('cart/carrinho.html', carrinho=carrinho, total=total)

@cart_bp.route('/add/<int:produto_id>', methods=['POST'])
@login_required
def add(produto_id):
    produto = Product.query.get_or_404(produto_id)
    quantidade = int(request.form.get('quantidade', 1))

    if quantidade > produto.estoque:
        flash('Estoque insuficiente!', 'danger')
        return redirect(url_for('catalog.index'))

    carrinho = session.get('cart', {})
    pid = str(produto_id)

    if pid in carrinho:
        carrinho[pid]['quantidade'] += quantidade
    else:
        carrinho[pid] = {
            'nome': produto.nome,
            'preco': produto.preco,
            'quantidade': quantidade
        }

    session['cart'] = carrinho
    session.modified = True
    flash(f'{produto.nome} adicionado ao carrinho!', 'success')
    return redirect(url_for('cart.view'))

@cart_bp.route('/remove/<pid>', methods=['POST'])
@login_required
def remove(pid):
    carrinho = session.get('cart', {})
    carrinho.pop(pid, None)
    session['cart'] = carrinho
    session.modified = True
    flash('Item removido do carrinho.', 'info')
    return redirect(url_for('cart.view'))

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    session.pop('cart', None)
    flash('Carrinho esvaziado.', 'info')
    return redirect(url_for('cart.view'))