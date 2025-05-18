"""
Customer repository module for data access operations on Customer entities.

This module provides a concrete implementation of the BaseRepository for Customer entities,
offering specific query methods tailored to customer data access needs.
"""

from typing import Optional, Type, List

from sqlalchemy import or_

from app.extensions import db
from app.models import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """
    Repository for Customer model operations.
    Implements the BaseRepository interface for the Customer model.
    """

    @property
    def model(self) -> Type[Customer]:
        """
        The SQLAlchemy model class that this repository handles.
        """
        return Customer

    def get_by_cust_id(self, cust_id: str) -> Optional[Customer]:
        """
        Get a customer by its customer ID.

        Args:
            cust_id: The customer ID to search for

        Returns:
            The customer object or None if not found
        """
        return self.find_by(cust_id=cust_id)

    def search(self, search_term: str = None) -> List[Customer]:
        """
        Search for non-deleted customers by name or ID.

        Args:
            search_term: Term to search for in customer name or ID

        Returns:
            List of matching non-deleted customers
        """
        query = db.select(self.model).filter(self.model.deleted_at.is_(None))
        if search_term:
            query = query.filter(
                or_(
                    self.model.customer.ilike(f'%{search_term}%'),
                    self.model.cust_id.ilike(f'%{search_term}%')
                )
            )
        return db.session.execute(query).scalars().all()
