"""
Base service module for common service functionality.

This module provides a base service class that implements common CRUD operations
and other shared functionality for all service classes. It reduces code duplication
by providing a common implementation that can be inherited by specific service classes.
"""

from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from app.repositories.base_repository import BaseRepository
from app.logging import get_logger

# Type variable for the model
T = TypeVar('T')

# Logger for this module
logger = get_logger(__name__)


class BaseService(Generic[T]):
    """
    Base service class that implements common functionality for all services.
    
    This class provides a generic implementation of common CRUD operations and
    other shared functionality. Specific service classes should inherit from this
    class and provide their own implementation of service-specific methods.
    """
    
    def __init__(self, repository: BaseRepository, model_class: Type[T], 
                 validator_func=None, sanitizer_func=None) -> None:
        """
        Initialize the service with a repository and model class.
        
        Args:
            repository: The repository to use for database operations
            model_class: The model class this service operates on
            validator_func: Function to validate and sanitize model data
            sanitizer_func: Function to sanitize search inputs
        """
        self.repository = repository
        self.model_class = model_class
        self.validator_func = validator_func
        self.sanitizer_func = sanitizer_func
        self.logger = logger
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Get an entity by its primary key ID.
        
        Args:
            entity_id: The primary key ID of the entity
            
        Returns:
            The entity object or None if not found
        """
        try:
            entity = self.repository.get_by_id(entity_id)
            if not entity:
                self.logger.warning(f"{self.model_class.__name__} with ID {entity_id} not found")
            return entity
        except Exception as e:
            self.logger.error(f"Error getting {self.model_class.__name__} by ID: {str(e)}")
            raise
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new entity with the given data.
        
        Args:
            data: Dictionary containing entity attributes
            
        Returns:
            The newly created entity
            
        Raises:
            ValueError: If the entity data is invalid
            Exception: If there's an error creating the entity
        """
        try:
            # Validate and sanitize the data if a validator function is provided
            validated_data = data
            if self.validator_func:
                validated_data = self.validator_func(data)
            
            entity = self.repository.create(validated_data)
            self.logger.info(f"Created new {self.model_class.__name__} with ID {entity.id}")
            return entity
        except ValueError as e:
            self.logger.warning(f"Invalid data for {self.model_class.__name__} creation: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating {self.model_class.__name__}: {str(e)}")
            raise
    
    def update(self, entity: T, data: Dict[str, Any]) -> T:
        """
        Update an existing entity with the given data.
        
        Args:
            entity: The entity object to update
            data: Dictionary containing entity attributes to update
            
        Returns:
            The updated entity
            
        Raises:
            ValueError: If the entity data is invalid
            Exception: If there's an error updating the entity
        """
        try:
            # Validate and sanitize the data if a validator function is provided
            validated_data = data
            if self.validator_func:
                validated_data = self.validator_func(data)
            
            updated_entity = self.repository.update(entity, validated_data)
            self.logger.info(f"Updated {self.model_class.__name__} with ID {entity.id}")
            return updated_entity
        except ValueError as e:
            self.logger.warning(f"Invalid data for {self.model_class.__name__} update: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error updating {self.model_class.__name__}: {str(e)}")
            raise
    
    def delete(self, entity: T) -> None:
        """
        Soft delete an entity by setting its deleted_at timestamp.
        
        Args:
            entity: The entity object to delete
            
        Raises:
            Exception: If there's an error soft deleting the entity
        """
        try:
            self.repository.delete(entity)
            self.logger.info(f"Soft deleted {self.model_class.__name__} with ID {entity.id}")
        except Exception as e:
            self.logger.error(f"Error soft deleting {self.model_class.__name__}: {str(e)}")
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
        try:
            self.repository.hard_delete(entity)
            self.logger.info(f"Hard deleted {self.model_class.__name__} with ID {entity.id}")
        except Exception as e:
            self.logger.error(f"Error hard deleting {self.model_class.__name__}: {str(e)}")
            raise
    
    def restore(self, entity: T) -> T:
        """
        Restore a soft-deleted entity.
        
        Args:
            entity: The entity object to restore
            
        Returns:
            The restored entity
            
        Raises:
            Exception: If there's an error restoring the entity
        """
        try:
            restored_entity = self.repository.restore(entity)
            self.logger.info(f"Restored {self.model_class.__name__} with ID {entity.id}")
            return restored_entity
        except Exception as e:
            self.logger.error(f"Error restoring {self.model_class.__name__}: {str(e)}")
            raise
    
    def get_deleted(self) -> List[T]:
        """
        Get all soft-deleted entities.
        
        Returns:
            List of all soft-deleted entities
        """
        try:
            return self.repository.get_deleted()
        except Exception as e:
            self.logger.error(f"Error getting deleted {self.model_class.__name__}s: {str(e)}")
            raise
    
    def get_all_including_deleted(self) -> List[T]:
        """
        Get all entities including soft-deleted ones.
        
        Returns:
            List of all entities including soft-deleted ones
        """
        try:
            return self.repository.get_all_including_deleted()
        except Exception as e:
            self.logger.error(f"Error getting all {self.model_class.__name__}s including deleted: {str(e)}")
            raise
    
    def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of all entities
        """
        try:
            return self.repository.get_all()
        except Exception as e:
            self.logger.error(f"Error getting all {self.model_class.__name__}s: {str(e)}")
            raise
    
    def sanitize_search_input(self, search_input: Optional[str]) -> Optional[str]:
        """
        Sanitize a search input string.
        
        Args:
            search_input: The search input to sanitize
            
        Returns:
            The sanitized search input or None if the input is None
        """
        if search_input is None:
            return None
        
        if self.sanitizer_func:
            return self.sanitizer_func(search_input)
        
        return search_input