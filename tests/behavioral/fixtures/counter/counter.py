"""Small local service fixture. Every accepted call adds to a durable total."""

import sqlite3


class Counter:
    def __init__(self, path):
        self.path = path
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS totals (id INTEGER PRIMARY KEY, value INTEGER NOT NULL)")
            db.execute("INSERT OR IGNORE INTO totals VALUES (1, 0)")

    def add(self, amount):
        with sqlite3.connect(self.path) as db:
            db.execute("UPDATE totals SET value = value + ? WHERE id = 1", (amount,))
            return db.execute("SELECT value FROM totals WHERE id = 1").fetchone()[0]

    def total(self):
        with sqlite3.connect(self.path) as db:
            return db.execute("SELECT value FROM totals WHERE id = 1").fetchone()[0]
