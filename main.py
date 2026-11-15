
from database import Database
from market_data import MarketDataProvider

STARTING_CASH = 10_000.00


def money(value):
    return f"${value:,.2f}"


# ---------------- MARKET ----------------

def show_market(db):
    rows = db.get_latest_prices()

    if not rows:
        print("\nNo market data available. Sync first.")
        return

    print("\n--- Market ---")
    print(f"{'Symbol':<10} {'Price':>12} {'Date':>15}")

    for symbol, price, date in rows:
        print(f"{symbol:<10} {money(price):>12} {date:>15}")


def sync_market(db, provider):
    watchlist = db.get_watchlist()

    if not watchlist:
        print("Your watchlist is empty. Add some tickers first.")
        return

    print("\nFetching latest available daily prices...")

    for symbol in watchlist:
        try:
            rows = provider.fetch_history(symbol, period="5d")

            if rows:
                db.save_price_history(symbol, rows)

                date, close = rows[-1]

                print(
                    f"{symbol}: {money(close)} | {date}"
                )
            else:
                print(f"{symbol}: No data returned.")

        except Exception as error:
            print(f"{symbol}: Update failed ({error})")

    print("\nMarket synchronization complete.")


# ---------------- WATCHLIST ----------------

def add_ticker(db):
    symbol = input("\nEnter ticker symbol: ").strip().upper()

    if not symbol:
        print("Invalid ticker.")
        return

    # Verify that the symbol has data before adding it.
    try:
        provider = MarketDataProvider()
        rows = provider.fetch_history(symbol, period="5d")

        if not rows:
            print("No market data found. Check the ticker symbol.")
            return

        if db.add_ticker(symbol):
            db.save_price_history(symbol, rows)
            print(f"{symbol} successfully added to your watchlist!")
        else:
            print(f"{symbol} is already in your watchlist.")

    except Exception as error:
        print(f"Could not verify ticker: {error}")


def remove_ticker(db):
    symbol = input("\nEnter ticker to remove: ").strip().upper()

    if db.remove_ticker(symbol):
        print(f"{symbol} removed from your watchlist.")
    else:
        print(f"{symbol} was not found in your watchlist.")


def show_watchlist(db):
    tickers = db.get_watchlist()

    print("\n--- Your Watchlist ---")

    if not tickers:
        print("Your watchlist is empty.")
        return

    for index, symbol in enumerate(tickers, start=1):
        price = db.get_latest_price(symbol)

        if price is not None:
            print(f"{index}. {symbol} - {money(price)}")
        else:
            print(f"{index}. {symbol} - Not synced yet")


# ---------------- PORTFOLIO ----------------

def show_portfolio(db):
    cash = db.get_cash_balance()
    holdings = db.get_holdings()

    total_equity = cash

    print("\n--- Portfolio ---")
    print(f"Cash balance: {money(cash)}")

    if not holdings:
        print("No stock holdings yet.")

    for symbol, quantity in holdings:
        price = db.get_latest_price(symbol)

        if price is None:
            print(f"{symbol}: {quantity} shares | Price unavailable")
            continue

        value = quantity * price
        total_equity += value

        print(
            f"{symbol}: {quantity} shares | "
            f"Price: {money(price)} | Value: {money(value)}"
        )

    print(f"Estimated net worth: {money(total_equity)}")


# ---------------- TRADING ----------------

def trade(db, side):
    symbol = input("Stock symbol: ").strip().upper()

    price = db.get_latest_price(symbol)

    if price is None:
        print("No saved price found. Sync market data first.")
        return

    try:
        quantity = int(input("Number of shares: "))

        if quantity <= 0:
            print("Quantity must be greater than zero.")
            return

        db.execute_trade(symbol, side, quantity, price)

        action = "bought" if side == "BUY" else "sold"

        print(
            f"Successfully {action} {quantity} "
            f"{symbol} at {money(price)} per share."
        )

    except ValueError as error:
        print(f"Trade failed: {error}")


# ---------------- HISTORY ----------------

def show_history(db):
    symbol = input("Enter ticker: ").strip().upper()

    rows = db.get_price_history(symbol, limit=20)

    if not rows:
        print("No saved history found.")
        return

    print(f"\n--- {symbol} Price History ---")

    for date, close in rows:
        print(f"{date}: {money(close)}")


def show_trade_history(db):
    rows = db.get_trade_history()

    print("\n--- Trade History ---")

    if not rows:
        print("No trades recorded.")
        return

    for date, side, quantity, symbol, price, total in rows:
        print(
            f"{date} | {side} {quantity} {symbol} | "
            f"{money(price)} each | Total: {money(total)}"
        )


# ---------------- MAIN ----------------

def main():
    db = Database(
        "market.db",
        starting_cash=STARTING_CASH
    )

    provider = MarketDataProvider()

    print("\n=== Virtual Stock Market Simulator ===")
    print("Real historical market data | Virtual trading | SQLite")

    while True:
        print("""
1. View market
2. Sync market data
3. Buy shares
4. Sell shares
5. View portfolio
6. View saved price history
7. View trade history
8. Add ticker
9. Remove ticker
10. View watchlist
11. Exit
""")

        choice = input("Choice: ").strip()

        if choice == "1":
            show_market(db)

        elif choice == "2":
            sync_market(db, provider)

        elif choice == "3":
            trade(db, "BUY")

        elif choice == "4":
            trade(db, "SELL")

        elif choice == "5":
            show_portfolio(db)

        elif choice == "6":
            show_history(db)

        elif choice == "7":
            show_trade_history(db)

        elif choice == "8":
            add_ticker(db)

        elif choice == "9":
            remove_ticker(db)

        elif choice == "10":
            show_watchlist(db)

        elif choice == "11":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Select 1-11.")


if __name__ == "__main__":
    main()
