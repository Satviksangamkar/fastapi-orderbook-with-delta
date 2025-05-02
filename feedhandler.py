from typing import Dict, List
from datetime import datetime
from cryptofeed import FeedHandler
from cryptofeed.defines import L2_BOOK
from cryptofeed.exchanges import Binance

orderbook_data: Dict[str, Dict] = {}

async def orderbook_callback(book, receipt_timestamp):
    orderbook_data[book.symbol.upper()] = {
        "symbol": book.symbol.upper(),
        "bids": [{"price": price, "amount": book.book.bids[price]} for price in sorted(book.book.bids.keys(), reverse=True)],
        "asks": [{"price": price, "amount": book.book.asks[price]} for price in sorted(book.book.asks.keys())]
    }

def get_orderbook_data(symbol: str, depth: int = None):
    book = orderbook_data.get(symbol.upper())
    if not book:
        return None
    return {
        "symbol": book["symbol"],
        "bids": book["bids"][:depth] if depth else book["bids"],
        "asks": book["asks"][:depth] if depth else book["asks"]
    }

async def run_feed():
    f = FeedHandler()
    f.add_feed(Binance(
        symbols=['BTC-USDT'],
        channels=[L2_BOOK],
        max_depth=1000,
        callbacks={L2_BOOK: orderbook_callback}
    ))
    f.run(start_loop=False)
