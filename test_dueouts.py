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
    
    # Test with no date parameters
    print("Testing get_dueouts with no date parameters:")
    dueouts = order_service.get_dueouts()
    print(f"Found {len(dueouts)} orders")
    
    # Test with start date only (7 days ago)
    start_date = datetime.now().date() - timedelta(days=7)
    print(f"\nTesting get_dueouts with start date {start_date}:")
    dueouts = order_service.get_dueouts(start=start_date)
    print(f"Found {len(dueouts)} orders")
    
    # Test with end date only (7 days in the future)
    end_date = datetime.now().date() + timedelta(days=7)
    print(f"\nTesting get_dueouts with end date {end_date}:")
    dueouts = order_service.get_dueouts(end=end_date)
    print(f"Found {len(dueouts)} orders")
    
    # Test with both start and end date
    print(f"\nTesting get_dueouts with start date {start_date} and end date {end_date}:")
    dueouts = order_service.get_dueouts(start=start_date, end=end_date)
    print(f"Found {len(dueouts)} orders")
    
    # If there are any results, print the first few to verify ordering
    if dueouts:
        print("\nFirst few orders (should be ordered by earliest due date first):")
        for i, order in enumerate(dueouts[:5]):
            print(f"{i+1}. Log: {order.log}, Due Out: {order.dueout}")