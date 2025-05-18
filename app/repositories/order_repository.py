"""
Order repository module for data access operations on Order entities.

This module provides a concrete implementation of the BaseRepository for Order entities,
offering specific query methods tailored to order data access needs, including search,
filtering, sorting, and pagination capabilities.
"""

from datetime import date
from typing import Optional, Type, List, Any, Union
from sqlalchemy.orm import Query, joinedload
from flask_sqlalchemy.pagination import Pagination

from sqlalchemy import and_, or_

from app.extensions import db
from app.models import Order
from app.repositories.base_repository import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """
    Repository for Order model operations.
    Implements the BaseRepository interface for the Order model.
    """

    @property
    def model(self) -> Type[Order]:
        """
        The SQLAlchemy model class that this repository handles.
        """
        return Order

    def get_by_log(self, log_id: str) -> Optional[Order]:
        """
        Get an order by its log ID.

        Args:
            log_id: The log ID of the order

        Returns:
            The order object or None if not found
        """
        # Use a query with joinedload to eager load the customer relationship
        query = db.select(self.model).options(joinedload(self.model.customer)).filter(
            self.model.log == log_id,
            self.model.deleted_at.is_(None)
        )
        return db.session.execute(query).scalar_one_or_none()

    def search(self, cust: str = None, title: str = None) -> List[Order]:
        """
        Search for non-deleted orders by customer and/or title.

        Args:
            cust: Customer to search for
            title: Title to search for

        Returns:
            List of matching non-deleted orders
        """
        clauses = [self.model.deleted_at.is_(None)]  # Only include non-deleted orders

        if cust:
            clauses.append(self.model.cust.ilike(f'%{cust}%'))

        if title:
            clauses.append(self.model.title.ilike(f'%{title}%'))

        # Use joinedload to eager load the customer relationship
        orders_query = db.select(self.model).options(joinedload(self.model.customer)).where(and_(*clauses)).order_by(self.model.datin.desc(), self.model.cust.desc())
        return db.session.execute(orders_query).scalars().all()

    def filter(self, search: Optional[str] = None) -> Query:
        """
        Filter non-deleted orders by search term (customer or title).

        Args:
            search: Search term

        Returns:
            Filtered query object with only non-deleted orders
        """
        # Start with a query that filters out deleted records and eager loads the customer relationship
        query = self.model.query.options(joinedload(self.model.customer)).filter(self.model.deleted_at.is_(None))

        if search:
            query = query.filter(or_(
                self.model.cust.ilike(f'%{search}%'),
                self.model.title.ilike(f'%{search}%')
            ))
        return query

    def apply_sort(self, query: Query, sort_argument: Optional[str] = None) -> Query:
        """
        Apply sorting to a query.

        Args:
            query: The query to sort
            sort_argument: Comma-separated list of fields to sort by

        Returns:
            Sorted query object
        """
        if sort_argument:
            sort_order = [getattr(self.model, s[1:]).desc() if s[0] == '-' else getattr(self.model, s[1:])
                          for s in sort_argument.split(',')]
            query = query.order_by(*sort_order)
        return query

    def paginate(self, query: Query, page: int, per_page: int) -> Pagination:
        """
        Paginate a query.

        Args:
            query: The query to paginate
            page: Page number
            per_page: Items per page

        Returns:
            Pagination object
        """
        return db.paginate(query, page=page, per_page=per_page)

    def get_dueouts(self, start: date = None, end: date = None) -> List[Order]:
        """
        Get non-deleted orders that are due out within a date range.

        Args:
            start: Start date
            end: End date

        Returns:
            List of non-deleted orders due out in the date range
        """
        # Use joinedload to eager load the customer relationship
        duesql = db.select(self.model).options(joinedload(self.model.customer))
        # Filter out deleted records
        duesql = duesql.where(self.model.deleted_at.is_(None))
        duesql = duesql.where((self.model.logtype == "TR") | (self.model.logtype == "DP") | (self.model.logtype == "AA"))
        duesql = duesql.where(self.model.datout.is_(None))
        duesql = duesql.where(self.model.dueout.isnot(None))

        if start is not None:
            duesql = duesql.where(self.model.dueout >= start)

        if end is not None:
            duesql = duesql.where(self.model.dueout <= end)

        duesql = duesql.order_by(self.model.dueout.asc())

        return db.session.execute(duesql).scalars().all()
