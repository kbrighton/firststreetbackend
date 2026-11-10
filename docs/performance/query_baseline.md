# Order Query Baseline

Captured on 2026-11-09 with `app/tests/test_query_baselines.py` on the project's SQLite in-memory test database.

```powershell
$env:TEST_DATABASE_URL='sqlite:///:memory:'
.\.venv\Scripts\python.exe -m pytest -q -s app/tests/test_query_baselines.py
```

The deterministic dataset contains 500 synthetic orders for one customer. It includes soft-deleted orders, shipped orders, and due dates spanning today through 14 days from today. The benchmark measures each authenticated request from the Flask test client, counts all SQL statements executed during that request (including the user lookup), counts returned order rows, and runs `EXPLAIN QUERY PLAN` for SQLite statements referencing `Orders`.

The before/after comparison below uses the initial full-row baseline and the latest run after applying an 18-field list projection that matches `OrderSchema`. Row counts and statement counts remained unchanged.

| Workflow | Rows | Queries (before → after) | Latency ms (before → after) |
| --- | ---: | ---: | ---: |
| `/api/data?start=0&length=25` | 25 | 3 → 3 | 7.756 → 8.270 |
| `/order_search/` (page 1) | 20 | 3 → 3 | 46.118 → 43.184 |
| `/api/orders/dueouts` (14-day range) | 188 | 2 → 2 | 26.870 → 10.656 |

The projection reduces each order-list `SELECT` to the 18 fields serialized by `OrderSchema`; detail/update reads remain full model reads. Query counts show no deferred-column N+1 queries. SQLite still reported a table scan for each order query; the paginated search page and due-outs plans also used a temporary B-tree for ordering, while `/api/data` count and page plans did not. The due-outs regression coverage verifies inclusive date boundaries, shipped/deleted/type exclusions, and returned API/UI content. The focused API, UI, search-pagination, schema, configuration, and benchmark suite passed 31 tests; SQLAlchemy emitted existing `Query.get()` deprecation warnings.

Each latency is one local request measurement and the change is not a statistically robust performance claim. The configured production database engine and representative production data volume were not available, and in-memory SQLite plans are not transferable to another engine. No index or migration is justified by this evidence; rerun the benchmark on the deployed engine and a larger representative dataset before drawing production conclusions.
