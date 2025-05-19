# Soft Delete Implementation

## Overview
This document outlines the implementation of soft delete functionality for important entities in the system. Soft delete allows records to be marked as deleted without actually removing them from the database, which provides the ability to restore deleted data if needed.

## Changes Made

### 1. Model Changes
Added a `deleted_at` timestamp field to the following models:
- `Customer` model
- `Order` model
- `User` model

When a record is soft deleted, this field is set to the current timestamp. Non-deleted records have this field set to `NULL`.

### 2. Repository Layer Changes
Modified the `BaseRepository` class to:
- Change the `delete` method to implement soft delete by setting the `deleted_at` timestamp
- Add a `hard_delete` method for cases where permanent deletion is needed
- Add a `restore` method to restore soft-deleted records
- Add `get_all_including_deleted` and `get_deleted` methods to retrieve deleted records
- Update all query methods to filter out soft-deleted records by default

Updated repository-specific query methods to filter out deleted records:
- `CustomerRepository.search`
- `OrderRepository.search`
- `OrderRepository.filter`
- `OrderRepository.get_dueouts`

### 3. Service Layer Changes
Updated all service classes to support soft delete functionality:
- `CustomerService`
- `OrderService`
- `UserService`

Added new methods to each service:
- `hard_delete_*` - For permanent deletion
- `restore_*` - To restore soft-deleted records
- `get_deleted_*` - To retrieve soft-deleted records
- `get_all_*_including_deleted` - To retrieve all records including deleted ones

### 4. Database Migration
Created a new migration script to add the `deleted_at` column to all relevant tables:
- `Customers` table
- `Orders` table
- `user` table

## Usage

### Soft Delete
To soft delete a record, use the existing delete methods:
```python
customer_service.delete_customer(customer)
order_service.delete_order(order)
user_service.delete_user(user)
```

### Hard Delete
To permanently delete a record:
```python
customer_service.hard_delete_customer(customer)
order_service.hard_delete_order(order)
user_service.hard_delete_user(user)
```

### Restore
To restore a soft-deleted record:
```python
customer_service.restore_customer(customer)
order_service.restore_order(order)
user_service.restore_user(user)
```

### Retrieving Deleted Records
To get all soft-deleted records:
```python
deleted_customers = customer_service.get_deleted_customers()
deleted_orders = order_service.get_deleted_orders()
deleted_users = user_service.get_deleted_users()
```

To get all records including deleted ones:
```python
all_customers = customer_service.get_all_customers_including_deleted()
all_orders = order_service.get_all_orders_including_deleted()
all_users = user_service.get_all_users_including_deleted()
```

## Benefits
1. Data Recovery: Accidentally deleted data can be restored
2. Data Integrity: Maintains referential integrity by not actually removing records
3. Audit Trail: Provides a history of deleted records
4. User Experience: Allows for "trash bin" functionality where users can restore deleted items