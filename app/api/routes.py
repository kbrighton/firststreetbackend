from typing import Dict, List, Any, Optional, Union, Tuple
from flask import request, abort, jsonify, make_response, Response
from flask_login import login_required, current_user, login_user, logout_user
import logging
from datetime import datetime, date

from app.utils.auth_utils import admin_required

# Configure logging
logger = logging.getLogger(__name__)

from app.extensions import db
from app.api import bp
from app.models import Order, Customer, User
from app.schema import (
    order_schema, orders_schema, 
    customer_schema, customers_schema,
    user_schema, users_schema
)
from app.services.order_service import OrderService
from app.services.customer_service import CustomerService
from app.services.user_service import UserService

# Constants moved from main routes
ORDER_FIELDS: List[str] = ['id', 'log', 'artlo', 'title', 'prior', 'datin', 'dueout',
                'colorf', 'print_n', 'logtype', 'rush', 'datout', 'artno']


# Legacy endpoints - kept for backward compatibility
@bp.route('/data')
@login_required
def fetch_data() -> Dict[str, Any]:
    """
    Fetch orders data with filtering, sorting, and pagination.

    Returns:
        Dictionary with order data and total count.
    """
    # Get search parameter
    search = request.args.get('search')

    # Create service instance
    order_service = OrderService()

    # Use service to filter orders
    query = order_service.filter_orders(search=search)
    total_orders = query.count()

    # Apply sorting
    sort_argument = request.args.get('sort')
    query = order_service.order_query(query, sort_argument=sort_argument)

    # pagination
    start = request.args.get('start', type=int, default=-1)
    length = request.args.get('length', type=int, default=-1)
    if start != -1 and length != -1:
        query = query.offset(start).limit(length)

    # response
    return {
        'data': orders_schema.dump(query),
        'total': total_orders / 10,
    }


@bp.route('/data', methods=['POST'])
@login_required
def update_order() -> Tuple[str, int]:
    """
    Update an order via legacy endpoint.

    Returns:
        Empty string and HTTP status code.
    """
    data = request.get_json()
    logger.info(f"Updating order with data: {data}")
    if 'id' not in data:
        logger.error("No id provided in update request")
        abort(400)

    # Create service instance
    order_service = OrderService()

    # Use service to get order by ID
    order = order_service.get_order_by_id(data['id'])
    logger.info(f"Found order with id {order}")
    if order is None:
        logger.error(f"Order with id {data['id']} not found")
        abort(404)

    try:
        # Prepare update data
        update_data: Dict[str, Any] = {}
        for field in data:
            if field == 'id':
                continue
            if field in ORDER_FIELDS:
                update_data[field] = data[field]
                logger.info(f"Will update {field} to {data[field]} in {order}")

        # Use service to update order
        order_service.update_order(order, update_data)
        logger.info(f"Successfully updated order {order.log}")
        return '', 204
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        abort(500)


