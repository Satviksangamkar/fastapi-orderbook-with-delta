from fastapi import FastAPI, HTTPException
import logging
import multiprocessing
from multiprocessing import Manager

import feed_handler_orderbook

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

@app.on_event("startup")
def startup_event():
    manager = Manager()
    shared_data = manager.dict({
        'timestamp': None,
        'depth': manager.dict({'bids': manager.list(), 'asks': manager.list()}),
        'delta': manager.dict({'bids': manager.list(), 'asks': manager.list()})
    })
    lock = manager.Lock()

    # Start FeedHandler in a separate process
    process = multiprocessing.Process(
        target=feed_handler_orderbook.start_orderbook,
        args=(shared_data, lock),
        daemon=True
    )
    process.start()
    app.state.shared_data = shared_data
    app.state.lock = lock
    logging.info("Orderbook feed handler started in its own process")

@app.get("/orderbook")
def get_orderbook(depth_levels: int = 10):
    shared_data = app.state.shared_data
    lock = app.state.lock

    with lock:
        data = {
            'timestamp': shared_data['timestamp'],
            'depth': {
                'bids': list(shared_data['depth']['bids'])[:depth_levels],
                'asks': list(shared_data['depth']['asks'])[:depth_levels]
            },
            'delta': {
                'bids': list(shared_data['delta']['bids']),
                'asks': list(shared_data['delta']['asks'])
            }
        }

    if data['timestamp'] is None:
        raise HTTPException(503, "Orderbook data not yet available")
    return data