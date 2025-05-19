"""
Main routes module for handling web UI endpoints.

This module defines all the routes for the main blueprint, handling web UI requests
for order management, search functionality, and due-out tracking. It uses the service
layer to interact with the database and implements proper error handling and logging.
"""

from typing import List, Dict, Any, Tuple, Optional, Union
from datetime import date
from flask import render_template, redirect, url_for, request, flash, abort, Response
from flask_login import login_required
from sqlalchemy import and_, or_

from app.extensions import db
from app.logging import get_logger
from app.main import bp
from app.models import Order
from app.schemas import orders_schema
from app.services.order_service import OrderService
from app.utils.pagination import SimplePagination
from app.utils.form_utils import extract_form_data
from .forms import OrderForm, SearchForm, SearchLog, DisplayDueouts

# Get logger for this module
logger = get_logger(__name__)

ORDER_EDIT = "main.order_edit"
ORDERS = "main/orders.html"
SEARCH = "main/search.html"
DUEOUT_TITLES: List[Tuple[str, str]] = [
    ('log', 'Log#'), ('artlo', 'Artlog'), ('cust', 'Customer'), ('title', 'Title'), 
    ('prior', 'Priority'), ('datin', 'Date In'), ('dueout', 'Due Out'), ('colorf', 'Colors'), 
    ('print_n', 'Print Number'), ('logtype', 'Logtype'), ('rush', 'Rush'), ('artno','Artist ID')
]


@bp.route('/')
@login_required
def index() -> str:
    """
    Render the main index page.

    This route displays the main dashboard or landing page of the application.
    It requires the user to be logged in.

    Returns:
        Rendered HTML template for the index page.
    """
    return render_template("main/index.html")


# This function has been replaced by OrderService.update_order


@bp.route('/order/<log_id>', methods=['POST', 'GET'])
@login_required
def order_edit(log_id: str) -> Union[str, Response]:
    """
    Edit an existing order.

    This route handles both displaying the order edit form (GET) and
    processing form submissions to update an order (POST).

    Args:
        log_id: The log ID of the order to edit.

    Returns:
        On GET: Rendered HTML template with the order form.
        On POST: Redirect to the same page after successful update,
                or rendered form with error messages if validation fails.
    """
    try:
        # Create service instance
        order_service = OrderService()

        order = order_service.get_order_by_log(log_id)
        if order is None:
            logger.error(f"Order with log_id {log_id} not found")
            flash(f"Order with log number {log_id} not found")
            return redirect(url_for('main.search_form'))

        form = OrderForm(obj=order)
        if request.method == 'POST' and form.validate_on_submit():
            try:
                # Extract form data
                order_data = extract_form_data(form, model=order)

                order_service.update_order(order, order_data)
                logger.info(f"Successfully updated order {order.log}")
                flash(f"Order {order.log} updated successfully")
                return redirect(url_for(ORDER_EDIT, log_id=order.log))
            except Exception as e:
                logger.error(f"Error updating order: {str(e)}")
                flash("An error occurred while updating the order")
                return render_template(ORDERS, form=form)
        return render_template(ORDERS, form=form)
    except Exception as e:
        logger.error(f"Error in order_edit: {str(e)}")
        flash("An error occurred while accessing the order")
        return redirect(url_for('main.search_form'))


@bp.route('/order_search/', methods=['POST', 'GET'])
@login_required
def search_result() -> Union[str, Response]:
    """
    Display search results for orders.

    This route processes search parameters from the query string and
    displays matching orders in a paginated table.

    Query Parameters:
        cust: Customer ID or name to search for.
        title: Order title to search for.
        page: Page number for pagination.

    Returns:
        Rendered HTML template with search results,
        or redirect to search form if no results found.
    """
    cust = request.args.get('cust')
    title = request.args.get('title')

    # Create service instance
    order_service = OrderService()

    # Use the service to search for orders
    orders = order_service.search_orders(cust=cust, title=title)

    # Convert to list for pagination
    orders_list = list(orders)

    if not orders_list:
        flash("Could not find any orders that match")
        return redirect(url_for("main.search_form"))

    # Create a paginated response
    page = request.args.get('page', 1, type=int)
    per_page = 20
    total = len(orders_list)
    start = (page - 1) * per_page
    end = min(start + per_page, total)

    # Manual pagination
    items = orders_list[start:end]

    # Create a pagination object using our utility class
    pagination = SimplePagination(items, page, per_page, total)

    titles = DUEOUT_TITLES
    data = orders_schema.dump(items)

    return render_template("main/resultstable.html", pagination=pagination, data=data, titles=titles, Order=Order)


