"""
Base repository module providing a generic repository implementation.

This module defines an abstract base repository class that serves as a foundation for all
concrete repository implementations. It provides generic CRUD operations and query methods
that work with any SQLAlchemy model, implementing the repository pattern to abstract
data access logic from the rest of the application.

The BaseRepository class uses Python's Generic typing to provide type hints for the
specific model type that a concrete repository handles.
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Any, Dict, Type
from datetime import datetime

from app.extensions import db
from app.logging import get_logger
from sqlalchemy import and_

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """
    Abstract base repository class that defines the interface for all repositories.
    This provides a common set of methods for CRUD operations on database models.
    """
    # Create a logger for this class
    logger = get_logger(__name__)

    @property
    @abstractmethod
    def model(self) -> Type[T]:
        """
        The SQLAlchemy model class that this repository handles.
        Must be implemented by concrete repository classes.
        """
        pass

    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get an entity by its primary key ID.
        Only returns non-deleted entities.

        Args:
            id: The primary key ID of the entity

        Returns:
            The entity object or None if not found or deleted
        """
        self.logger.debug(f"Getting {self.model.__name__} by ID: {id}")
        try:
            entity = self.model.query.get(id)
            if entity and entity.deleted_at is None:
                self.logger.debug(f"Found {self.model.__name__} with ID: {id}")
                return entity
            else:
                self.logger.debug(f"No active {self.model.__name__} found with ID: {id}")
                return None
        except Exception as e:
            self.logger.error(f"Error getting {self.model.__name__} by ID {id}: {str(e)}")
            raise

    def get_all(self) -> List[T]:
        """
        Get all non-deleted entities.

        Returns:
            List of all non-deleted entities
        """
        self.logger.debug(f"Getting all active {self.model.__name__} entities")
        try:
            entities = self.model.query.filter(self.model.deleted_at.is_(None)).all()
            self.logger.debug(f"Retrieved {len(entities)} active {self.model.__name__} entities")
            return entities
        except Exception as e:
            self.logger.error(f"Error getting all active {self.model.__name__} entities: {str(e)}")
            raise

    def find_by(self, **kwargs) -> Optional[T]:
        """
        Find a non-deleted entity by the given criteria.

        Args:
            **kwargs: Criteria to filter by

        Returns:
            The entity object or None if not found or deleted
        """
        self.logger.debug(f"Finding active {self.model.__name__} by criteria: {kwargs}")
        try:
            # Add deleted_at is None to the filter criteria
            query = db.select(self.model).filter_by(**kwargs).filter(self.model.deleted_at.is_(None))
            entity = db.session.execute(query).scalar_one_or_none()
            if entity:
                self.logger.debug(f"Found active {self.model.__name__} matching criteria: {kwargs}")
            else:
                self.logger.debug(f"No active {self.model.__name__} found matching criteria: {kwargs}")
            return entity
        except Exception as e:
            self.logger.error(f"Error finding active {self.model.__name__} by criteria {kwargs}: {str(e)}")
            raise

    def find_all_by(self, **kwargs) -> List[T]:
        """
        Find all non-deleted entities matching the given criteria.

        Args:
            **kwargs: Criteria to filter by

        Returns:
            List of matching non-deleted entities
        """
        self.logger.debug(f"Finding all active {self.model.__name__} entities by criteria: {kwargs}")
        try:
            # Add deleted_at is None to the filter criteria
            query = db.select(self.model).filter_by(**kwargs).filter(self.model.deleted_at.is_(None))
            entities = db.session.execute(query).scalars().all()
            self.logger.debug(f"Found {len(entities)} active {self.model.__name__} entities matching criteria: {kwargs}")
            return entities
        except Exception as e:
            self.logger.error(f"Error finding active {self.model.__name__} entities by criteria {kwargs}: {str(e)}")
            raise

    def create(self, entity_data: Dict[str, Any]) -> T:
        """
        Create a new entity with the given data.

        Args:
            entity_data: Dictionary containing entity attributes

        Returns:
            The newly created entity

        Raises:
            Exception: If there's an error creating the entity
        """
        self.logger.info(f"Creating new {self.model.__name__} with data: {entity_data}")
        try:
            entity = self.model()
            for key, value in entity_data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            db.session.add(entity)
            db.session.commit()

            # Get the ID if available
            entity_id = getattr(entity, 'id', None)
            id_info = f" with ID: {entity_id}" if entity_id else ""
            self.logger.info(f"Created {self.model.__name__}{id_info}")

            return entity
        except Exception as e:
            self.logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            db.session.rollback()
            raise

    def update(self, entity: T, entity_data: Dict[str, Any]) -> T:
        """
        Update an existing entity with the given data.

        Args:
            entity: The entity object to update
            entity_data: Dictionary containing entity attributes to update

        Returns:
            The updated entity

        Raises:
            Exception: If there's an error updating the entity
        """
        # Get the ID if available
        entity_id = getattr(entity, 'id', None)
        id_info = f" with ID: {entity_id}" if entity_id else ""

        self.logger.info(f"Updating {self.model.__name__}{id_info}")
        self.logger.debug(f"Update data: {entity_data}")

        try:
            for key, value in entity_data.items():
                if hasattr(entity, key):
                    old_value = getattr(entity, key)
                    setattr(entity, key, value)
                    self.logger.debug(f"Updated {self.model.__name__} attribute '{key}' from '{old_value}' to '{value}'")

            db.session.commit()
            self.logger.info(f"Updated {self.model.__name__}{id_info}")
            return entity
        except Exception as e:
            self.logger.error(f"Error updating {self.model.__name__}{id_info}: {str(e)}")
            db.session.rollback()
            raise

    def delete(self, entity: T) -> None:
        """
        Soft delete an entity by setting its deleted_at timestamp.

        Args:
            entity: The entity object to delete

        Raises:
            Exception: If there's an error soft deleting the entity
        """
        # Get the ID if available
        entity_id = getattr(entity, 'id', None)
        id_info = f" with ID: {entity_id}" if entity_id else ""

        self.logger.warning(f"Soft deleting {self.model.__name__}{id_info}")
        try:
            # Set the deleted_at timestamp
            setattr(entity, 'deleted_at', datetime.now())
            db.session.commit()
            self.logger.info(f"Soft deleted {self.model.__name__}{id_info}")
        except Exception as e:
            self.logger.error(f"Error soft deleting {self.model.__name__}{id_info}: {str(e)}")
            db.session.rollback()
            raise

    def hard_delete(self, entity: T) -> None:
        """
        Permanently delete an entity from the database.
        This should be used with caution as it cannot be undone.

        Args:
            entity: The entity object to delete

        Raises:
            Exception: If there's an error deleting the entity
        """
        # Get the ID if available
        entity_id = getattr(entity, 'id', None)
        id_info = f" with ID: {entity_id}" if entity_id else ""

        self.logger.warning(f"Hard deleting {self.model.__name__}{id_info}")
        try:
            db.session.delete(entity)
            db.session.commit()
            self.logger.info(f"Hard deleted {self.model.__name__}{id_info}")
        except Exception as e:
            self.logger.error(f"Error hard deleting {self.model.__name__}{id_info}: {str(e)}")
            db.session.rollback()
            raise

    def exists(self, **kwargs) -> bool:
        """
        Check if a non-deleted entity with the given criteria exists.

        Args:
            **kwargs: Criteria to check

        Returns:
            True if the non-deleted entity exists, False otherwise
        """
        self.logger.debug(f"Checking if active {self.model.__name__} exists with criteria: {kwargs}")
        try:
            # Add deleted_at is None to the filter criteria
            query = db.select(self.model).filter_by(**kwargs).filter(self.model.deleted_at.is_(None))
            exists = db.session.execute(query).first() is not None
            self.logger.debug(f"Active {self.model.__name__} {'exists' if exists else 'does not exist'} with criteria: {kwargs}")
            return exists
        except Exception as e:
            self.logger.error(f"Error checking if active {self.model.__name__} exists with criteria {kwargs}: {str(e)}")
            raise

    def restore(self, entity: T) -> T:
        """
        Restore a soft-deleted entity by clearing its deleted_at timestamp.

        Args:
            entity: The entity object to restore

        Returns:
            The restored entity

        Raises:
            Exception: If there's an error restoring the entity
        """
        # Get the ID if available
        entity_id = getattr(entity, 'id', None)
        id_info = f" with ID: {entity_id}" if entity_id else ""

        self.logger.info(f"Restoring {self.model.__name__}{id_info}")
        try:
            # Clear the deleted_at timestamp
            setattr(entity, 'deleted_at', None)
            db.session.commit()
            self.logger.info(f"Restored {self.model.__name__}{id_info}")
            return entity
        except Exception as e:
            self.logger.error(f"Error restoring {self.model.__name__}{id_info}: {str(e)}")
            db.session.rollback()
            raise

    def get_all_including_deleted(self) -> List[T]:
        """
        Get all entities including deleted ones.

        Returns:
            List of all entities including deleted ones
        """
        self.logger.debug(f"Getting all {self.model.__name__} entities including deleted")
        try:
            entities = self.model.query.all()
            self.logger.debug(f"Retrieved {len(entities)} {self.model.__name__} entities including deleted")
            return entities
        except Exception as e:
            self.logger.error(f"Error getting all {self.model.__name__} entities including deleted: {str(e)}")
            raise

    def get_deleted(self) -> List[T]:
        """
        Get all deleted entities.

        Returns:
            List of all deleted entities
        """
        self.logger.debug(f"Getting all deleted {self.model.__name__} entities")
        try:
            entities = self.model.query.filter(self.model.deleted_at.isnot(None)).all()
            self.logger.debug(f"Retrieved {len(entities)} deleted {self.model.__name__} entities")
            return entities
        except Exception as e:
            self.logger.error(f"Error getting deleted {self.model.__name__} entities: {str(e)}")
            raise
