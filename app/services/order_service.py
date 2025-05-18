"""
Order service module for managing order-related business logic.

This module provides a service class that encapsulates all business logic related to orders,
including CRUD operations, search functionality, filtering, sorting, and data validation.
It handles order creation, updates, deletion, and querying while ensuring data integrity.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import date
from sqlalchemy.orm import Query
from flask_sqlalchemy.pagination import Pagination

from app.models import Order
from app.repositories.order_repository import OrderRepository
from app.utils.validation import validate_and_sanitize_order_data, sanitize_string
from app.services.base_service import BaseService


class OrderService(BaseService[Order]):
    """
    Service class to encapsulate business logic related to orders.
    This provides a layer of abstraction between the routes and the database models.
    """

    def __init__(self, order_repository: Optional[OrderRepository] = None) -> None:
        """
        Initialize the service with a repository.

        Args:
            order_repository: The repository to use.
                If not provided, a new instance will be created.
        """
        repository = order_repository or OrderRepository()
        super().__init__(repository, Order, validate_and_sanitize_order_data, sanitize_string)

    def get_order_by_log(self, log_id: str) -> Optional[Order]:
        """
        Get an order by its log ID.

        Args:
            log_id: The log ID of the order

        Returns:
            The order object or None if not found
        """
        return self.repository.get_by_log(log_id)

    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Get an order by its primary key ID.

        Args:
            order_id: The primary key ID of the order

        Returns:
            The order object or None if not found
        """
        return super().get_by_id(order_id)

    def create_order(self, order_data: Dict[str, Any]) -> Order:
        """
        Create a new order with the given data.

        Args:
            order_data: Dictionary containing order attributes

        Returns:
            The newly created order

        Raises:
            ValueError: If the order data is invalid
            Exception: If there's an error creating the order
        """
        return super().create(order_data)

    def update_order(self, order: Order, order_data: Dict[str, Any]) -> Order:
        """
        Update an existing order with the given data.

        Args:
            order: The order object to update
            order_data: Dictionary containing order attributes to update

        Returns:
            The updated order

        Raises:
            ValueError: If the order data is invalid
            Exception: If there's an error updating the order
        """
        return super().update(order, order_data)

    def delete_order(self, order: Order) -> None:
        """
        Soft delete an order by setting its deleted_at timestamp.

        Args:
            order: The order object to delete

        Raises:
            Exception: If there's an error soft deleting the order
        """
        super().delete(order)

    def hard_delete_order(self, order: Order) -> None:
        """
        Permanently delete an order from the database.
        This should be used with caution as it cannot be undone.

        Args:
            order: The order object to delete

        Raises:
            Exception: If there's an error deleting the order
        """
        super().hard_delete(order)

    def restore_order(self, order: Order) -> Order:
        """
        Restore a soft-deleted order.

        Args:
            order: The order object to restore

        Returns:
            The restored order

        Raises:
            Exception: If there's an error restoring the order
        """
        return super().restore(order)

    def get_deleted_orders(self) -> List[Order]:
        """
        Get all soft-deleted orders.

        Returns:
            List of all soft-deleted orders
        """
        return super().get_deleted()

    def get_all_orders_including_deleted(self) -> List[Order]:
        """
        Get all orders including soft-deleted ones.

        Returns:
            List of all orders including soft-deleted ones
        """
        return super().get_all_including_deleted()

    def search_orders(self, cust: Optional[str] = None, title: Optional[str] = None) -> List[Order]:
        """
        Search for orders by customer and/or title.

        Args:
            cust: Customer to search for
            title: Title to search for

        Returns:
            List of matching orders
        """
        # Sanitize search inputs
        sanitized_cust = self.sanitize_search_input(cust)
        sanitized_title = self.sanitize_search_input(title)

        return self.repository.search(sanitized_cust, sanitized_title)

    def filter_orders(self, search: Optional[str] = None) -> Query:
        """
        Filter orders by search term (customer or title).

        Args:
            search: Search term

        Returns:
            Filtered query object
        """
        # Sanitize search input
        sanitized_search = self.sanitize_search_input(search)

        return self.repository.filter(sanitized_search)

    def order_query(self, query: Query, sort_argument: Optional[str] = None) -> Query:
        """
        Apply sorting to a query.

        Args:
            query: The query to sort
            sort_argument: Comma-separated list of fields to sort by

        Returns:
            Sorted query object
        """
        return self.repository.apply_sort(query, sort_argument)

    def paginate_query(self, query: Query, page: int, per_page: int) -> Pagination:
        """
        Paginate a query.

        Args:
            query: The query to paginate
            page: Page number
            per_page: Items per page

        Returns:
            Pagination object
        """
        return self.repository.paginate(query, page, per_page)

    def get_dueouts(self, start: Optional[date] = None, end: Optional[date] = None) -> List[Order]:
        """
        Get orders that are due out within a date range.

        Args:
            start: Start date
            end: End date

        Returns:
            List of orders due out in the date range
        """
        return self.repository.get_dueouts(start, end)

    def check_order_exists(self, log: str) -> bool:
        """
        Check if an order with the given log exists.

        Args:
            log: The log ID to check

        Returns:
            True if the order exists, False otherwise
        """
        return self.repository.exists(log=log)
