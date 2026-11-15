from datetime import datetime, timezone
from database import Database
from market_data import MarketDataProvider

STARTING_CASH = 10_000.00
WATCHLIST = ["AAPL", "NVDA", "GOOG", "MSFT", "AMZN", "META", "NFLX", "TSLA", "ORCL"]


def money(value):
    return f"${value:,.2f}"


def show_market(db):
    rows = db.get_latest_prices()
    if not rows:
        print("\nNo market data saved yet. Choose 'Sync market data' first.")
        return

    print("\n--- Market (latest data saved locally) ---")
    print(f"{'Symbol':<8} {'Price':>12} {'As of':>22}")
    for symbol, price, timestamp in rows:
        print(f"{symbol:<8} {money(price):>12} {timestamp:>22}")


def show_portfolio(db):
    cash = db.get_cash_balance()
    holdings = db.get_holdings()
    total = cash

    print("\n--- Portfolio ---")
    print(f"Cash balance: {money(cash)}")
    if not holdings:
        print("No stock holdings yet.")

    for symbol, quantity in holdings:
        latest = db.get_latest_price(symbol)
        if latest is None:
            print(f"{symbol}: {quantity} shares (price unavailable)")
            continue
        value = quantity * latest
        total += value
        print(f"{symbol}: {quantity} shares | Price: {money(latest)} | Value: {money(value)}")

    print(f"Estimated net worth: {money(total)}")


def trade(db, side):
    symbol = input("Stock symbol: ").strip().upper()
    if not symbol:
        print("Please enter a symbol.")
        return

    price = db.get_latest_price(symbol)
    if price is None:
        print("No saved price for that symbol. Sync market data first.")
        return

    try:
        quantity = int(input("Whole shares: "))
    except ValueError:
        print("Quantity must be a whole number.")
        return

    if quantity <= 0:
        print("Quantity must be greater than zero.")
        return

    try:
        db.execute_trade(symbol, side, quantity, price)
        action = "bought" if side == "BUY" else "sold"
        print(f"Successfully {action} {quantity} {symbol} at {money(price)} per share.")
    except ValueError as error:
        print(error)


def sync_market(db, provider):
    print("\nFetching latest available daily market data...")
    for symbol in WATCHLIST:
        try:
            rows = provider.fetch_history(symbol, period="5d")
            db.save_price_history(symbol, rows)
            if rows:
                latest_date, close = rows[-1]
                print(f"{symbol}: saved {latest_date} close at {money(close)}")
            else:
                print(f"{symbol}: provider returned no data")
        except Exception as error:
            print(f"{symbol}: could not update ({error})")

    print("\nSync finished. Data is stored in market.db.")


def show_history(db):
    symbol = input("Symbol to inspect: ").strip().upper()
    rows = db.get_price_history(symbol, limit=20)
    if not rows:
        print("No saved history for that symbol.")
        return

    print(f"\n--- {symbol} recent saved closing prices ---")
    for date, close in rows:
        print(f"{date}: {money(close)}")


def main():
    db = Database("market.db", starting_cash=STARTING_CASH)
    provider = MarketDataProvider()

    print("\n=== Virtual Stock Market Simulator ===")
    print("Educational simulator: trades use the latest price saved in your local database.")
    while True:
        print("""
1. View market
2. Sync market data
3. Buy shares
4. Sell shares
5. View portfolio
6. View saved price history
7. View trade history
8. Exit
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
            for row in db.get_trade_history():
                print(row)
        elif choice == "8":
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Select a number from 1 to 8.")


if __name__ == "__main__":
    main()
