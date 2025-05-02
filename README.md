Key Features & Components

FastAPI–based HTTP Server

ASGI app exposing /api/orderbook/... routes

Root health-check and favicon stub

Local URL: http://localhost:8000/

Cryptofeed Integration

WebSocket L2_BOOK feed from Binance Futures

In-memory order-book state via orderbook_callback

Eight Analytics Endpoints

Depth View – ±X% of best bid/ask
http://localhost:8000/api/orderbook/depth?symbol=BTC-USDT&percent=2

Delta – bid volume − ask volume
http://localhost:8000/api/orderbook/delta?symbol=BTC-USDT&percent=2

Ratio – (bid−ask)/(bid+ask)
http://localhost:8000/api/orderbook/ratio?symbol=BTC-USDT&percent=2

Total Liquidity – sum of bid+ask volumes
http://localhost:8000/api/orderbook/total?symbol=BTC-USDT&percent=2

Mid Price & Spread – (bid+ask)/2 ＆ ask−bid
http://localhost:8000/api/orderbook/midspread?symbol=BTC-USDT

Order Imbalance – normalized bid/ask skew
http://localhost:8000/api/orderbook/imbalance?symbol=BTC-USDT&percent=2

Order Walls – price levels with ≥ threshold size
http://localhost:8000/api/orderbook/walls?symbol=BTC-USDT&threshold=10

Cumulative Depth – running sum at each level
http://localhost:8000/api/orderbook/cumulative?symbol=BTC-USDT&percent=2
