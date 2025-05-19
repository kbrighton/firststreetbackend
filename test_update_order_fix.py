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

    # Get an existing order to update
    print("Getting an existing order...")
    orders = order_service.get_all()
    if not orders:
        print("No orders found to test with.")
        exit(1)

    order = orders[0]
    print(f"Found order with log: {order.log}")

    # Test updating with string date parameters (this would have caused the error before the fix)
    print("\nTesting update_order with string date parameters:")
    try:
        # Create update data with string dates
        update_data = {
            'title': f'Updated Order Title - {datetime.now().strftime("%H:%M:%S")}',
            'dueout': '2025-12-31',  # String date
            'artout': '2025-06-30'   # String date
        }

        # Update the order
        updated_order = order_service.update_order(order, update_data)

        print(f"Success! Order updated with title: {updated_order.title}")
        print(f"Due out date: {updated_order.dueout}")
        print(f"Art out date: {updated_order.artout}")
    except Exception as e:
        print(f"Error: {str(e)}")

    # Test with date objects (this should work as before)
    print("\nTesting update_order with date objects:")
    try:
        # Create update data with date objects
        update_data = {
            'title': f'Updated Order Title - {datetime.now().strftime("%H:%M:%S")}',
            'dueout': datetime.now().date() + timedelta(days=60),  # Date object
            'artout': datetime.now().date() + timedelta(days=30)   # Date object
        }

        # Update the order
        updated_order = order_service.update_order(order, update_data)

        print(f"Success! Order updated with title: {updated_order.title}")
        print(f"Due out date: {updated_order.dueout}")
        print(f"Art out date: {updated_order.artout}")
    except Exception as e:
        print(f"Error: {str(e)}")
