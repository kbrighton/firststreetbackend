import pytest
from unittest.mock import MagicMock, patch
from app.services.order_service import OrderService
from app.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.utils.validation import validate_and_sanitize_order_data, sanitize_string
from datetime import date, timedelta


class TestOrderService:
    """Test suite for the OrderService class."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        repo = MagicMock(spec=OrderRepository)
        repo.get_by_id.return_value = MagicMock(spec=Order, id=1, log="12345")
        repo.get_by_log.return_value = MagicMock(spec=Order, id=1, log="12345")
        repo.create.return_value = MagicMock(spec=Order, id=1, log="12345")
        repo.update.return_value = MagicMock(spec=Order, id=1, log="12345")
        repo.get_all.return_value = [MagicMock(spec=Order, id=i, log=f"{i}2345") for i in range(1, 4)]
        repo.search.return_value = [MagicMock(spec=Order, id=1, log="12345", title="Test Order")]
        repo.filter.return_value = MagicMock()
        repo.apply_sort.return_value = MagicMock()
        repo.paginate.return_value = MagicMock()
        repo.get_dueouts.return_value = [MagicMock(spec=Order, id=1, log="12345", dueout=date.today())]
        repo.exists.return_value = True
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create an OrderService instance for testing."""
        with patch('app.services.order_service.OrderRepository', return_value=mock_repository):
            return OrderService(order_repository=mock_repository)

    def test_init_with_repository(self, mock_repository):
        """Test initializing with a repository."""
        service = OrderService(order_repository=mock_repository)
        assert service.repository is mock_repository

    def test_init_without_repository(self):
        """Test initializing without a repository."""
        with patch('app.services.order_service.OrderRepository') as mock_repo_class:
            mock_repo_instance = MagicMock()
            mock_repo_class.return_value = mock_repo_instance
            
            service = OrderService()
            
            mock_repo_class.assert_called_once()
            assert service.repository is mock_repo_instance

    def test_get_order_by_log(self, service, mock_repository):
        """Test getting an order by log ID."""
        order = service.get_order_by_log("12345")
        
        mock_repository.get_by_log.assert_called_once_with("12345")
        assert order is not None
        assert order.log == "12345"

    def test_get_order_by_id(self, service, mock_repository):
        """Test getting an order by ID."""
        order = service.get_order_by_id(1)
        
        mock_repository.get_by_id.assert_called_once_with(1)
        assert order is not None
        assert order.id == 1

    def test_create_order(self, service, mock_repository):
        """Test creating an order."""
        with patch('app.services.order_service.validate_and_sanitize_order_data') as mock_validate:
            mock_validate.return_value = {"log": "12345", "title": "Test Order"}
            
            order_data = {"log": "12345", "title": "Test Order"}
            order = service.create_order(order_data)
            
            mock_validate.assert_called_once_with(order_data)
            mock_repository.create.assert_called_once_with({"log": "12345", "title": "Test Order"})
            assert order is not None
            assert order.id == 1
            assert order.log == "12345"

    def test_update_order(self, service, mock_repository):
        """Test updating an order."""
        with patch('app.services.order_service.validate_and_sanitize_order_data') as mock_validate:
            mock_validate.return_value = {"title": "Updated Order"}
            
            order = MagicMock(spec=Order, id=1, log="12345")
            order_data = {"title": "Updated Order"}
            updated_order = service.update_order(order, order_data)
            
            mock_validate.assert_called_once_with(order_data)
            mock_repository.update.assert_called_once_with(order, {"title": "Updated Order"})
            assert updated_order is not None
            assert updated_order.id == 1
            assert updated_order.log == "12345"

    def test_delete_order(self, service, mock_repository):
        """Test soft deleting an order."""
        order = MagicMock(spec=Order, id=1, log="12345")
        
        service.delete_order(order)
        
        mock_repository.delete.assert_called_once_with(order)

    def test_hard_delete_order(self, service, mock_repository):
        """Test hard deleting an order."""
        order = MagicMock(spec=Order, id=1, log="12345")
        
        service.hard_delete_order(order)
        
        mock_repository.hard_delete.assert_called_once_with(order)

    def test_restore_order(self, service, mock_repository):
        """Test restoring a soft-deleted order."""
        order = MagicMock(spec=Order, id=1, log="12345", deleted_at="2023-01-01")
        mock_repository.restore.return_value = MagicMock(spec=Order, id=1, log="12345", deleted_at=None)
        
        restored_order = service.restore_order(order)
        
        mock_repository.restore.assert_called_once_with(order)
        assert restored_order is not None
        assert restored_order.id == 1
        assert restored_order.log == "12345"
        assert restored_order.deleted_at is None

    def test_get_deleted_orders(self, service, mock_repository):
        """Test getting all soft-deleted orders."""
        mock_repository.get_deleted.return_value = [
            MagicMock(spec=Order, id=i, log=f"{i}2345", deleted_at="2023-01-01") 
            for i in range(4, 6)
        ]
        
        deleted_orders = service.get_deleted_orders()
        
        mock_repository.get_deleted.assert_called_once()
        assert len(deleted_orders) == 2
        assert all(hasattr(order, 'deleted_at') for order in deleted_orders)

    def test_get_all_orders_including_deleted(self, service, mock_repository):
        """Test getting all orders including soft-deleted ones."""
        mock_repository.get_all_including_deleted.return_value = [
            MagicMock(spec=Order, id=i, log=f"{i}2345") for i in range(1, 6)
        ]
        
        all_orders = service.get_all_orders_including_deleted()
        
        mock_repository.get_all_including_deleted.assert_called_once()
        assert len(all_orders) == 5

    def test_search_orders(self, service, mock_repository):
        """Test searching for orders."""
        with patch('app.services.order_service.sanitize_string') as mock_sanitize:
            mock_sanitize.side_effect = lambda x: f"sanitized_{x}" if x else None
            
            orders = service.search_orders(cust="12345", title="Test")
            
            assert mock_sanitize.call_count == 2
            mock_repository.search.assert_called_once_with("sanitized_12345", "sanitized_Test")
            assert len(orders) == 1
            assert orders[0].log == "12345"
            assert orders[0].title == "Test Order"

    def test_filter_orders(self, service, mock_repository):
        """Test filtering orders."""
        with patch('app.services.order_service.sanitize_string') as mock_sanitize:
            mock_sanitize.return_value = "sanitized_term"
            
            query = service.filter_orders("test")
            
            mock_sanitize.assert_called_once_with("test")
            mock_repository.filter.assert_called_once_with("sanitized_term")
            assert query is not None

    def test_order_query(self, service, mock_repository):
        """Test applying sorting to a query."""
        query = MagicMock()
        sorted_query = service.order_query(query, "log,title")
        
        mock_repository.apply_sort.assert_called_once_with(query, "log,title")
        assert sorted_query is not None

    def test_paginate_query(self, service, mock_repository):
        """Test paginating a query."""
        query = MagicMock()
        paginated = service.paginate_query(query, 1, 10)
        
        mock_repository.paginate.assert_called_once_with(query, 1, 10)
        assert paginated is not None

    def test_get_dueouts(self, service, mock_repository):
        """Test getting orders due out within a date range."""
        today = date.today()
        tomorrow = today + timedelta(days=1)
        
        orders = service.get_dueouts(today, tomorrow)
        
        mock_repository.get_dueouts.assert_called_once_with(today, tomorrow)
        assert len(orders) == 1
        assert orders[0].log == "12345"
        assert orders[0].dueout == today

    def test_check_order_exists(self, service, mock_repository):
        """Test checking if an order exists."""
        exists = service.check_order_exists("12345")
        
        mock_repository.exists.assert_called_once_with(log="12345")
        assert exists is True