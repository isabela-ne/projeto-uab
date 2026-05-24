from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.order import Order

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')

@orders_bp.route('/')
@login_required
def historico():
    pedidos = Order.query.filter_by(user_id=current_user.id)\
                         .order_by(Order.created_at.desc()).all()
    return render_template('orders/historico.html', pedidos=pedidos)

@orders_bp.route('/<int:id>')
@login_required
def detalhe(id):
    pedido = Order.query.get_or_404(id)

    # Segurança: cliente só vê seus próprios pedidos
    if pedido.user_id != current_user.id and current_user.role != 'Administrador':
        abort(403)

    return render_template('orders/detalhe.html', pedido=pedido)