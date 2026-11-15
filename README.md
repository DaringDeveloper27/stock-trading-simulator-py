# Virtual Stock Market Simulator (Python + SQLite)

A beginner-friendly translation and extension of the original C++ stock simulator.

## Features

- Fetches actual historical daily closing prices through `yfinance`.
- Saves market prices locally in SQLite (`market.db`).
- Keeps a virtual cash balance, share holdings, and trade history.
- Supports buying and selling virtual shares.
- Displays portfolio value using the latest price saved in the database.
- Keeps the most recent daily price history for each symbol.

## Requirements

- Python 3.10 or newer
- Internet connection for market-data synchronization

## Setup on macOS

Open Terminal in this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

## How to use

1. Choose **2. Sync market data** to download the latest available daily prices.
2. Choose **1. View market** to see saved prices.
3. Choose **3. Buy shares** or **4. Sell shares**.
4. Choose **5. View portfolio** to see cash, holdings, and estimated net worth.
5. Choose **6. View saved price history** or **7. View trade history**.

The database is created automatically as `market.db` the first time the program runs.

## Important data limitations

- `yfinance` is an unofficial interface to Yahoo Finance, not an official exchange feed.
- This project fetches **daily historical data**, not guaranteed real-time quotes.
- The newest available daily close may be delayed or may be from the previous trading session.
- Data availability, symbol coverage, and Yahoo Finance access can change.
- Trades are simulated at the latest price stored in your local database. They are not real orders and do not represent executable market prices.
- This is an educational project, not financial advice.

## Project structure

```text
stock_market_simulator/
├── main.py          # Menu, market display, and virtual trading
├── database.py      # SQLite database and portfolio transactions
├── market_data.py   # External market-data fetching
├── requirements.txt
└── README.md
```

## Good next upgrades

- Add a graphical dashboard with Streamlit.
- Add OHLCV charts and percentage returns.
- Add fractional shares and order types.
- Add a second provider with a documented quote API for explicitly real-time or delayed quotes.
- Add a backtesting engine and compare simulated outcomes with historical data.
