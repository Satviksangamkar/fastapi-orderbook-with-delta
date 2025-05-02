from fastapi import FastAPI, Query
from feedhandler import get_orderbook_data, run_feed
import asyncio, platform, sys

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.stdout.reconfigure(encoding='utf-8')
app = FastAPI()

@app.get("/")
def root():
    return {"message": "FastAPI Order Book Feed is running"}

@app.get("/api/orderbook")
def get_full_orderbook(symbol: str = Query(...)):
    data = get_orderbook_data(symbol)
    if not data:
        return {"error": "No data available for symbol"}
    return {
        "bids": data["bids"],
        "asks": data["asks"]
    }

@app.get("/api/orderbook/depth")
def get_orderbook_depth(symbol: str = Query(...), depth: int = Query(10, ge=1, le=100)):
    data = get_orderbook_data(symbol, depth)
    if not data:
        return {"error": "No data available for symbol"}
    bid_total = sum(level["amount"] for level in data["bids"])
    ask_total = sum(level["amount"] for level in data["asks"])
    return {
        "bids": data["bids"],
        "asks": data["asks"],
        "delta": round(bid_total - ask_total, 8)
    }

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_feed())