# Order endpoints
@bp.route('/orders')
@login_required
def get_orders() -> Dict[str, Any]:
    """
    Get all orders with pagination, sorting, and filtering.

    Returns:
        Dictionary with paginated order data.
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search')
    sort = request.args.get('sort')

    # Create service instance
    order_service = OrderService()

    # Filter orders
    query = order_service.filter_orders(search=search)

    # Apply sorting
    if sort:
        query = order_service.order_query(query, sort_argument=sort)

    # Apply pagination
    paginated = order_service.paginate_query(query, page, per_page)

    # Prepare response
    return {
        'items': orders_schema.dump(paginated.items),
        'page': page,
        'per_page': per_page,
        'total': paginated.total,
        'pages': paginated.pages
    }


@bp.route('/orders/<int:id>')
@login_required
def get_order(id: int) -> Response:
    """
    Get a specific order by ID.

    Args:
        id: The order ID.

    Returns:
        JSON response with order data.

    Raises:
        404: If order not found.
    """
    order_service = OrderService()
    order = order_service.get_order_by_id(id)

    if not order:
        abort(404, description="Order not found")

    return jsonify(order_schema.dump(order))


@bp.route('/orders/log/<log_id>')
@login_required
def get_order_by_log(log_id: str) -> Response:
    """
    Get a specific order by log ID.

    Args:
        log_id: The order log ID.

    Returns:
        JSON response with order data.

    Raises:
        404: If order not found.
    """
    order_service = OrderService()
    order = order_service.get_order_by_log(log_id)

    if not order:
        abort(404, description="Order not found")

    return jsonify(order_schema.dump(order))


@bp.route('/orders', methods=['POST'])
@login_required
def create_order() -> Tuple[Response, int]:
    """
    Create a new order.

    Returns:
        JSON response with created order data and HTTP status code.

    Raises:
        400: If no data provided or validation fails.
        409: If order with the same log already exists.
        500: If there's an error creating the order.
    """
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    order_service = OrderService()

    # Check if order with this log already exists
    if 'log' in data and order_service.check_order_exists(data['log']):
        abort(409, description="Order with this log already exists")

    try:
        order = order_service.create_order(data)
        return jsonify(order_schema.dump(order)), 201
    except ValueError as e:
        logger.warning(f"Validation error creating order: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        abort(500, description="Error creating order")


@bp.route('/orders/<int:id>', methods=['PUT'])
@login_required
def update_order_by_id(id: int) -> Response:
    """
    Update an existing order.

    Args:
        id: The order ID.

    Returns:
        JSON response with updated order data.

    Raises:
        400: If no data provided or validation fails.
        404: If order not found.
        500: If there's an error updating the order.
    """
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    order_service = OrderService()
    order = order_service.get_order_by_id(id)

    if not order:
        abort(404, description="Order not found")

    try:
        updated_order = order_service.update_order(order, data)
        return jsonify(order_schema.dump(updated_order))
    except ValueError as e:
        logger.warning(f"Validation error updating order: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        abort(500, description="Error updating order")


@bp.route('/orders/<int:id>', methods=['DELETE'])
@login_required
def delete_order(id: int) -> Tuple[str, int]:
    """
    Delete an order.

    Args:
        id: The order ID.

    Returns:
        Empty string and HTTP status code.

    Raises:
        404: If order not found.
        500: If there's an error deleting the order.
    """
    order_service = OrderService()
    order = order_service.get_order_by_id(id)

    if not order:
        abort(404, description="Order not found")

    try:
        order_service.delete_order(order)
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting order: {str(e)}")
        abort(500, description="Error deleting order")


@bp.route('/orders/dueouts')
@login_required
def get_dueouts() -> Response:
    """
    Get orders due out within a date range.

    Query Parameters:
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.

    Returns:
        JSON response with due out orders.

    Raises:
        400: If date format is invalid or end date is before start date.
    """
    from app.utils.validation import sanitize_string, validate_date_range

    # Get query parameters
    start_date = sanitize_string(request.args.get('start_date'))
    end_date = sanitize_string(request.args.get('end_date'))

    try:
        # Parse dates if provided
        start: Optional[date] = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
        end: Optional[date] = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None

        # Validate date range if both dates are provided
        if start and end and not validate_date_range(start, end):
            abort(400, description="End date must be after start date")

        order_service = OrderService()
        dueouts = order_service.get_dueouts(start=start, end=end)

        return jsonify(orders_schema.dump(dueouts))
    except ValueError:
        abort(400, description="Invalid date format. Use YYYY-MM-DD")


# Customer endpoints
@bp.route('/customers')
@login_required
def get_customers() -> Response:
    """
    Get all customers.

    Returns:
        JSON response with all customers.
    """
    customer_service = CustomerService()
    customers = customer_service.get_all_customers()

    return jsonify(customers_schema.dump(customers))


@bp.route('/customers/<int:id>')
@login_required
def get_customer(id: int) -> Response:
    """
    Get a specific customer by ID.

    Args:
        id: The customer ID.

    Returns:
        JSON response with customer data.

    Raises:
        404: If customer not found.
    """
    customer_service = CustomerService()
    customer = customer_service.get_customer_by_id(id)

    if not customer:
        abort(404, description="Customer not found")

    return jsonify(customer_schema.dump(customer))


@bp.route('/customers/cust_id/<cust_id>')
@login_required
def get_customer_by_cust_id(cust_id: str) -> Response:
    """
    Get a specific customer by customer ID.

    Args:
        cust_id: The customer's unique identifier.

    Returns:
        JSON response with customer data.

    Raises:
        404: If customer not found.
    """
    customer_service = CustomerService()
    customer = customer_service.get_customer_by_cust_id(cust_id)

    if not customer:
        abort(404, description="Customer not found")

    return jsonify(customer_schema.dump(customer))


@bp.route('/customers', methods=['POST'])
@login_required
def create_customer() -> Tuple[Response, int]:
    """
    Create a new customer.

    Returns:
        JSON response with created customer data and HTTP status code.

    Raises:
        400: If no data provided or validation fails.
        500: If there's an error creating the customer.
    """
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    customer_service = CustomerService()

    try:
        customer = customer_service.create_customer(data)
        return jsonify(customer_schema.dump(customer)), 201
    except ValueError as e:
        logger.warning(f"Validation error creating customer: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error creating customer: {str(e)}")
        abort(500, description="Error creating customer")


@bp.route('/customers/<int:id>', methods=['PUT'])
@login_required
def update_customer(id: int) -> Response:
    """
    Update an existing customer.

    Args:
        id: The customer ID.

    Returns:
        JSON response with updated customer data.

    Raises:
        400: If no data provided or validation fails.
        404: If customer not found.
        500: If there's an error updating the customer.
    """
    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    customer_service = CustomerService()
    customer = customer_service.get_customer_by_id(id)

    if not customer:
        abort(404, description="Customer not found")

    try:
        updated_customer = customer_service.update_customer(customer, data)
        return jsonify(customer_schema.dump(updated_customer))
    except ValueError as e:
        logger.warning(f"Validation error updating customer: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error updating customer: {str(e)}")
        abort(500, description="Error updating customer")


@bp.route('/customers/<int:id>', methods=['DELETE'])
@login_required
def delete_customer(id: int) -> Tuple[str, int]:
    """
    Delete a customer.

    Args:
        id: The customer ID.

    Returns:
        Empty string and HTTP status code.

    Raises:
        404: If customer not found.
        500: If there's an error deleting the customer.
    """
    customer_service = CustomerService()
    customer = customer_service.get_customer_by_id(id)

    if not customer:
        abort(404, description="Customer not found")

    try:
        customer_service.delete_customer(customer)
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting customer: {str(e)}")
        abort(500, description="Error deleting customer")


@bp.route('/customers/search')
@login_required
def search_customers() -> Response:
    """
    Search for customers.

    Query Parameters:
        q: Search term to filter customers by.

    Returns:
        JSON response with matching customers.
    """
    search_term = request.args.get('q')

    customer_service = CustomerService()
    customers = customer_service.search_customers(search_term=search_term)

    return jsonify(customers_schema.dump(customers))


# Authentication endpoints
@bp.route('/auth/login', methods=['POST'])
def api_login() -> Response:
    """
    Login via API.

    Request Body:
        username: User's username.
        password: User's password.
        remember: (optional) Boolean to remember the login session.

    Returns:
        JSON response with login status and user data.

    Raises:
        400: If username and password are not provided or validation fails.
        401: If authentication fails.
        500: If there's an error during login.
    """
    from app.utils.validation import sanitize_string

    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        abort(400, description="Username and password required")

    # Sanitize inputs
    username = sanitize_string(data['username'])
    # Don't sanitize password
    password = data['password']

    try:
        user_service = UserService()
        user = user_service.authenticate_user(username, password)

        if not user:
            abort(401, description="Invalid username or password")

        login_user(user, remember=data.get('remember', False))

        return jsonify({
            'message': 'Login successful',
            'user': user_schema.dump(user)
        })
    except ValueError as e:
        logger.warning(f"Validation error during login: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        abort(500, description="Error during login")


@bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout() -> Response:
    """
    Logout via API.

    Returns:
        JSON response with logout status.
    """
    logout_user()
    return jsonify({'message': 'Logout successful'})


# User endpoints (admin only)
@bp.route('/users')
@login_required
@admin_required
def get_users() -> Response:
    """
    Get all users (admin only).

    Returns:
        JSON response with all users.
    """
    user_service = UserService()
    users = user_service.get_all_users()

    return jsonify(users_schema.dump(users))


@bp.route('/users/<int:id>')
@login_required
@admin_required
def get_user(id: int) -> Response:
    """
    Get a specific user by ID (admin only).

    Args:
        id: The user ID.

    Returns:
        JSON response with user data.

    Raises:
        404: If user not found.
    """
    user_service = UserService()
    user = user_service.get_user_by_id(id)

    if not user:
        abort(404, description="User not found")

    return jsonify(user_schema.dump(user))


@bp.route('/users', methods=['POST'])
@login_required
@admin_required
def create_user() -> Tuple[Response, int]:
    """
    Create a new user (admin only).

    Request Body:
        username: User's username.
        email: User's email.
        password: User's password.
        role: (optional) User's role. Defaults to 'user'.

    Returns:
        JSON response with created user data and HTTP status code.

    Raises:
        400: If required fields are missing or validation fails.
        500: If there's an error creating the user.
    """
    from app.utils.validation import sanitize_string

    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        abort(400, description="Username, email, and password required")

    # Sanitize inputs
    username = sanitize_string(data['username'])
    email = sanitize_string(data['email'])
    # Don't sanitize password
    password = data['password']
    role = sanitize_string(data.get('role', 'user'))

    user_service = UserService()

    try:
        user = user_service.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )
        return jsonify(user_schema.dump(user)), 201
    except ValueError as e:
        logger.warning(f"Validation error creating user: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        abort(500, description="Error creating user")


@bp.route('/users/<int:id>', methods=['PUT'])
@login_required
def update_user(id: int) -> Response:
    """
    Update an existing user (admin only or self).

    Args:
        id: The user ID.

    Request Body:
        username: (optional) User's new username.
        email: (optional) User's new email.
        password: (optional) User's new password.
        role: (optional) User's new role (admin only).

    Returns:
        JSON response with updated user data.

    Raises:
        400: If no data provided or validation fails.
        403: If trying to update another user without admin privileges or changing role without admin privileges.
        404: If user not found.
        500: If there's an error updating the user.
    """
    from app.utils.validation import sanitize_string

    # Check if user is updating themselves or is admin
    if id != current_user.id and current_user.role != 'admin':
        abort(403, description="You can only update your own user information unless you're an admin")

    data = request.get_json()
    if not data:
        abort(400, description="No data provided")

    # Sanitize inputs
    sanitized_data: Dict[str, Any] = {}
    if 'username' in data:
        sanitized_data['username'] = sanitize_string(data['username'])
    if 'email' in data:
        sanitized_data['email'] = sanitize_string(data['email'])
    if 'password' in data:
        # Don't sanitize password
        sanitized_data['password'] = data['password']
    if 'role' in data:
        sanitized_data['role'] = sanitize_string(data['role'])

    user_service = UserService()
    user = user_service.get_user_by_id(id)

    if not user:
        abort(404, description="User not found")

    # Only admins can change roles
    if 'role' in sanitized_data and current_user.role != 'admin':
        abort(403, description="Only admins can change user roles")

    try:
        updated_user = user_service.update_user(user, sanitized_data)
        return jsonify(user_schema.dump(updated_user))
    except ValueError as e:
        logger.warning(f"Validation error updating user: {str(e)}")
        abort(400, description=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        abort(500, description="Error updating user")


@bp.route('/users/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(id: int) -> Tuple[str, int]:
    """
    Delete a user (admin only).

    Args:
        id: The user ID.

    Returns:
        Empty string and HTTP status code.

    Raises:
        403: If trying to delete yourself.
        404: If user not found.
        500: If there's an error deleting the user.
    """
    # Prevent deleting self
    if id == current_user.id:
        abort(403, description="Cannot delete yourself")

    user_service = UserService()
    user = user_service.get_user_by_id(id)

    if not user:
        abort(404, description="User not found")

    try:
        user_service.delete_user(user)
        return '', 204
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        abort(500, description="Error deleting user")
