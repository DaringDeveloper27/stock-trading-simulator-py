import sqlite3
from datetime import datetime, timezone


class Database:
    def __init__(self, path="market.db", starting_cash=10_000.0):
        self.path = path
        self._initialize(starting_cash)

    def connect(self):
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self, starting_cash):
        with self.connect() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS account (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    cash REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS holdings (
                    symbol TEXT PRIMARY KEY,
                    quantity INTEGER NOT NULL CHECK (quantity >= 0)
                );

                CREATE TABLE IF NOT EXISTS daily_prices (
                    symbol TEXT NOT NULL,
                    price_date TEXT NOT NULL,
                    close REAL NOT NULL CHECK (close > 0),
                    fetched_at TEXT NOT NULL,
                    PRIMARY KEY (symbol, price_date)
                );

                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    price REAL NOT NULL CHECK (price > 0),
                    total REAL NOT NULL,
                    traded_at TEXT NOT NULL
                );
            """)
            con.execute(
                "INSERT OR IGNORE INTO account (id, cash) VALUES (1, ?)",
                (starting_cash,)
            )

    def get_cash_balance(self):
        with self.connect() as con:
            row = con.execute("SELECT cash FROM account WHERE id = 1").fetchone()
            return float(row[0])

    def get_holdings(self):
        with self.connect() as con:
            return con.execute(
                "SELECT symbol, quantity FROM holdings WHERE quantity > 0 ORDER BY symbol"
            ).fetchall()

    def save_price_history(self, symbol, rows):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.connect() as con:
            con.executemany("""
                INSERT INTO daily_prices (symbol, price_date, close, fetched_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(symbol, price_date)
                DO UPDATE SET close=excluded.close, fetched_at=excluded.fetched_at
            """, [(symbol, date, float(close), now) for date, close in rows if close and close > 0])

    def get_latest_price(self, symbol):
        with self.connect() as con:
            row = con.execute("""
                SELECT close FROM daily_prices
                WHERE symbol = ?
                ORDER BY price_date DESC LIMIT 1
            """, (symbol,)).fetchone()
            return float(row[0]) if row else None

    def get_latest_prices(self):
        with self.connect() as con:
            return con.execute("""
                SELECT p.symbol, p.close, p.price_date
                FROM daily_prices p
                JOIN (
                    SELECT symbol, MAX(price_date) AS latest_date
                    FROM daily_prices GROUP BY symbol
                ) latest
                ON p.symbol = latest.symbol AND p.price_date = latest.latest_date
                ORDER BY p.symbol
            """).fetchall()

    def get_price_history(self, symbol, limit=20):
        with self.connect() as con:
            return con.execute("""
                SELECT price_date, close FROM daily_prices
                WHERE symbol = ? ORDER BY price_date DESC LIMIT ?
            """, (symbol, limit)).fetchall()

    def execute_trade(self, symbol, side, quantity, price):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        if price <= 0:
            raise ValueError("Price must be positive.")

        total = quantity * price
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        with self.connect() as con:
            cash = con.execute(
                "SELECT cash FROM account WHERE id = 1"
            ).fetchone()[0]
            held_row = con.execute(
                "SELECT quantity FROM holdings WHERE symbol = ?", (symbol,)
            ).fetchone()
            held = held_row[0] if held_row else 0

            if side == "BUY":
                if cash < total:
                    raise ValueError("Insufficient virtual cash.")
                con.execute("UPDATE account SET cash = cash - ? WHERE id = 1", (total,))
                con.execute("""
                    INSERT INTO holdings(symbol, quantity) VALUES (?, ?)
                    ON CONFLICT(symbol) DO UPDATE
                    SET quantity = quantity + excluded.quantity
                """, (symbol, quantity))
            elif side == "SELL":
                if held < quantity:
                    raise ValueError("You do not own enough shares to sell.")
                con.execute("UPDATE account SET cash = cash + ? WHERE id = 1", (total,))
                con.execute(
                    "UPDATE holdings SET quantity = quantity - ? WHERE symbol = ?",
                    (quantity, symbol)
                )
            else:
                raise ValueError("Unknown trade side.")

            con.execute("""
                INSERT INTO trades(symbol, side, quantity, price, total, traded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (symbol, side, quantity, price, total, now))

    def get_trade_history(self):
        with self.connect() as con:
            return con.execute("""
                SELECT traded_at, side, quantity, symbol, price, total
                FROM trades ORDER BY id DESC LIMIT 50
            """).fetchall()
