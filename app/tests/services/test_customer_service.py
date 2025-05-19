import pytest
from unittest.mock import MagicMock, patch
from app.services.customer_service import CustomerService
from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.utils.validation import validate_and_sanitize_customer_data, sanitize_string


class TestCustomerService:
    """Test suite for the CustomerService class."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository for testing."""
        repo = MagicMock(spec=CustomerRepository)
        repo.get_by_id.return_value = MagicMock(spec=Customer, id=1, cust_id="12345")
        repo.get_by_cust_id.return_value = MagicMock(spec=Customer, id=1, cust_id="12345")
        repo.create.return_value = MagicMock(spec=Customer, id=1, cust_id="12345")
        repo.update.return_value = MagicMock(spec=Customer, id=1, cust_id="12345")
        repo.get_all.return_value = [MagicMock(spec=Customer, id=i, cust_id=f"{i}2345") for i in range(1, 4)]
        repo.search.return_value = [MagicMock(spec=Customer, id=1, cust_id="12345", customer="Test Customer")]
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create a CustomerService instance for testing."""
        with patch('app.services.customer_service.CustomerRepository', return_value=mock_repository):
            return CustomerService(customer_repository=mock_repository)

    def test_init_with_repository(self, mock_repository):
        """Test initializing with a repository."""
        service = CustomerService(customer_repository=mock_repository)
        assert service.repository is mock_repository

    def test_init_without_repository(self):
        """Test initializing without a repository."""
        with patch('app.services.customer_service.CustomerRepository') as mock_repo_class:
            mock_repo_instance = MagicMock()
            mock_repo_class.return_value = mock_repo_instance
            
            service = CustomerService()
            
            mock_repo_class.assert_called_once()
            assert service.repository is mock_repo_instance

    def test_get_customer_by_id(self, service, mock_repository):
        """Test getting a customer by ID."""
        customer = service.get_customer_by_id(1)
        
        mock_repository.get_by_id.assert_called_once_with(1)
        assert customer is not None
        assert customer.id == 1

    def test_get_customer_by_cust_id(self, service, mock_repository):
        """Test getting a customer by customer ID."""
        customer = service.get_customer_by_cust_id("12345")
        
        mock_repository.get_by_cust_id.assert_called_once_with("12345")
        assert customer is not None
        assert customer.cust_id == "12345"

    def test_create_customer(self, service, mock_repository):
        """Test creating a customer."""
        with patch('app.services.customer_service.validate_and_sanitize_customer_data') as mock_validate:
            mock_validate.return_value = {"cust_id": "12345", "customer": "Test Customer"}
            
            customer_data = {"cust_id": "12345", "customer": "Test Customer"}
            customer = service.create_customer(customer_data)
            
            mock_validate.assert_called_once_with(customer_data)
            mock_repository.create.assert_called_once_with({"cust_id": "12345", "customer": "Test Customer"})
            assert customer is not None
            assert customer.id == 1
            assert customer.cust_id == "12345"

    def test_update_customer(self, service, mock_repository):
        """Test updating a customer."""
        with patch('app.services.customer_service.validate_and_sanitize_customer_data') as mock_validate:
            mock_validate.return_value = {"customer": "Updated Customer"}
            
            customer = MagicMock(spec=Customer, id=1, cust_id="12345")
            customer_data = {"customer": "Updated Customer"}
            updated_customer = service.update_customer(customer, customer_data)
            
            mock_validate.assert_called_once_with(customer_data)
            mock_repository.update.assert_called_once_with(customer, {"customer": "Updated Customer"})
            assert updated_customer is not None
            assert updated_customer.id == 1
            assert updated_customer.cust_id == "12345"

    def test_delete_customer(self, service, mock_repository):
        """Test soft deleting a customer."""
        customer = MagicMock(spec=Customer, id=1, cust_id="12345")
        
        service.delete_customer(customer)
        
        mock_repository.delete.assert_called_once_with(customer)

    def test_hard_delete_customer(self, service, mock_repository):
        """Test hard deleting a customer."""
        customer = MagicMock(spec=Customer, id=1, cust_id="12345")
        
        service.hard_delete_customer(customer)
        
        mock_repository.hard_delete.assert_called_once_with(customer)

    def test_restore_customer(self, service, mock_repository):
        """Test restoring a soft-deleted customer."""
        customer = MagicMock(spec=Customer, id=1, cust_id="12345", deleted_at="2023-01-01")
        mock_repository.restore.return_value = MagicMock(spec=Customer, id=1, cust_id="12345", deleted_at=None)
        
        restored_customer = service.restore_customer(customer)
        
        mock_repository.restore.assert_called_once_with(customer)
        assert restored_customer is not None
        assert restored_customer.id == 1
        assert restored_customer.cust_id == "12345"
        assert restored_customer.deleted_at is None

    def test_get_deleted_customers(self, service, mock_repository):
        """Test getting all soft-deleted customers."""
        mock_repository.get_deleted.return_value = [
            MagicMock(spec=Customer, id=i, cust_id=f"{i}2345", deleted_at="2023-01-01") 
            for i in range(4, 6)
        ]
        
        deleted_customers = service.get_deleted_customers()
        
        mock_repository.get_deleted.assert_called_once()
        assert len(deleted_customers) == 2
        assert all(hasattr(customer, 'deleted_at') for customer in deleted_customers)

    def test_get_all_customers_including_deleted(self, service, mock_repository):
        """Test getting all customers including soft-deleted ones."""
        mock_repository.get_all_including_deleted.return_value = [
            MagicMock(spec=Customer, id=i, cust_id=f"{i}2345") for i in range(1, 6)
        ]
        
        all_customers = service.get_all_customers_including_deleted()
        
        mock_repository.get_all_including_deleted.assert_called_once()
        assert len(all_customers) == 5

    def test_search_customers(self, service, mock_repository):
        """Test searching for customers."""
        with patch('app.services.customer_service.sanitize_string') as mock_sanitize:
            mock_sanitize.return_value = "sanitized_term"
            
            customers = service.search_customers("test")
            
            mock_sanitize.assert_called_once_with("test")
            mock_repository.search.assert_called_once_with("sanitized_term")
            assert len(customers) == 1
            assert customers[0].cust_id == "12345"
            assert customers[0].customer == "Test Customer"

    def test_get_all_customers(self, service, mock_repository):
        """Test getting all customers."""
        customers = service.get_all_customers()
        
        mock_repository.get_all.assert_called_once()
        assert len(customers) == 3