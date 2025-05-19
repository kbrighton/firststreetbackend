from app.extensions import db
from sqlalchemy import event, ForeignKey
from sqlalchemy.orm import relationship
import re
from datetime import date, datetime
from typing import Dict, Any, Optional, List


"""
Order model representing customer orders in the system.

This module defines the Order model which stores information about customer orders,
including order details, pricing, artwork information, and shipping details.
It also provides validation methods to ensure data integrity.
"""


class Order(db.Model):
    """
    Order model for storing customer order information.

    This class represents an order in the system and contains all the fields
    necessary to track an order from creation to completion, including
    customer information, artwork details, pricing, and shipping information.

    Attributes:
        id (int): Primary key for the order.
        log (str): Unique log identifier for the order.
        cust (str): Customer identifier.
        cust_p_0 (str): Customer purchase order number.
        prior (str): Priority indicator.
        shipout (str): Shipping method code.
        howship (str): Shipping carrier code.
        weight (float): Weight of the order.
        artlo (str): Artwork log identifier.
        datin (date): Date the order was received.
        artout (date): Date the artwork was completed.
        dueout (date): Due date for the order.
        logtype (str): Type of order (e.g., TR, DP, AA).
        datout (date): Date the order was shipped.
        title (str): Title or description of the order.
        subtotal (float): Subtotal amount before tax and shipping.
        sales_tax (float): Sales tax amount.
        ship_frght (float): Shipping and freight charges.
        total (float): Total order amount.
        rush (bool): Indicates if this is a rush order.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
        deleted_at (datetime): Timestamp when the record was soft-deleted, or None if active.
    """
    __tablename__ = 'Orders'

    id = db.Column(db.Integer, db.Identity(), primary_key=True, nullable=False)
    log = db.Column('LOG', db.String(7), unique=True, index=True)
    cust = db.Column('CUST', db.String(5), index=True)
    cust_p_0 = db.Column('CUST_P_0', db.String(8))
    prior = db.Column('PRIOR', db.String(1))
    shipout = db.Column('SHIPOUT', db.String(5))
    howship = db.Column('HOWSHIP', db.String(5))
    weight = db.Column('WEIGHT', db.Float(53))
    artlo = db.Column('ARTLO', db.String(5))
    datin = db.Column('DATIN', db.Date)
    artout = db.Column('ARTOUT', db.Date)
    dueout = db.Column('DUEOUT', db.Date)
    logtype = db.Column('LOGTYPE', db.String(5))
    datout = db.Column('DATOUT', db.Date)
    colorf = db.Column('COLORF', db.Float(53))
    inktyp = db.Column('INKTYP', db.Float(53))
    colori = db.Column('COLORI', db.Float(53))
    print_n = db.Column('PRINT_N', db.Float(53))
    rush_n = db.Column('RUSH_N', db.Float(53))
    colorc_n = db.Column('COLORC_N', db.Float(53))
    gang_n = db.Column('GANG_N', db.Float(53))
    artc_n = db.Column('ARTC_N', db.Float(53))
    appl_n = db.Column('APPL_N', db.Float(53))
    adhes_n = db.Column('ADHES_N', db.Float(53))
    let_nu_n = db.Column('LET_NU_N', db.Float(53))
    garmnt_n = db.Column('GARMNT_N', db.Float(53))
    print_c = db.Column('PRINT_C', db.Float(53))
    rush_c = db.Column('RUSH_C', db.Float(53))
    colorc_c = db.Column('COLORC_C', db.Float(53))
    gang_c = db.Column('GANG_C', db.Float(53))
    artc_c = db.Column('ARTC_C', db.Float(53))
    appl_c = db.Column('APPL_C', db.Float(53))
    adhes_c = db.Column('ADHES_C', db.Float(53))
    let_nu_c = db.Column('LET_NU_C', db.Float(53))
    garmnt_c = db.Column('GARMNT_C', db.Float(53))
    print_t = db.Column('PRINT_T', db.Float(53))
    rush_t = db.Column('RUSH_T', db.Float(53))
    colorc_t = db.Column('COLORC_T', db.Float(53))
    gang_t = db.Column('GANG_T', db.Float(53))
    artc_t = db.Column('ARTC_T', db.Float(53))
    appl_t = db.Column('APPL_T', db.Float(53))
    adhes_t = db.Column('ADHES_T', db.Float(53))
    let_nu_t = db.Column('LET_NU_T', db.Float(53))
    garmnt_t = db.Column('GARMNT_T', db.Float(53))
    subtotal = db.Column('SUBTOTAL', db.Float(53))
    sales_tax = db.Column('SALES_TAX', db.Float(53))
    ship_frght = db.Column('SHIP_FRGHT', db.Float(53))
    total = db.Column('TOTAL', db.Float(53))
    art_1 = db.Column('ART_1', db.String(5))
    art_2 = db.Column('ART_2', db.String(5))
    art_3 = db.Column('ART_3', db.String(5))
    art_4 = db.Column('ART_4', db.String(5))
    art_5 = db.Column('ART_5', db.String(5))
    art_6 = db.Column('ART_6', db.String(5))
    art_7 = db.Column('ART_7', db.String(5))
    art_8 = db.Column('ART_8', db.String(5))
    art_9 = db.Column('ART_9', db.String(5))
    print_1 = db.Column('PRINT_1', db.String(5))
    print_2 = db.Column('PRINT_2', db.String(5))
    print_3 = db.Column('PRINT_3', db.String(5))
    print_4 = db.Column('PRINT_4', db.String(5))
    print_5 = db.Column('PRINT_5', db.String(5))
    print_6 = db.Column('PRINT_6', db.String(5))
    print_7 = db.Column('PRINT_7', db.String(5))
    print_8 = db.Column('PRINT_8', db.String(5))
    print_9 = db.Column('PRINT_9', db.String(5))
    a1 = db.Column('A1', db.Float(53))
    a2 = db.Column('A2', db.Float(53))
    a3 = db.Column('A3', db.Float(53))
    a4 = db.Column('A4', db.Float(53))
    a5 = db.Column('A5', db.Float(53))
    a6 = db.Column('A6', db.Float(53))
    a7 = db.Column('A7', db.Float(53))
    a8 = db.Column('A8', db.Float(53))
    a9 = db.Column('A9', db.Float(53))
    p1 = db.Column('P1', db.Float(53))
    p2 = db.Column('P2', db.Float(53))
    p3 = db.Column('P3', db.Float(53))
    p4 = db.Column('P4', db.Float(53))
    p5 = db.Column('P5', db.Float(53))
    p6 = db.Column('P6', db.Float(53))
    p7 = db.Column('P7', db.Float(53))
    p8 = db.Column('P8', db.Float(53))
    p9 = db.Column('P9', db.Float(53))
    title = db.Column('TITLE', db.String(256))
    let_style = db.Column('LET_STYLE', db.String(5))
    ref_artlo = db.Column('REF_ARTLO', db.String(5))
    artpag = db.Column('ARTPAG', db.String(3))
    artno = db.Column('ARTNO', db.String(5))
    artencl = db.Column('ARTENCL', db.String(1))
    ret_art = db.Column('RET_ART', db.String(1))
    reorder = db.Column('REORDER', db.String(1))
    cust_info = db.Column('CUST_INFO', db.String(95))
    locate = db.Column('LOCATE', db.String(15))
    set_1 = db.Column('SET_1', db.String(5))
    set_2 = db.Column('SET_2', db.String(5))
    set_3 = db.Column('SET_3', db.String(5))
    set_4 = db.Column('SET_4', db.String(5))
    pck_1 = db.Column('PCK_1', db.String(5))
    pck_2 = db.Column('PCK_2', db.String(5))
    pck_3 = db.Column('PCK_3', db.String(5))
    pck_4 = db.Column('PCK_4', db.String(5))
    s1 = db.Column('S1', db.Float(53))
    s2 = db.Column('S2', db.Float(53))
    s3 = db.Column('S3', db.Float(53))
    s4 = db.Column('S4', db.Float(53))
    u1 = db.Column('U1', db.Float(53))
    u2 = db.Column('U2', db.Float(53))
    u3 = db.Column('U3', db.Float(53))
    u4 = db.Column('U4', db.Float(53))
    artd_1 = db.Column('ARTD_1', db.Date)
    artd_2 = db.Column('ARTD_2', db.Date)
    artd_3 = db.Column('ARTD_3', db.Date)
    artd_4 = db.Column('ARTD_4', db.Date)
    artd_5 = db.Column('ARTD_5', db.Date)
    artd_6 = db.Column('ARTD_6', db.Date)
    artd_7 = db.Column('ARTD_7', db.Date)
    artd_8 = db.Column('ARTD_8', db.Date)
    artd_9 = db.Column('ARTD_9', db.Date)
    arto_1 = db.Column('ARTO_1', db.Date)
    arto_2 = db.Column('ARTO_2', db.Date)
    arto_3 = db.Column('ARTO_3', db.Date)
    arto_4 = db.Column('ARTO_4', db.Date)
    arto_5 = db.Column('ARTO_5', db.Date)
    arto_6 = db.Column('ARTO_6', db.Date)
    arto_7 = db.Column('ARTO_7', db.Date)
    arto_8 = db.Column('ARTO_8', db.Date)
    arto_9 = db.Column('ARTO_9', db.Date)
    lupd = db.Column('LUPD', db.Date)
    origpr = db.Column('ORIGPR', db.String(1))
    rush = db.Column('RUSH', db.Boolean())
    late = db.Column('LATE', db.Float(53))
    timeout = db.Column('TIMEOUT', db.String(8))
    timein = db.Column('TIMEIN', db.String(8))
    out = db.Column('OUT', db.Float(53))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())
    deleted_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        """
        Return a string representation of the Order object.

        Returns:
            str: String representation of the Order.
        """
        return f'<Order "{self.log}">'

    def validate_data(self) -> Dict[str, str]:
        """
        Validate the order data against business rules.

        This method checks various fields of the order for validity, including:
        - Log number format and length
        - Customer number format and length
        - Title length
        - Art log format and length
        - Numeric field ranges (quantities, prices, etc.)
        - Log type validity
        - Date validations (not in past, proper ranges)

        Returns:
            Dict[str, str]: A dictionary mapping field names to error messages if validation fails,
                           or an empty dictionary if all validations pass.
        """
        errors = {}

        # Validate log
        if self.log:
            if not self._validate_alphanumeric(self.log) or not self._validate_length(self.log, 5, 7):
                errors['log'] = "LOG# must be between 5 and 7 alphanumeric characters"

        # Validate cust
        if self.cust:
            if not self._validate_alphanumeric(self.cust) or not self._validate_length(self.cust, 5, 5):
                errors['cust'] = "Customer# must be exactly 5 alphanumeric characters"

        # Validate title
        if self.title:
            if not self._validate_length(self.title, 1, 256):
                errors['title'] = "Title must be between 1 and 256 characters"

        # Validate artlo
        if self.artlo:
            if not re.match(r'^[A-Za-z0-9\-_]*$', self.artlo) or not self._validate_length(self.artlo, 0, 5):
                errors['artlo'] = "Art Log must contain only letters, numbers, hyphens, and underscores, and be at most 5 characters"

        # Validate ref_artlo
        if self.ref_artlo:
            if not self._validate_alphanumeric(self.ref_artlo, True) or not self._validate_length(self.ref_artlo, 0, 5):
                errors['ref_artlo'] = "Art Reference must be at most 5 alphanumeric characters"

        # Validate artno
        if self.artno:
            if not self._validate_alphanumeric(self.artno, True) or not self._validate_length(self.artno, 0, 5):
                errors['artno'] = "Artist ID must be at most 5 alphanumeric characters"

        # Validate numeric fields
        numeric_fields = [
            ('print_n', "Quantity"),
            ('colorf', "Number of colors"),
            ('weight', "Weight"),
            ('subtotal', "Subtotal"),
            ('sales_tax', "Sales Tax"),
            ('ship_frght', "Shipping"),
            ('total', "Total")
        ]

        for field_name, display_name in numeric_fields:
            value = getattr(self, field_name, None)
            if value is not None and not self._validate_number_range(value, 0):
                errors[field_name] = f"{display_name} must be a non-negative number"

        # Validate logtype
        if self.logtype:
            valid_logtypes = ["TR", "DP", "AA", "VG", "DG", "GM", "DTF", "PP"]
            if self.logtype not in valid_logtypes:
                errors['logtype'] = f"Log Type must be one of: {', '.join(valid_logtypes)}"

        # Validate dates
        date_fields = [
            ('datin', "Date In"),
            ('artout', "Art Out"),
            ('dueout', "Due Out"),
            ('datout', "Date Out")
        ]

        for field_name, display_name in date_fields:
            value = getattr(self, field_name, None)
            if field_name in ['artout', 'dueout'] and value and not self._validate_date_not_in_past(value):
                errors[field_name] = f"{display_name} cannot be in the past"

        # Validate date ranges
        if self.datin and self.dueout and not self._validate_date_range(self.datin, self.dueout):
            errors['dueout'] = "Due Out date must be after Date In"

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
    def _validate_number_range(value: float, min_value: Optional[float] = None, max_value: Optional[float] = None) -> bool:
        """
        Validate that a number is within the specified range.

        Args:
            value (float): The number to validate.
            min_value (Optional[float], optional): The minimum allowed value. Defaults to None.
            max_value (Optional[float], optional): The maximum allowed value. Defaults to None.

        Returns:
            bool: True if the number is within the valid range, False otherwise.
        """
        if value is None:
            return True

        if min_value is not None and value < min_value:
            return False

        if max_value is not None and value > max_value:
            return False

        return True

    @staticmethod
    def _validate_date_not_in_past(value: date) -> bool:
        """
        Validate that a date is not in the past.

        Args:
            value (date): The date to validate.

        Returns:
            bool: True if the date is today or in the future, False otherwise.
        """
        if value is None:
            return True

        return value >= date.today()

    @staticmethod
    def _validate_date_range(start_date: date, end_date: date) -> bool:
        """
        Validate that the end date is after the start date.

        Args:
            start_date (date): The start date.
            end_date (date): The end date.

        Returns:
            bool: True if the end date is on or after the start date, False otherwise.
        """
        if start_date is None or end_date is None:
            return True

        return end_date >= start_date


@event.listens_for(Order, 'before_insert')
@event.listens_for(Order, 'before_update')
def validate_order(mapper, connection, order):
    """
    Validate order data before insert or update operations.

    This function is registered as an event listener for both 'before_insert' and 'before_update'
    events on the Order model. It calls the validate_data method on the order instance and
    raises a ValueError if any validation errors are found.

    Args:
        mapper: The SQLAlchemy mapper that is the target of this event.
        connection: The SQLAlchemy connection being used for the operation.
        order (Order): The order instance being inserted or updated.

    Raises:
        ValueError: If validation fails, with a message containing all validation errors.
    """
    errors = order.validate_data()
    if errors:
        error_messages = "; ".join([f"{field}: {message}" for field, message in errors.items()])
        raise ValueError(f"Order validation failed: {error_messages}")
