"""
Customer service module for managing customer-related business logic.

This module provides a service class that encapsulates all business logic related to customers,
including CRUD operations, search functionality, and data validation.
"""

from typing import List, Optional, Dict, Any
from app.models import Customer
from app.repositories.customer_repository import CustomerRepository
from app.utils.validation import validate_and_sanitize_customer_data, sanitize_string
from app.services.base_service import BaseService


class CustomerService(BaseService[Customer]):
    """
    Service class to encapsulate business logic related to customers.
    This provides a layer of abstraction between the routes and the database models.
    """

    def __init__(self, customer_repository: Optional[CustomerRepository] = None) -> None:
        """
        Initialize the service with a repository.

        Args:
            customer_repository: The repository to use.
                If not provided, a new instance will be created.
        """
        repository = customer_repository or CustomerRepository()
        super().__init__(repository, Customer, validate_and_sanitize_customer_data, sanitize_string)

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        Get a customer by its primary key ID.

        Args:
            customer_id: The primary key ID of the customer

        Returns:
            The customer object or None if not found
        """
        return super().get_by_id(customer_id)

    def get_customer_by_cust_id(self, cust_id: str) -> Optional[Customer]:
        """
        Get a customer by its customer ID.

        Args:
            cust_id: The customer ID

        Returns:
            The customer object or None if not found
        """
        return self.repository.get_by_cust_id(cust_id)

    def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """
        Create a new customer with the given data.

        Args:
            customer_data: Dictionary containing customer attributes

        Returns:
            The newly created customer

        Raises:
            ValueError: If the customer data is invalid
            Exception: If there's an error creating the customer
        """
        return super().create(customer_data)

    def update_customer(self, customer: Customer, customer_data: Dict[str, Any]) -> Customer:
        """
        Update an existing customer with the given data.

        Args:
            customer: The customer object to update
            customer_data: Dictionary containing customer attributes to update

        Returns:
            The updated customer

        Raises:
            ValueError: If the customer data is invalid
            Exception: If there's an error updating the customer
        """
        return super().update(customer, customer_data)

    def delete_customer(self, customer: Customer) -> None:
        """
        Soft delete a customer by setting its deleted_at timestamp.

        Args:
            customer: The customer object to delete

        Raises:
            Exception: If there's an error soft deleting the customer
        """
        super().delete(customer)

    def hard_delete_customer(self, customer: Customer) -> None:
        """
        Permanently delete a customer from the database.
        This should be used with caution as it cannot be undone.

        Args:
            customer: The customer object to delete

        Raises:
            Exception: If there's an error deleting the customer
        """
        super().hard_delete(customer)

    def restore_customer(self, customer: Customer) -> Customer:
        """
        Restore a soft-deleted customer.

        Args:
            customer: The customer object to restore

        Returns:
            The restored customer

        Raises:
            Exception: If there's an error restoring the customer
        """
        return super().restore(customer)

    def get_deleted_customers(self) -> List[Customer]:
        """
        Get all soft-deleted customers.

        Returns:
            List of all soft-deleted customers
        """
        return super().get_deleted()

    def get_all_customers_including_deleted(self) -> List[Customer]:
        """
        Get all customers including soft-deleted ones.

        Returns:
            List of all customers including soft-deleted ones
        """
        return super().get_all_including_deleted()

    def search_customers(self, search_term: Optional[str] = None) -> List[Customer]:
        """
        Search for customers by name or ID.

        Args:
            search_term: Term to search for in customer name or ID

        Returns:
            List of matching customers
        """
        # Sanitize search term
        sanitized_search_term = self.sanitize_search_input(search_term)

        return self.repository.search(sanitized_search_term)

    def get_all_customers(self) -> List[Customer]:
        """
        Get all customers.

        Returns:
            List of all customers
        """
        return super().get_all()
