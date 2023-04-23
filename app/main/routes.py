from typing import List, Tuple, Any

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required
from sqlalchemy import and_, or_

from app.extensions import db
from app.main import bp
from app.models import Order
from app.schema import OrderSchema, order_schema, orders_schema
from .forms import OrderForm, SearchForm, SearchLog, DisplayDueouts

ORDER_EDIT = "main.order_edit"
ORDERS = "main/orders.html"
SEARCH = "main/search.html"
DUEOUT_TITLES: list[tuple[str, str] | Any] = [('Log', 'Log#'), ('ARTLO', 'Artlog'), ('CUST', 'Customer'), ('TITLE', 'Title'), ('PRIOR', 'Priority'),
                 ('DATIN', 'Date In'), ('DUEOUT', 'Due Out'), ('COLORF', 'Colors'), ('PRINTN', 'Print Number'),
                 ('LOGTYPE', 'Logtype'), ('RUSHN', 'Rush'), ('DATOUT', 'Date Out')]


@bp.route('/')
@login_required
def index():
    return render_template("main/index.html")


@bp.route('/order/<log_id>', methods=['POST', 'GET'])
@login_required
def order_edit(log_id):
    order = db.session.execute(db.select(Order).filter_by(LOG=log_id)).scalar_one()
    form = OrderForm(obj=order)
    if request.method == 'POST' and form.validate_on_submit():
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
        return redirect(url_for(ORDER_EDIT, log_id=order.LOG))
    return render_template(ORDERS, form=form)


@bp.route('/order_search/', methods=['POST', 'GET'])
@login_required
def search_result():
    cust = request.args.get('cust')
    title = request.args.get('title')
    clauses = []
    if cust:
        clauses.append(Order.CUST.ilike(f'%{cust}%'))

    if title:
        clauses.append(Order.TITLE.ilike(f'%{title}%'))

    orders_list = db.select(Order).where(and_(*clauses)).order_by(Order.DATIN.desc(), Order.CUST.desc())

    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(orders_list, page=page, per_page=20)
    orders = pagination.items
    if not orders:
        flash("Could not find any orders that match")

        return redirect(url_for("main.search_form"))

    titles = DUEOUT_TITLES
    data = orders_schema.dump(orders)

    return render_template("main/resultstable.html", pagination=pagination, data=data, titles=titles, Order=Order)


@bp.route('/order', methods=['POST', 'GET'])
@login_required
def new_order():
    form = OrderForm()
    if request.method == 'POST' and form.validate_on_submit():
        order = db.session.execute(db.select(Order).filter_by(LOG=form.LOG.data)).first()
        if order is None:
            order = Order()
            order.LOG = form.LOG.data.upper()
            order.CUST = form.CUST.data.upper()
            order.TITLE = form.TITLE.data.upper()
            order.DATIN = form.DATIN.data
            order.ARTOUT = form.ARTOUT.data
            order.DUEOUT = form.DUEOUT.data
            order.PRINT_N = form.PRINT_N.data
            order.ARTLO = form.ARTLO.data.upper()
            order.PRIOR = form.PRIOR.data
            order.LOGTYPE = form.LOGTYPE.data.upper()
            order.COLORF = form.COLORF.data
            order.REF_ARTLO = form.REF_ARTLO.data
            order.HOWSHIP = form.HOWSHIP.data
            order.DATOUT = form.DATOUT.data

            db.session.add(order)
            db.session.commit()
            return redirect(url_for(ORDER_EDIT, log_id=order.LOG))
        else:
            flash("That LOG Number already exists")
            return render_template(ORDERS, form=form)

    return render_template(ORDERS, form=form)


@bp.route('/search', methods=['POST', 'GET'])
@login_required
def search_form():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('main.search_result', cust=form.CUST.data, title=form.TITLE.data))

    return render_template(SEARCH, form=form)


@bp.route('/search_log', methods=['POST', 'GET'])
@login_required
def search_log():
    form = SearchLog()
    if form.validate_on_submit():
        order = db.session.execute(db.select(Order).filter_by(LOG=form.LOG.data)).first()
        if order is not None:
            return redirect(url_for(ORDER_EDIT, log_id=form.LOG.data))
        flash('Log number does not exist')
        return render_template(SEARCH, form=form)
    return render_template(SEARCH, form=form)


@bp.route('/dueouts', methods=['POST', 'GET'])
@login_required
def view_dueouts():
    form = DisplayDueouts()
    if form.validate_on_submit():
        duesql = (
            db.select(Order)
            .where(
                and_(
                    or_(Order.LOGTYPE == "TR", Order.LOGTYPE == "DP"),
                    Order.DATOUT == None,
                    Order.DUEOUT == form.Date.data,
                )
            )
            .order_by(Order.DUEOUT.desc())
        )
        dueouts = db.session.execute(duesql).scalars()
        titles = DUEOUT_TITLES
        data = orders_schema.dump(dueouts)

        return render_template('main/dueouttable.html', titles=titles, data=data)
    return render_template("main/dueoutform.html", form=form)


@bp.route('/dueouts_all', methods=['POST', 'GET'])
@login_required
def all_dueouts():
    duesql = (
        db.select(Order)
        .where(
            and_(
                or_(Order.LOGTYPE == "TR", Order.LOGTYPE == "DP"),
                Order.DATOUT == None,
            ),
            Order.DUEOUT != None,
        )
        .order_by(Order.DUEOUT.desc())
    )
    dueouts = db.session.execute(duesql).scalars()
    titles = DUEOUT_TITLES
    data = orders_schema.dump(dueouts)
    return render_template('main/dueouttable.html', titles=titles, data=data)
