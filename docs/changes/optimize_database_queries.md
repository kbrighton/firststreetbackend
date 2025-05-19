# Optimizing Database Queries to Reduce N+1 Problems

## Overview
This document outlines the changes made to optimize database queries and reduce N+1 query problems in the application. N+1 query problems occur when an application makes one query to fetch a list of items, and then makes additional queries for each item in the list to fetch related data. This results in N+1 queries (1 for the list, N for each item), which can significantly impact performance.

## Changes Made

### 1. Added Relationship Between Order and Customer Models
Added an explicit relationship between the Order and Customer models to allow for eager loading of related data:

```python
# In app/models/order.py
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# Modified the cust field to be a foreign key
cust = db.Column('CUST', db.String(5), ForeignKey('Customers.cust_id'), index=True)

# Added relationship to Customer
customer = relationship("Customer", foreign_keys=[cust], primaryjoin="Order.cust == Customer.cust_id", lazy="joined")
```

The `lazy="joined"` parameter ensures that the customer data is loaded eagerly when an order is fetched, which helps prevent N+1 query issues.

### 2. Updated OrderRepository Methods to Use Eager Loading
Modified the repository methods to explicitly use eager loading when fetching orders:

```python
# In app/repositories/order_repository.py
from sqlalchemy.orm import joinedload

# Updated get_by_log method
def get_by_log(self, log_id: str) -> Optional[Order]:
    query = db.select(self.model).options(joinedload(self.model.customer)).filter(
        self.model.log == log_id,
        self.model.deleted_at.is_(None)
    )
    return db.session.execute(query).scalar_one_or_none()

# Updated search method
def search(self, cust: str = None, title: str = None) -> List[Order]:
    # ...
    orders_query = db.select(self.model).options(joinedload(self.model.customer)).where(and_(*clauses))
    # ...

# Updated filter method
def filter(self, search: Optional[str] = None) -> Query:
    query = self.model.query.options(joinedload(self.model.customer)).filter(self.model.deleted_at.is_(None))
    # ...

# Updated get_dueouts method
def get_dueouts(self, start: date = None, end: date = None) -> List[Order]:
    duesql = db.select(self.model).options(joinedload(self.model.customer))
    # ...
```

### 3. Updated OrderSchema to Include Customer Data
Modified the OrderSchema to include customer data in the serialized output:

```python
# In app/schemas/order_schema.py
from marshmallow import fields

class OrderSchema(marshmallow.SQLAlchemyAutoSchema):
    # Include customer data in the schema
    customer_name = fields.Method("get_customer_name")
    
    def get_customer_name(self, obj):
        """Get the customer name from the related customer object"""
        if obj.customer:
            return obj.customer.customer
        return None
    
    class Meta:
        model = Order
        include_relationships = True
        fields = (
        "id", "log", "cust", "customer_name", "title", "datin", "artout", "dueout", "print_n", "artlo", "prior", "logtype", "colorf", "rush",
        "ref_artlo", "howship", "datout", "created_at", "updated_at")
        dateformat = "%x"
```

## Benefits
These changes provide the following benefits:

1. **Reduced Database Queries**: By eager loading related data, we reduce the number of database queries needed to fetch related customer data for orders.
2. **Improved Performance**: Fewer database queries means faster response times and reduced server load.
3. **Better Code Organization**: Explicit relationships between models make the code more maintainable and easier to understand.
4. **Enhanced Data Access**: The updated schema makes it easier to access customer data directly from serialized order data.

## Testing
The changes have been tested to ensure that:
1. Orders are correctly associated with their customers
2. Customer data is loaded efficiently when fetching orders
3. The application continues to function correctly with the optimized queries

## Conclusion
By implementing these changes, we've significantly reduced the N+1 query problems in the application, resulting in improved performance and efficiency.