@bp.route('/order', methods=['POST', 'GET'])
@login_required
def new_order() -> str:
    """
    Create a new order.

    This route handles both displaying the new order form (GET) and
    processing form submissions to create a new order (POST).

    Returns:
        On GET: Rendered HTML template with the empty order form.
        On POST: Redirect to the edit page for the new order after successful creation,
                or rendered form with error messages if validation fails.
    """
    form = OrderForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create service instance
            order_service = OrderService()

            # Check if order with this log already exists
            if order_service.check_order_exists(form.log.data):
                logger.warning(f"Attempted to create duplicate order with log {form.log.data}")
                flash("That LOG Number already exists")
                return render_template(ORDERS, form=form)

            # Extract form data and create new order
            order_data = extract_form_data(form)

            order = order_service.create_order(order_data)
            logger.info(f"Successfully created new order {order.log}")
            flash(f"Order {order.log} created successfully")
            return redirect(url_for(ORDER_EDIT, log_id=order.log))
        except Exception as e:
            logger.error(f"Error creating new order: {str(e)}")
            flash("An error occurred while creating the order")
            return render_template(ORDERS, form=form)
    return render_template(ORDERS, form=form)


@bp.route('/newsearch')
@login_required
def new_search() -> str:
    return render_template("main/newresults.html")


@bp.route('/search', methods=['POST', 'GET'])
@login_required
def search_form() -> Union[str, Response]:
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('main.search_result', cust=form.cust.data, title=form.title.data))

    return render_template(SEARCH, form=form)


@bp.route('/search_log', methods=['POST', 'GET'])
@login_required
def search_log() -> Union[str, Response]:
    form = SearchLog()
    if form.validate_on_submit():
        # Create service instance
        order_service = OrderService()
        if order_service.check_order_exists(form.log.data):
            return redirect(url_for(ORDER_EDIT, log_id=form.log.data))
        flash('Log number does not exist')
        return render_template(SEARCH, form=form)
    return render_template(SEARCH, form=form)


def process_dueouts_form(start: Optional[date] = None, end: Optional[date] = None) -> str:
    """
    Process the due-outs form and generate the due-outs table.

    This helper function retrieves orders that are due out within the specified
    date range and renders them in a table.

    Args:
        start: Start date for the due-out range.
        end: End date for the due-out range.

    Returns:
        Rendered HTML template with the due-outs table.
    """
    # Create service instance
    order_service = OrderService()

    # Use the service to get dueouts
    dueouts = order_service.get_dueouts(start=start, end=end)

    titles = DUEOUT_TITLES
    data = orders_schema.dump(dueouts)
    return render_template('main/dueouttable.html', titles=titles, data=data)


@bp.route('/dueouts', methods=['POST', 'GET'])
@login_required
def view_dueouts() -> str:  # sourcery skip: none-compare
    """
    Display the due-outs form and process submissions.

    This route handles both displaying the due-outs date range form (GET) and
    processing form submissions to view orders due out in a specific date range (POST).

    Returns:
        On GET: Rendered HTML template with the due-outs form.
        On POST: Rendered HTML template with the due-outs table for the specified date range.
    """
    form = DisplayDueouts()
    if form.validate_on_submit():
        return process_dueouts_form(start=form.start_date.data, end=form.end_date.data)
    return render_template("main/dueoutform.html", form=form)


@bp.route('/dueouts_all')
@login_required
def all_dueouts() -> str:  # sourcery skip: none-compare
    """
    Display all due-outs without date filtering.

    This route shows all orders that are due out, without any date range filtering.

    Returns:
        Rendered HTML template with the due-outs table containing all due-out orders.
    """
    return process_dueouts_form()
