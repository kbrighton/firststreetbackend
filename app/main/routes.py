from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required
from sqlalchemy import and_, or_

from app.extensions import db
from app.main import bp
from app.models import Order
from .forms import OrderForm, SearchForm, SearchLog, DisplayDueouts

ORDER_EDIT = "main.order_edit"
ORDERS = "main/orders.html"
SEARCH = "main/search.html"

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


@bp.route('/order/<string:cust>/<string:title>', methods=['POST', 'GET'])
@login_required
def search_result(cust, title):
    clauses = [Order.CUST.ilike(f'%{cust}%'), Order.TITLE.ilike(f'%{title}%')]
    orders_list = db.select(Order).where(and_(*clauses))

    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(orders_list, page=page, per_page=1)
    order = pagination.items
    if not order:
        flash("Could not find any orders that match")

        return redirect(url_for("main.search_form"))

    form = OrderForm(obj=order.pop())
    if request.method == 'POST' and form.validate_on_submit():
        order = db.session.execute(db.select(Order).filter_by(LOG=form.LOG.data)).scalar_one()
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

        db.session.commit()
        return redirect(url_for(ORDER_EDIT, log_id=order.LOG))

    return render_template("main/results.html", pagination=pagination, form=form)


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

        duesql = db.select(Order).where(
            and_(
                or_(Order.LOGTYPE == "TR", Order.LOGTYPE == "DP"),
                Order.DATOUT == None,
                Order.DUEOUT == form.Date.data,
            )
        )
        dueouts = db.session.execute(duesql).scalars()
        titles = [('Log', 'Log#'), ('ARTLO', 'Artlog'), ('CUST', 'Customer'), ('TITLE','Title'), ('PRIOR', 'Priority'), ('DATIN', 'Date In'), ('DUEOUT', 'Due Out'), ('COLORF', 'Colors'), ('PRINTN', 'Print Number'), ('LOGTYPE', 'Logtype'), ('RUSHN', 'Rush'), ('DATOUT', 'Date Out')]
        data = []
        for due in dueouts:
            data.append({
                'Log': due.LOG,
                'ARTLO': due.ARTLO,
                'CUST': due.CUST,
                'TITLE': due.TITLE,
                'PRIOR': due.PRIOR,
                'DATIN': due.DATIN,
                'DUEOUT': due.DUEOUT,
                'COLORF': due.COLORF,
                'PRINTN': due.PRINT_N,
                'LOGTYPE': due.LOGTYPE,
                'RUSHN': due.RUSH_N,
                'DATOUT': due.DATOUT
            })
        return render_template('main/dueouttable.html', titles=titles, data=data)
    return render_template("main/dueoutform.html", form=form)
