from fastapi import APIRouter, HTTPException
import logging
from datetime import datetime, timezone
import feed_handler_single

router = APIRouter()

@router.get("/candle")
def get_candle():
    logging.info("Received request for candle data")
    with feed_handler_single.lock:
        curr = feed_handler_single.current_candle.copy() if feed_handler_single.current_candle else None
        last = feed_handler_single.last_candle.copy() if feed_handler_single.last_candle else None

    def format_candle(c):
        if not c:
            return None
        dt = datetime.fromtimestamp(c["start_time"], tz=timezone.utc)
        return {
            "start_time": dt.isoformat(),
            "open": c["open"],
            "high": c["high"],
            "low": c["low"],
            "close": c["close"],
            "volume": c["volume"]
        }

    response = {
        "current": format_candle(curr),
        "last": format_candle(last)
    }
    logging.info(f"Candle data response: {response}")
    return response
