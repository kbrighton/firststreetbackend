# Fix for `get_dueouts` Method

## Issue
There were two potential issues with the `get_dueouts` method in the `OrderRepository` class:

1. **Incorrect NULL comparison syntax**: The method was using `== None` and `!= None` for SQL NULL comparisons, which might not work correctly in all SQLAlchemy versions or configurations.

2. **Incorrect ordering**: The method was ordering results by due date in descending order (latest first), which might not be the most intuitive for users looking at orders that are due out soon.

## Solution
The following changes were made to fix these issues:

1. Changed the NULL comparison from `self.model.datout == None` to `self.model.datout.is_(None)` and from `self.model.dueout != None` to `self.model.dueout.isnot(None)`. This is the SQLAlchemy-recommended way to check for NULL values in database queries.

2. Changed the ordering from descending (`self.model.dueout.desc()`) to ascending (`self.model.dueout.asc()`). This means that orders with the earliest due dates will appear first, which is typically what users would expect when looking at orders that are due out.

## Testing
A test script was created to verify that the changes fixed the issues. The script tested the `get_dueouts` method with various date parameters and confirmed that:

1. The SQL queries are being generated with the proper syntax for NULL comparisons (`IS NULL` and `IS NOT NULL`)
2. The ordering is in ascending order by due date
3. The method returns the expected results based on the date parameters

## Files Changed
- `app/repositories/order_repository.py`: Modified the `get_dueouts` method to use proper NULL comparison syntax and ascending order by due date.