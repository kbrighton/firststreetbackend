import pytest
from unittest.mock import MagicMock, patch
from app.services.base_service import BaseService
from app.models.customer import Customer
from app.extensions import db
from datetime import datetime


class TestBaseService:
    """Test suite for the BaseService class."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        repo = MagicMock()
        repo.get_by_id.return_value = MagicMock(spec=Customer, id=1)
        repo.create.return_value = MagicMock(spec=Customer, id=1)
        repo.update.return_value = MagicMock(spec=Customer, id=1)
        repo.get_all.return_value = [MagicMock(spec=Customer, id=i) for i in range(1, 4)]
        repo.get_deleted.return_value = [MagicMock(spec=Customer, id=i, deleted_at=datetime.now()) for i in range(4, 6)]
        repo.get_all_including_deleted.return_value = [MagicMock(spec=Customer, id=i) for i in range(1, 6)]
        return repo

    @pytest.fixture
    def mock_validator(self):
        """Create a mock validator function for testing."""
        return MagicMock(return_value={"validated": True})

    @pytest.fixture
    def mock_sanitizer(self):
        """Create a mock sanitizer function for testing."""
        return MagicMock(return_value="sanitized")

    @pytest.fixture
    def service(self, mock_repository, mock_validator, mock_sanitizer):
        """Create a BaseService instance for testing."""
        return BaseService(
            repository=mock_repository,
            model_class=Customer,
            validator_func=mock_validator,
            sanitizer_func=mock_sanitizer
        )

    def test_get_by_id(self, service, mock_repository):
        """Test getting an entity by ID."""
        entity = service.get_by_id(1)
        
        mock_repository.get_by_id.assert_called_once_with(1)
        assert entity is not None
        assert entity.id == 1

    def test_get_by_id_not_found(self, service, mock_repository):
        """Test getting a non-existent entity by ID."""
        mock_repository.get_by_id.return_value = None
        
        entity = service.get_by_id(999)
        
        mock_repository.get_by_id.assert_called_once_with(999)
        assert entity is None

    def test_create(self, service, mock_repository, mock_validator):
        """Test creating an entity."""
        data = {"name": "Test"}
        entity = service.create(data)
        
        mock_validator.assert_called_once_with(data)
        mock_repository.create.assert_called_once_with({"validated": True})
        assert entity is not None
        assert entity.id == 1

    def test_create_without_validator(self, mock_repository):
        """Test creating an entity without a validator function."""
        service = BaseService(repository=mock_repository, model_class=Customer)
        data = {"name": "Test"}
        
        entity = service.create(data)
        
        mock_repository.create.assert_called_once_with(data)
        assert entity is not None
        assert entity.id == 1

    def test_update(self, service, mock_repository, mock_validator):
        """Test updating an entity."""
        entity = MagicMock(spec=Customer, id=1)
        data = {"name": "Updated"}
        
        updated_entity = service.update(entity, data)
        
        mock_validator.assert_called_once_with(data)
        mock_repository.update.assert_called_once_with(entity, {"validated": True})
        assert updated_entity is not None
        assert updated_entity.id == 1

    def test_update_without_validator(self, mock_repository):
        """Test updating an entity without a validator function."""
        service = BaseService(repository=mock_repository, model_class=Customer)
        entity = MagicMock(spec=Customer, id=1)
        data = {"name": "Updated"}
        
        updated_entity = service.update(entity, data)
        
        mock_repository.update.assert_called_once_with(entity, data)
        assert updated_entity is not None
        assert updated_entity.id == 1

    def test_delete(self, service, mock_repository):
        """Test soft deleting an entity."""
        entity = MagicMock(spec=Customer, id=1)
        
        service.delete(entity)
        
        mock_repository.delete.assert_called_once_with(entity)

    def test_hard_delete(self, service, mock_repository):
        """Test hard deleting an entity."""
        entity = MagicMock(spec=Customer, id=1)
        
        service.hard_delete(entity)
        
        mock_repository.hard_delete.assert_called_once_with(entity)

    def test_restore(self, service, mock_repository):
        """Test restoring a soft-deleted entity."""
        entity = MagicMock(spec=Customer, id=1, deleted_at=datetime.now())
        mock_repository.restore.return_value = MagicMock(spec=Customer, id=1, deleted_at=None)
        
        restored_entity = service.restore(entity)
        
        mock_repository.restore.assert_called_once_with(entity)
        assert restored_entity is not None
        assert restored_entity.id == 1
        assert restored_entity.deleted_at is None

    def test_get_deleted(self, service, mock_repository):
        """Test getting all soft-deleted entities."""
        deleted_entities = service.get_deleted()
        
        mock_repository.get_deleted.assert_called_once()
        assert len(deleted_entities) == 2
        assert all(entity.deleted_at is not None for entity in deleted_entities)

    def test_get_all_including_deleted(self, service, mock_repository):
        """Test getting all entities including soft-deleted ones."""
        all_entities = service.get_all_including_deleted()
        
        mock_repository.get_all_including_deleted.assert_called_once()
        assert len(all_entities) == 5

    def test_get_all(self, service, mock_repository):
        """Test getting all active entities."""
        active_entities = service.get_all()
        
        mock_repository.get_all.assert_called_once()
        assert len(active_entities) == 3

    def test_sanitize_search_input(self, service, mock_sanitizer):
        """Test sanitizing search input."""
        sanitized = service.sanitize_search_input("test")
        
        mock_sanitizer.assert_called_once_with("test")
        assert sanitized == "sanitized"

    def test_sanitize_search_input_none(self, service, mock_sanitizer):
        """Test sanitizing None search input."""
        sanitized = service.sanitize_search_input(None)
        
        mock_sanitizer.assert_not_called()
        assert sanitized is None

    def test_sanitize_search_input_without_sanitizer(self, mock_repository):
        """Test sanitizing search input without a sanitizer function."""
        service = BaseService(repository=mock_repository, model_class=Customer)
        
        sanitized = service.sanitize_search_input("test")
        
        assert sanitized == "test"

    def test_error_handling(self, service, mock_repository):
        """Test error handling in service methods."""
        mock_repository.get_by_id.side_effect = Exception("Test error")
        
        with pytest.raises(Exception) as excinfo:
            service.get_by_id(1)
        
        assert "Test error" in str(excinfo.value)