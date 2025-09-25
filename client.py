# client.py
import asyncio
import websockets
import json
from datetime import datetime
import random

USE_LIVE_FEED = False   # Set True if you have a live feed
SERVER_URI = "ws://127.0.0.1:8765"


STATIC_SNAPSHOTS = [
    {
        "timestamp": "2025-08-25T16:50:00Z",
        "underlying_symbol": "NIFTY",
        "underlying_price": 24967.75,
        "risk_free_rate": 0.0545,
        "data": [
            {
                "strike": 24900.0,
                "expiry_date": "2025-08-28",
                "call_option": {"implied_volatility": 0.0901, "ltp": 123.15},
                "put_option": {"implied_volatility": 0.0573, "ltp": 58.65}
            },
            {
                "strike": 25000.0,
                "expiry_date": "2025-08-28",
                "call_option": {"implied_volatility": 0.078, "ltp": 69.75},
                "put_option": {"implied_volatility": 0.0873, "ltp": 106.05}
            }
        ]
    },
    {
        "timestamp": "2025-08-25T16:51:00Z",
        "underlying_symbol": "NIFTY",
        "underlying_price": 24980.50,
        "risk_free_rate": 0.0545,
        "data": [
            {
                "strike": 24950.0,
                "expiry_date": "2025-08-28",
                "call_option": {"implied_volatility": 0.085, "ltp": 101.40},
                "put_option": {"implied_volatility": 0.061, "ltp": 76.25}
            },
            {
                "strike": 25100.0,
                "expiry_date": "2025-09-04",
                "call_option": {"implied_volatility": 0.092, "ltp": 44.30},
                "put_option": {"implied_volatility": 0.094, "ltp": 132.10}
            }
        ]
    }
]


async def live_feed_generator():
    """Simulate a live feed by generating random snapshots every 2 seconds"""
    underlying_price = 25000.0
    while True:
        timestamp = datetime.utcnow().isoformat() + "Z"
        snapshot = {
            "timestamp": timestamp,
            "underlying_symbol": "NIFTY",
            "underlying_price": underlying_price + random.uniform(-20, 20),
            "risk_free_rate": 0.0545,
            "data": [
                {
                    "strike": 24900.0,
                    "expiry_date": "2025-08-28",
                    "call_option": {"implied_volatility": 0.09 + random.uniform(-0.01, 0.01), "ltp": 120 + random.uniform(-5, 5)},
                    "put_option": {"implied_volatility": 0.06 + random.uniform(-0.01, 0.01), "ltp": 60 + random.uniform(-5, 5)}
                },
                {
                    "strike": 25000.0,
                    "expiry_date": "2025-08-28",
                    "call_option": {"implied_volatility": 0.08 + random.uniform(-0.01, 0.01), "ltp": 70 + random.uniform(-5, 5)},
                    "put_option": {"implied_volatility": 0.085 + random.uniform(-0.01, 0.01), "ltp": 105 + random.uniform(-5, 5)}
                }
            ]
        }
        yield snapshot
        await asyncio.sleep(2)


async def run_client():
    async with websockets.connect(SERVER_URI) as ws:
        print("Connected to server:", SERVER_URI)

        if USE_LIVE_FEED:
            print("Using live feed...")
            async for snapshot in live_feed_generator():
                await ws.send(json.dumps(snapshot))
                response = await ws.recv()
                print(f"Received Greeks @ {snapshot['timestamp']}:")
                print(json.dumps(json.loads(response), indent=2))
        else:
            print("Using static snapshots for testing...")
            for snapshot in STATIC_SNAPSHOTS:
                await ws.send(json.dumps(snapshot))
                response = await ws.recv()
                print(f"Received Greeks @ {snapshot['timestamp']}:")
                print(json.dumps(json.loads(response), indent=2))
                await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_client())
