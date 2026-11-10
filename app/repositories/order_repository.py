"""
Order repository module for data access operations on Order entities.

This module provides a concrete implementation of the BaseRepository for Order entities,
offering specific query methods tailored to order data access needs, including search,
filtering, sorting, and pagination capabilities.
"""

from datetime import date
from typing import Optional, Type, List, Any

from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import and_, or_
from sqlalchemy.orm import load_only

from app.extensions import db
from app.models import Order
from app.repositories.base_repository import BaseRepository


SORTABLE_ORDER_FIELDS = frozenset({
    'id', 'log', 'artlo', 'cust', 'title', 'prior', 'datin', 'dueout',
    'colorf', 'print_n', 'logtype', 'rush', 'datout',
})
ORDER_LIST_FIELDS = (
    'id', 'log', 'cust', 'title', 'datin', 'artout', 'dueout', 'print_n',
    'artlo', 'prior', 'logtype', 'colorf', 'rush', 'ref_artlo', 'howship',
    'datout', 'created_at', 'updated_at',
)


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

    def _with_list_projection(self, query: Any) -> Any:
        """Load only the fields serialized by the order list schema."""
        return query.options(
            load_only(*(getattr(self.model, field) for field in ORDER_LIST_FIELDS))
        )

    def get_by_log(self, log_id: str) -> Optional[Order]:
        """
        Get an order by its log ID.

        Args:
            log_id: The log ID of the order

        Returns:
            The order object or None if not found
        """
        # Query for the order by log ID
        query = db.select(self.model).filter(
            self.model.log == log_id,
            self.model.deleted_at.is_(None)
        )
        return db.session.execute(query).scalar_one_or_none()

    def _search_query(
        self, cust: Optional[str] = None, title: Optional[str] = None
    ) -> Any:
        """Build the filtered, consistently ordered order-search query."""
        clauses = [self.model.deleted_at.is_(None)]

        if cust:
            clauses.append(self.model.cust.ilike(f'%{cust}%'))

        if title:
            clauses.append(self.model.title.ilike(f'%{title}%'))

        return db.select(self.model).where(and_(*clauses)).order_by(
            self.model.datin.desc(), self.model.cust.desc(), self.model.id.desc()
        )

    def search(self, cust: Optional[str] = None, title: Optional[str] = None) -> List[Order]:
        """
        Search for non-deleted orders by customer and/or title.

        Args:
            cust: Customer to search for
            title: Title to search for

        Returns:
            List of matching non-deleted orders
        """
        return db.session.execute(self._search_query(cust, title)).scalars().all()

    def search_paginated(
        self,
        cust: str,
        title: str,
        page: int,
        per_page: int,
        sort_argument: Optional[str] = None,
    ) -> Pagination:
        """Return one database-paginated page of matching orders."""
        query = self._search_query(cust, title)
        if sort_argument:
            query = self.apply_sort(query.order_by(None), sort_argument)
        return db.paginate(
            self._with_list_projection(query),
            page=page,
            per_page=per_page,
            error_out=False,
        )

    def filter(self, search: Optional[str] = None) -> Any:
        """
        Filter non-deleted orders by search term (customer or title).

        Args:
            search: Search term

        Returns:
            Filtered query object with only non-deleted orders
        """
        # Start with a query that filters out deleted records
        query = self._with_list_projection(
            db.select(self.model).filter(self.model.deleted_at.is_(None))
        )

        if search:
            query = query.filter(or_(
                self.model.cust.ilike(f'%{search}%'),
                self.model.title.ilike(f'%{search}%')
            ))
        return query

    def apply_sort(self, query: Any, sort_argument: Optional[str] = None) -> Any:
        """
        Apply sorting to a query.

        Args:
            query: The query to sort
            sort_argument: Comma-separated list of fields to sort by

        Returns:
            Sorted query object
        """
        if not sort_argument:
            return query

        sort_order = []
        sort_fields = set()
        for raw_term in sort_argument.split(','):
            term = raw_term.strip()
            if not term:
                raise ValueError('Sort terms must specify a supported order field')

            direction = term[0] if term[0] in '+-' else '+'
            field_name = term[1:] if term[0] in '+-' else term
            if field_name not in SORTABLE_ORDER_FIELDS:
                raise ValueError(f'Unsupported sort field: {field_name or term}')

            field = getattr(self.model, field_name)
            sort_order.append(field.desc() if direction == '-' else field.asc())
            sort_fields.add(field_name)

        if 'id' not in sort_fields:
            sort_order.append(self.model.id.desc())

        return query.order_by(*sort_order)

    def paginate(self, query: Any, page: int, per_page: int) -> Pagination:
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
        # Ensure start and end are date objects if provided
        if start is not None and not isinstance(start, date):
            if isinstance(start, str):
                try:
                    from datetime import datetime
                    start = datetime.strptime(start, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"Invalid start date format: {start}. Expected format: YYYY-MM-DD")
            else:
                raise TypeError(f"start must be a date object or a string in YYYY-MM-DD format, got {type(start)}")

        if end is not None and not isinstance(end, date):
            if isinstance(end, str):
                try:
                    from datetime import datetime
                    end = datetime.strptime(end, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"Invalid end date format: {end}. Expected format: YYYY-MM-DD")
            else:
                raise TypeError(f"end must be a date object or a string in YYYY-MM-DD format, got {type(end)}")

        # Query for orders due out within the date range
        duesql = self._with_list_projection(db.select(self.model))
        # Filter out deleted records
        duesql = duesql.where(self.model.deleted_at.is_(None))
        duesql = duesql.where((self.model.logtype == "TR") | (self.model.logtype == "DP") | (self.model.logtype == "AA") | (self.model.logtype == "DTF"))
        duesql = duesql.where(self.model.datout.is_(None))
        duesql = duesql.where(self.model.dueout.isnot(None))

        if start is not None:
            duesql = duesql.where(self.model.dueout >= start)

        if end is not None:
            duesql = duesql.where(self.model.dueout <= end)

        duesql = duesql.order_by(self.model.dueout.asc())

        return db.session.execute(duesql).scalars().all()
