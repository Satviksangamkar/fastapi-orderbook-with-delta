# main.py

import asyncio
import logging
from datetime import datetime
from decimal import Decimal
from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient

from feedhandler import get_orderbook_data, run_feed
from schemas import (
    DepthResponse, DeltaResponse, RatioResponse,
    TotalLiquidityResponse, MidSpreadResponse,
    ImbalanceResponse, WallsResponse, CumulativeDepthResponse
)

# --- MongoDB setup ---
MONGO_URI = "mongodb+srv://satvik:Stankarrk@satvik.kimjuo9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(MONGO_URI)
db = client["cryptofeed_db"]

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_feed())

@app.get("/")
def root():
    return {"message": "Order Book API running. Use /api/orderbook/* endpoints."}

@app.get("/favicon.ico")
def favicon():
    return {}

def _to_decimal(f):
    return Decimal(str(f))

def _store(collection: str, doc: dict):
    db[collection].insert_one(doc)

@app.get("/api/orderbook/depth", response_model=DepthResponse)
def depth(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "bids": fb,
            "asks": fa
        }
        _store("depth_view", doc)
        return doc
    except Exception as e:
        logging.exception("Depth endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/delta", response_model=DeltaResponse)
def delta(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        bid_total = sum(_to_decimal(b["amount"]) for b in fb)
        ask_total = sum(_to_decimal(a["amount"]) for a in fa)
        delta_val = bid_total - ask_total
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "delta": float(delta_val)
        }
        _store("delta", doc)
        return doc
    except Exception as e:
        logging.exception("Delta endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/ratio", response_model=RatioResponse)
def ratio(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        bid_total = sum(_to_decimal(b["amount"]) for b in fb)
        ask_total = sum(_to_decimal(a["amount"]) for a in fa)
        total = bid_total + ask_total
        ratio_val = (bid_total - ask_total) / total if total > 0 else Decimal("0")
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "ratio": float(ratio_val)
        }
        _store("ratio", doc)
        return doc
    except Exception as e:
        logging.exception("Ratio endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/total", response_model=TotalLiquidityResponse)
def liquidity(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        total = sum(_to_decimal(b["amount"]) for b in fb) + sum(_to_decimal(a["amount"]) for a in fa)
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "totalLiquidity": float(total)
        }
        _store("liquidity_total", doc)
        return doc
    except Exception as e:
        logging.exception("Total endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/midspread", response_model=MidSpreadResponse)
def midspread(symbol: str = Query(...)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        mid = (best_bid + best_ask) / Decimal("2")
        spread = best_ask - best_bid
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "midPrice": float(mid),
            "spread": float(spread)
        }
        _store("mid_spread", doc)
        return doc
    except Exception as e:
        logging.exception("MidSpread endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/imbalance", response_model=ImbalanceResponse)
def imbalance(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [b for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [a for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        bid_total = sum(_to_decimal(b["amount"]) for b in fb)
        ask_total = sum(_to_decimal(a["amount"]) for a in fa)
        imb = (bid_total - ask_total) / (bid_total + ask_total) if (bid_total + ask_total) > 0 else Decimal("0")
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "imbalance": float(imb)
        }
        _store("imbalance", doc)
        return doc
    except Exception as e:
        logging.exception("Imbalance endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/walls", response_model=WallsResponse)
def walls(symbol: str = Query(...), threshold: float = Query(10.0, gt=0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        thresh = _to_decimal(threshold)
        bids = [b for b in data["bids"] if _to_decimal(b["amount"]) >= thresh]
        asks = [a for a in data["asks"] if _to_decimal(a["amount"]) >= thresh]
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "threshold": float(thresh),
            "walls": {"bids": bids, "asks": asks}
        }
        _store("order_walls", doc)
        return doc
    except Exception as e:
        logging.exception("Walls endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orderbook/cumulative", response_model=CumulativeDepthResponse)
def cumulative(symbol: str = Query(...), percent: float = Query(1.0, ge=0.1, le=10.0)):
    data = get_orderbook_data(symbol)
    if data is None:
        raise HTTPException(status_code=404, detail="No data available for symbol")
    try:
        pct = _to_decimal(percent)
        bids, asks = data["bids"], data["asks"]
        best_bid = _to_decimal(max(b["price"] for b in bids))
        best_ask = _to_decimal(min(a["price"] for a in asks))
        bid_thresh = best_bid * (Decimal("1") - pct/Decimal("100"))
        ask_thresh = best_ask * (Decimal("1") + pct/Decimal("100"))
        fb = [(b["price"], _to_decimal(b["amount"])) for b in bids if _to_decimal(b["price"]) >= bid_thresh]
        fa = [(a["price"], _to_decimal(a["amount"])) for a in asks if _to_decimal(a["price"]) <= ask_thresh]
        cum_bids, cum_asks = [], []
        running = Decimal("0")
        for price, amt in fb:
            running += amt
            cum_bids.append({"price": price, "cumulative": float(running)})
        running = Decimal("0")
        for price, amt in fa:
            running += amt
            cum_asks.append({"price": price, "cumulative": float(running)})
        doc = {
            "timestamp": datetime.utcnow(),
            "symbol": symbol.upper(),
            "percent": float(pct),
            "cumulativeBids": cum_bids,
            "cumulativeAsks": cum_asks
        }
        _store("cumulative_depth", doc)
        return doc
    except Exception as e:
        logging.exception("Cumulative endpoint failed")
        raise HTTPException(status_code=500, detail=str(e))
