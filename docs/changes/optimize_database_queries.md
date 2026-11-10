# Historical Database Optimization Proposal (Not Implemented)

> This document records an earlier proposal, not changes that were applied. Its suggested `Order.customer` relationship and `customer_name` schema field are absent from the current model and schema; use the code and current baseline as authoritative.

## Current implementation

- `Order.cust` is stored as a string and does not define a foreign key or relationship to `Customer`.
- `OrderSchema` does not serialize customer relationship data.
- Order list queries project the fields in `OrderSchema` to avoid loading unused model columns; detail and update reads continue to use full `Order` records.
- No new index was added. The available query plans are from a 500-order in-memory SQLite dataset and do not justify a production index.

See [`docs/performance/query_baseline.md`](../performance/query_baseline.md) for the measured baseline and limitations.

## Superseded proposal

The original draft proposed adding a customer foreign key and relationship, using `joinedload` in order queries, and adding a customer name to the serialized order schema. Those changes were never implemented and should not be treated as current guidance. Revisit this design only if the data model and product contract explicitly establish an order-to-customer relationship.
