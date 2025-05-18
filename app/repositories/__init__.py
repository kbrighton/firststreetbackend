"""
Repositories package for data access.

This package contains repository classes that encapsulate the data access logic of the application.
Repositories act as an abstraction layer between the services and the database,
providing methods for CRUD operations and queries on specific domain entities.

Each repository class is responsible for a specific domain entity (e.g., Order, Customer, User)
and provides methods for creating, reading, updating, and deleting those entities.
The repository pattern helps to isolate the application from changes in the data source
and makes the code more testable.
"""
