from flask import Flask
from app import create_app
from app.services.order_service import OrderService
from datetime import datetime, timedelta

# Create a test application
app = create_app()

# Use the application context
with app.app_context():
    # Create an instance of OrderService
    order_service = OrderService()
    
    # Test with string date parameters (this would have caused the error before the fix)
    print("Testing get_dueouts with string date parameters:")
    try:
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        dueouts = order_service.get_dueouts(start=start_date, end=end_date)
        print(f"Success! Found {len(dueouts)} orders")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test with date objects (this should work as before)
    print("\nTesting get_dueouts with date objects:")
    try:
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date() + timedelta(days=30)
        dueouts = order_service.get_dueouts(start=start_date, end=end_date)
        print(f"Success! Found {len(dueouts)} orders")
    except Exception as e:
        print(f"Error: {str(e)}")