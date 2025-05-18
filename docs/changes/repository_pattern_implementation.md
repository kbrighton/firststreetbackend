# Repository Pattern Implementation

## Overview

This document describes the implementation of the repository pattern for database access in the FirstStreet Backend application. The repository pattern is a design pattern that separates the data access logic from the business logic, providing an abstraction layer between the data source (database) and the business logic.

## Benefits

- **Separation of Concerns**: Separates data access logic from business logic
- **Testability**: Makes it easier to unit test services by mocking repositories
- **Flexibility**: Makes it easier to change the data source without affecting the business logic
- **Maintainability**: Centralizes data access logic, making it easier to maintain
- **Consistency**: Provides a consistent interface for data access operations

## Implementation

### Structure

The repository pattern implementation consists of the following components:

1. **Base Repository**: An abstract base class that defines the common interface for all repositories
2. **Concrete Repositories**: Implementations of the base repository for specific models
3. **Service Layer**: Uses repositories to access data instead of directly accessing the database

### Base Repository

The `BaseRepository` class is an abstract base class that defines the common interface for all repositories. It provides methods for CRUD operations and querying entities.

```python
class BaseRepository(Generic[T], ABC):
    """
    Abstract base repository class that defines the interface for all repositories.
    This provides a common set of methods for CRUD operations on database models.
    """

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        """
        The SQLAlchemy model class that this repository handles.
        Must be implemented by concrete repository classes.
        """
        pass

    def get_by_id(self, id: Any) -> Optional[T]:
        """Get an entity by its primary key ID."""
        return self.model.query.get(id)

    def get_all(self) -> List[T]:
        """Get all entities."""
        return self.model.query.all()

    def find_by(self, **kwargs) -> Optional[T]:
        """Find an entity by the given criteria."""
        return db.session.execute(db.select(self.model).filter_by(**kwargs)).scalar_one_or_none()

    def find_all_by(self, **kwargs) -> List[T]:
        """Find all entities matching the given criteria."""
        return db.session.execute(db.select(self.model).filter_by(**kwargs)).scalars().all()

    def create(self, entity_data: Dict[str, Any]) -> T:
        """Create a new entity with the given data."""
        entity = self.model()
        for key, value in entity_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        db.session.add(entity)
        db.session.commit()
        return entity

    def update(self, entity: T, entity_data: Dict[str, Any]) -> T:
        """Update an existing entity with the given data."""
        for key, value in entity_data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        db.session.commit()
        return entity

    def delete(self, entity: T) -> None:
        """Delete an entity."""
        db.session.delete(entity)
        db.session.commit()

    def exists(self, **kwargs) -> bool:
        """Check if an entity with the given criteria exists."""
        return db.session.execute(db.select(self.model).filter_by(**kwargs)).first() is not None
```

### Concrete Repositories

Concrete repositories implement the base repository for specific models. They provide model-specific methods and override the `model` property.

Example: `UserRepository`

```python
class UserRepository(BaseRepository[User]):
    """
    Repository for User model operations.
    Implements the BaseRepository interface for the User model.
    """

    @property
    def model(self) -> Type[User]:
        """The SQLAlchemy model class that this repository handles."""
        return User

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.find_by(username=username)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.find_by(email=email)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.get_by_username(username)
        if user is None or not user.check_password(password):
            return None
        return user
```

### Service Layer

The service layer uses repositories to access data instead of directly accessing the database. This provides a clean separation of concerns and makes the code more maintainable and testable.

Example: `UserService`

```python
class UserService:
    """
    Service class to encapsulate business logic related to users.
    This provides a layer of abstraction between the routes and the database models.
    """

    def __init__(self, user_repository=None):
        """Initialize the service with a repository."""
        self.repository = user_repository or UserRepository()

    def get_user_by_id(self, user_id):
        """Get a user by its primary key ID."""
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username):
        """Get a user by its username."""
        return self.repository.get_by_username(username)

    def create_user(self, username, email, password):
        """Create a new user."""
        user_data = {
            'username': username,
            'email': email
        }
        user = self.repository.create(user_data)
        user.set_password(password)
        return self.repository.update(user, {})  # Save the password hash

    # Other methods...
```

## Usage

### Creating a New Repository

To create a new repository for a model:

1. Create a new file in the `app/repositories` directory
2. Define a class that inherits from `BaseRepository` with the model as the type parameter
3. Implement the `model` property to return the model class
4. Add any model-specific methods

Example:

```python
from app.models import MyModel
from app.repositories.base_repository import BaseRepository

class MyModelRepository(BaseRepository[MyModel]):
    @property
    def model(self):
        return MyModel

    # Add model-specific methods here
```

### Using a Repository in a Service

To use a repository in a service:

1. Import the repository class
2. Initialize the repository in the service's `__init__` method
3. Use the repository's methods to access data

Example:

```python
from app.repositories.my_model_repository import MyModelRepository

class MyModelService:
    def __init__(self, repository=None):
        self.repository = repository or MyModelRepository()

    def get_by_id(self, id):
        return self.repository.get_by_id(id)

    # Add service methods here
```

### Testing with Repositories

The repository pattern makes it easier to test services by mocking repositories:

```python
from unittest.mock import Mock
from app.services.user_service import UserService

def test_get_user_by_id():
    # Create a mock repository
    mock_repository = Mock()
    mock_repository.get_by_id.return_value = "mock_user"

    # Create a service with the mock repository
    service = UserService(mock_repository)

    # Test the service
    user = service.get_user_by_id(1)
    assert user == "mock_user"
    mock_repository.get_by_id.assert_called_once_with(1)
```

## Conclusion

The repository pattern provides a clean separation of concerns between data access logic and business logic. It makes the code more maintainable, testable, and flexible. By implementing this pattern, we've improved the architecture of the FirstStreet Backend application.