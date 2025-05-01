import logging
from datetime import datetime, timezone
import asyncio
import platform

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from cryptofeed import FeedHandler
from cryptofeed.defines import L2_BOOK
from cryptofeed.exchanges import BinanceFutures
from cryptofeed.symbols import Symbols

# Pre-seed mapping to skip exchangeInfo REST call
Symbols.set('BINANCE_FUTURES', {'BTC-USDT-PERP': 'BTCUSDT'}, {})

TOP_N = 10  # Number of levels in the depth snapshot

async def book_callback(book, ts, shared_data, lock):
    iso_ts = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

    # Extract top N bids and asks using iloc
    bids_depth = []
    for i in range(TOP_N):
        if i >= len(book.book.bids):
            break
        key = book.book.bids.iloc[-i-1]
        bids_depth.append((key, book.book.bids[key]))

    asks_depth = []
    for i in range(TOP_N):
        if i >= len(book.book.asks):
            break
        key = book.book.asks.iloc[i]
        asks_depth.append((key, book.book.asks[key]))

    # Convert to float tuples
    bids_depth = [(float(p), float(s)) for p, s in bids_depth]
    asks_depth = [(float(p), float(s)) for p, s in asks_depth]

    # Delta updates
    bids_delta = getattr(book, "delta", {}).get("bids", [])
    asks_delta = getattr(book, "delta", {}).get("asks", [])
    bids_delta = [(float(p), float(s)) for p, s in bids_delta]
    asks_delta = [(float(p), float(s)) for p, s in asks_delta]

    # Update shared data under lock
    with lock:
        shared_data['timestamp'] = iso_ts
        shared_data['depth']['bids'] = bids_depth
        shared_data['depth']['asks'] = asks_depth
        shared_data['delta']['bids'] = bids_delta
        shared_data['delta']['asks'] = asks_delta
        logging.info(f"Orderbook updated @ {iso_ts}")

def start_orderbook(shared_data, lock):
    """Run the FeedHandler in its own process with shared data."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    fh = FeedHandler()
    fh.add_feed(
        BinanceFutures(
            symbols=["BTC-USDT-PERP"],
            channels=[L2_BOOK],
            callbacks={
                L2_BOOK: lambda b, t: book_callback(b, t, shared_data, lock)
            }
        )
    )

    fh.run()