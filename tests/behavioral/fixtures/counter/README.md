# Counter service

This small synchronous Python service stores an integer total in SQLite.
`Counter(path).add(amount)` commits the increment and returns the total.
Each call is treated as a new request. `total()` returns the stored value.
It uses Python's standard library and requires no external service.
