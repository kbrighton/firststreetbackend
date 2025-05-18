from app.extensions import db
from sqlalchemy import event
import re
from typing import Dict, Any, Optional
from datetime import datetime


"""
Customer model representing customer information in the system.

This module defines the Customer model which stores information about customers,
including contact details, billing information, and shipping addresses.
It also provides validation methods to ensure data integrity.
"""


class Customer(db.Model):
    """
    Customer model for storing customer information.

    This class represents a customer in the system and contains all the fields
    necessary to track customer information, including contact details,
    billing information, and shipping addresses.

    Attributes:
        id (int): Primary key for the customer.
        cust_id (str): Unique customer identifier.
        customer_id (str): Secondary customer identifier.
        customer (str): Customer name.
        address_line_1 (str): First line of billing address.
        address_line_2 (str): Second line of billing address.
        city (str): City for billing address.
        state (str): State for billing address.
        zip (str): ZIP code for billing address.
        bill_to_contact (str): Contact person for billing.
        telephone_1 (str): Primary telephone number.
        telephone_2 (str): Secondary telephone number.
        fax_number (str): Fax number.
        tax_id (str): Tax identification number.
        resale_no (str): Resale number.
        cust_since (datetime): Date when customer relationship began.
        ship_to_1_address_line_1 (str): First line of shipping address.
        ship_to_1_address_line_2 (str): Second line of shipping address.
        ship_to_1_city (str): City for shipping address.
        ship_to_1_state (str): State for shipping address.
        ship_to_1_zip (str): ZIP code for shipping address.
        customer_email (str): Customer email address.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
        deleted_at (datetime): Timestamp when the record was soft-deleted, or None if active.
    """
    __tablename__ = 'Customers'

    id = db.Column(db.Integer, db.Identity(), primary_key=True, nullable=False)
    cust_id = db.Column('CUSTID', db.String(255), unique=True, index=True)  # Changed from primary_key to unique
    customer_id = db.Column('Customer ID', db.String(255))
    customer = db.Column('Customer', db.String(255))
    address_line_1 = db.Column('Address Line 1', db.String(255))
    address_line_2 = db.Column('Address Line 2', db.String(255))
    city = db.Column('City', db.String(255))
    state = db.Column('State', db.String(255))
    zip = db.Column('Zip', db.String(255))
    bill_to_contact = db.Column('Bill To Contact', db.String(255))
    telephone_1 = db.Column('Telephone 1', db.String(255))
    telephone_2 = db.Column('Telephone 2', db.String(255))
    fax_number = db.Column('Fax Number', db.String(255))
    tax_id = db.Column('Tax ID', db.String(255))
    resale_no = db.Column('Resale No', db.String(255))
    cust_since = db.Column('Cust Since', db.DateTime(True))
    ship_to_1_address_line_1 = db.Column('Ship to 1 Address Line 1', db.String(255))
    ship_to_1_address_line_2 = db.Column('Ship to 1 Address Line 2', db.String(255))
    ship_to_1_city = db.Column('Ship to 1 City ', db.String(255))
    ship_to_1_state = db.Column('Ship to 1 State ', db.String(255))
    ship_to_1_zip = db.Column('Ship to 1 Zip ', db.String(255))
    customer_email = db.Column('Customer E-mail', db.String(255))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """
        Return a string representation of the Customer object.

        Returns:
            str: String representation of the Customer.
        """
        return f'<Customer "{self.customer}">'

    def validate_data(self) -> Dict[str, str]:
        """
        Validate the customer data against business rules.

        This method checks various fields of the customer for validity, including:
        - Customer ID format and length
        - Customer name length
        - Email format
        - ZIP code format
        - Phone number format

        Returns:
            Dict[str, str]: A dictionary mapping field names to error messages if validation fails,
                           or an empty dictionary if all validations pass.
        """
        errors = {}

        # Validate cust_id
        if self.cust_id:
            if not self._validate_alphanumeric(self.cust_id) or not self._validate_length(self.cust_id, 5, 5):
                errors['cust_id'] = "Customer ID must be exactly 5 alphanumeric characters"

        # Validate customer name
        if self.customer:
            if not self._validate_length(self.customer, 1, 255):
                errors['customer'] = "Customer name must be between 1 and 255 characters"

        # Validate email
        if self.customer_email:
            if not self._validate_email(self.customer_email):
                errors['customer_email'] = "Invalid email format"

        # Validate zip code
        if self.zip:
            if not self._validate_zip(self.zip):
                errors['zip'] = "Invalid ZIP code format"

        # Validate phone numbers
        if self.telephone_1:
            if not self._validate_phone(self.telephone_1):
                errors['telephone_1'] = "Invalid phone number format"

        if self.telephone_2:
            if not self._validate_phone(self.telephone_2):
                errors['telephone_2'] = "Invalid phone number format"

        return errors

    @staticmethod
    def _validate_alphanumeric(value: str, allow_empty: bool = False) -> bool:
        """
        Validate that a string contains only alphanumeric characters.

        Args:
            value (str): The string to validate.
            allow_empty (bool, optional): Whether to allow empty strings. Defaults to False.

        Returns:
            bool: True if the string is valid, False otherwise.
        """
        if value is None or value == "":
            return allow_empty

        return bool(re.match(r'^[A-Za-z0-9]+$', value))

    @staticmethod
    def _validate_length(value: str, min_length: int = 0, max_length: Optional[int] = None) -> bool:
        """
        Validate that a string's length is within the specified range.

        Args:
            value (str): The string to validate.
            min_length (int, optional): The minimum allowed length. Defaults to 0.
            max_length (Optional[int], optional): The maximum allowed length. Defaults to None.

        Returns:
            bool: True if the string length is valid, False otherwise.
        """
        if value is None:
            return min_length == 0

        length = len(value)

        if length < min_length:
            return False

        if max_length is not None and length > max_length:
            return False

        return True

    @staticmethod
    def _validate_email(value: str) -> bool:
        """
        Validate email format.

        Args:
            value (str): The email address to validate.

        Returns:
            bool: True if the email format is valid or if the value is empty, False otherwise.
        """
        if not value:
            return True

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, value))

    @staticmethod
    def _validate_zip(value: str) -> bool:
        """
        Validate ZIP code format.

        Accepts 5-digit (12345) or 5+4 digit (12345-6789) formats.

        Args:
            value (str): The ZIP code to validate.

        Returns:
            bool: True if the ZIP code format is valid or if the value is empty, False otherwise.
        """
        if not value:
            return True

        # Allow 5-digit or 5+4 digit formats
        zip_pattern = r'^\d{5}(?:-\d{4})?$'
        return bool(re.match(zip_pattern, value))

    @staticmethod
    def _validate_phone(value: str) -> bool:
        """
        Validate phone number format.

        Accepts 10-digit phone numbers or 11-digit numbers with a leading 1.
        Common separators (spaces, hyphens, parentheses, periods) are removed before validation.

        Args:
            value (str): The phone number to validate.

        Returns:
            bool: True if the phone number format is valid or if the value is empty, False otherwise.
        """
        if not value:
            return True

        # Remove common separators for validation
        clean_phone = re.sub(r'[\s\-\(\)\.]+', '', value)

        # Check if it's a valid phone number (10 digits, or 11 with leading 1)
        return bool(re.match(r'^1?\d{10}$', clean_phone))


@event.listens_for(Customer, 'before_insert')
@event.listens_for(Customer, 'before_update')
def validate_customer(mapper, connection, customer):
    """
    Validate customer data before insert or update operations.

    This function is registered as an event listener for both 'before_insert' and 'before_update'
    events on the Customer model. It calls the validate_data method on the customer instance and
    raises a ValueError if any validation errors are found.

    Args:
        mapper: The SQLAlchemy mapper that is the target of this event.
        connection: The SQLAlchemy connection being used for the operation.
        customer (Customer): The customer instance being inserted or updated.

    Raises:
        ValueError: If validation fails, with a message containing all validation errors.
    """
    errors = customer.validate_data()
    if errors:
        error_messages = "; ".join([f"{field}: {message}" for field, message in errors.items()])
        raise ValueError(f"Customer validation failed: {error_messages}")
