from datetime import date, timedelta
from app.models.order import Order
from app.extensions import db
from app import create_app

# Create a test app context
app = create_app('testing')
with app.app_context():
    # Create an order with a past date for artout and dueout
    two_days_ago = date.today() - timedelta(days=2)
    yesterday = date.today() - timedelta(days=1)
    
    test_order = Order(
        log="TEST1",
        cust="12345",
        title="Test Order with Past Date",
        datin=two_days_ago,  # Earlier date than dueout to pass date range validation
        artout=yesterday,    # Past date for artout
        dueout=yesterday,    # Past date for dueout (but after datin)
        logtype="TR",
        print_n=100,
        colorf=2,
        subtotal=500.0,
        total=550.0
    )
    
    # Validate the order data
    errors = test_order.validate_data()
    
    # Print the validation results
    if errors:
        print("Validation failed with errors:")
        for field, error in errors.items():
            print(f"  {field}: {error}")
    else:
        print("Validation passed! Past dates are now accepted.")
        
    # Check if the specific validation methods return True for past dates
    print("\nTesting validation methods directly:")
    print(f"_validate_date_not_in_past(yesterday): {Order._validate_date_not_in_past(yesterday)}")
    
    # Try to save the order to the database
    try:
        db.session.add(test_order)
        db.session.commit()
        print("\nOrder with past dates successfully saved to database!")
        db.session.delete(test_order)  # Clean up
        db.session.commit()
    except Exception as e:
        print(f"\nError saving order: {str(e)}")
        db.session.rollback()