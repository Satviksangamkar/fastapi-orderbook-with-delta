from fastapi import FastAPI
import asyncio
from cryptofeed import FeedHandler
from cryptofeed.defines import L2_BOOK, BID, ASK
from cryptofeed.exchanges import BinanceFutures
from cryptofeed.symbols import Symbols

app = FastAPI()

# Predefine symbols to skip REST lookup
Symbols.set('BINANCE_FUTURES', {'BTC-USDT': 'BTCUSDT'}, {})

async def book_callback(book, ts):
    """
    Print top 5 bids and asks on every update.
    """
    depth = book.book
    bids = list(depth[BID].items())[:5]
    asks = list(depth[ASK].items())[:5]

    print(f"\n[{receipt_timestamp}] {book.exchange} {book.symbol} Depth:")
    print("BIDS:")
    for price, size in bids:
        print(f"  {price:.2f} : {size}")
    print("ASKS:")
    for price, size in asks:
        print(f"  {price:.2f} : {size}")

@app.on_event("startup")
async def start_feed():
    loop = asyncio.get_event_loop()
    fh = FeedHandler()
    fh.add_feed(
        BinanceFutures(
            symbols=['BTC-USDT'],
            channels=[L2_BOOK],
            callbacks={L2_BOOK: book_callback},
            ws_kwargs={
                "open_timeout": 20,
                "ping_interval": 20,
                "ping_timeout": 20
            }
        ),
        loop=loop
    )
    # Schedule without taking over the loop
    fh.run(start_loop=False, install_signal_handlers=False)

@app.on_event("shutdown")
async def stop_feed():
    await fh.stop_async()