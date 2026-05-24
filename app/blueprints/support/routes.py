from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.ticket import Ticket, TicketMessage

support_bp = Blueprint('support', __name__, url_prefix='/support')

@support_bp.route('/')
@login_required
def index():
    if current_user.role in ['Administrador', 'Atendente']:
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    else:
        tickets = Ticket.query.filter_by(usuario_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('support/index.html', tickets=tickets)

@support_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    if request.method == 'POST':
        assunto = request.form.get('assunto', '').strip()
        mensagem = request.form.get('mensagem', '').strip()
        if not assunto or not mensagem:
            flash('Preencha todos os campos.', 'warning')
            return render_template('support/novo.html')
        ticket = Ticket(usuario_id=current_user.id, assunto=assunto)
        db.session.add(ticket)
        db.session.flush()
        msg = TicketMessage(ticket_id=ticket.id, autor_id=current_user.id, mensagem=mensagem)
        db.session.add(msg)
        db.session.commit()
        flash('Chamado aberto com sucesso!', 'success')
        return redirect(url_for('support.detalhe', ticket_id=ticket.id))
    return render_template('support/novo.html')

@support_bp.route('/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def detalhe(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if current_user.role == 'Cliente' and ticket.usuario_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('support.index'))
    if request.method == 'POST':
        mensagem = request.form.get('mensagem', '').strip()
        novo_status = request.form.get('status')
        if mensagem:
            msg = TicketMessage(ticket_id=ticket.id, autor_id=current_user.id, mensagem=mensagem)
            db.session.add(msg)
        if novo_status and current_user.role in ['Administrador', 'Atendente']:
            ticket.status = novo_status
        db.session.commit()
        flash('Resposta enviada!', 'success')
        return redirect(url_for('support.detalhe', ticket_id=ticket.id))
    return render_template('support/detalhe.html', ticket=ticket)