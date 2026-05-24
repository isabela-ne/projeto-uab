from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
def index():
    if current_user.role != 'Administrador':
        flash('Acesso negado.', 'danger')
        return redirect(url_for('catalog.index'))
    return render_template('admin/index.html')
