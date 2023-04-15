from flask import render_template, session, redirect, url_for, request, flash

from app.main import bp
from app.extensions import db
from app.models import Customer, Order
from .forms import *
from sqlalchemy import and_


@bp.route('/')
def index():
    return render_template("main/index.html")


@bp.route('/order/<log_id>', methods=['POST', 'GET'])
def order_edit(log_id):
    order = db.session.execute(db.select(Order).filter_by(LOG=log_id)).scalar_one()
    form = OrderForm(obj=order)

    return render_template("main/orders.html", form=form)


@bp.route('/order/<cust>/<title>', methods=['POST', 'GET'])
def search_result(cust, title):
    cust = cust
    title = title

    clauses = [Order.CUST.like(f'%{cust}%'), Order.TITLE.like(f'%{title}%')]
    orders_list = db.select(Order).where(and_(*clauses))

    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(orders_list, page=page, per_page=1)
    order = pagination.items
    form = OrderForm(obj=order.pop())
    if request.method == 'POST' and form.validate_on_submit():
        order = db.session.execute(db.select(Order).filter_by(LOG=form.LOG.data)).scalar_one()
        order.CUST = form.CUST.data
        order.TITLE = form.TITLE.data
        order.DATIN = form.DATIN.data
        order.ARTOUT = form.ARTOUT.data
        order.DUEOUT = form.DUEOUT.data
        order.PRINT_N = form.PRINT_N.data
        order.ARTLO = form.ARTLO.data
        order.PRIOR = form.PRIOR.data
        order.LOGTYPE = form.LOGTYPE.data
        order.COLORF = form.COLORF.data
        order.REF_ARTLO = form.REF_ARTLO.data
        order.HOWSHIP = form.HOWSHIP.data
        order.DATOUT = form.DATOUT.data

        db.session.commit()
        return redirect(url_for('main.order_edit', log_id=order.LOG))

    return render_template("main/results.html", pagination=pagination, form=form)


@bp.route('/order', methods=['POST', 'GET'])
def new_order():
    form = OrderForm()
    if request.method == 'POST' and form.validate_on_submit():
        order = db.session.execute(db.select(Order).filter_by(LOG=form.LOG.data)).first()
        if order is None:
            order = Order()
            order.LOG = form.LOG.data
            order.CUST = form.CUST.data
            order.TITLE = form.TITLE.data
            order.DATIN = form.DATIN.data
            order.ARTOUT = form.ARTOUT.data
            order.DUEOUT = form.DUEOUT.data
            order.PRINT_N = form.PRINT_N.data
            order.ARTLO = form.ARTLO.data
            order.PRIOR = form.PRIOR.data
            order.LOGTYPE = form.LOGTYPE.data
            order.COLORF = form.COLORF.data
            order.REF_ARTLO = form.REF_ARTLO.data
            order.HOWSHIP = form.HOWSHIP.data
            order.DATOUT = form.DATOUT.data

            db.session.add(order)
            db.session.commit()
            return redirect(url_for('main.order_edit', log_id=order.LOG))
        else:
            flash("That LOG Number already exists")
            return render_template("main/orders.html", form=form)

    return render_template("main/orders.html", form=form)


@bp.route('/search', methods=['POST', 'GET'])
def search_form():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('main.search_result', cust=form.CUST.data, title=form.TITLE.data))

    return render_template("main/search.html", form=form)
