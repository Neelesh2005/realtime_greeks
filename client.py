# client.py
import asyncio
import websockets
import json
import datetime

# Multiple snapshots to simulate streaming feed
SNAPSHOTS = [
    {
        "timestamp": "2025-08-25T16:50:00Z",
        "underlying_symbol": "NIFTY",
        "underlying_price": 24967.75,
        "risk_free_rate": 0.0545,
        "data": [
            {
                "strike": 24900.00,
                "expiry_date": "2025-08-28",
                "call_option": {"implied_volatility": 0.0901, "ltp": 123.15},
                "put_option": {"implied_volatility": 0.0573, "ltp": 58.65}
            },
            {
                "strike": 25000.00,
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
                "strike": 24950.00,
                "expiry_date": "2025-08-28",
                "call_option": {"implied_volatility": 0.085, "ltp": 101.40},
                "put_option": {"implied_volatility": 0.061, "ltp": 76.25}
            },
            {
                "strike": 25100.00,
                "expiry_date": "2025-09-04",
                "call_option": {"implied_volatility": 0.092, "ltp": 44.30},
                "put_option": {"implied_volatility": 0.094, "ltp": 132.10}
            }
        ]
    },
    {
        "timestamp": "2025-08-25T16:52:00Z",
        "underlying_symbol": "NIFTY",
        "underlying_price": 25005.10,
        "risk_free_rate": 0.0545,
        "data": [
            {
                "strike": 25000.00,
                "expiry_date": "2025-08-28",
                "call_option": {"implied_volatility": 0.080, "ltp": 77.80},
                "put_option": {"implied_volatility": 0.085, "ltp": 98.90}
            },
            {
                "strike": 25200.00,
                "expiry_date": "2025-09-11",
                "call_option": {"implied_volatility": 0.102, "ltp": 28.15},
                "put_option": {"implied_volatility": 0.108, "ltp": 161.75}
            }
        ]
    }
]

async def run_client():
    uri = "ws://127.0.0.1:8765"
    async with websockets.connect(uri) as ws:
        print("Connected to server:", uri)

        for snap in SNAPSHOTS:
            # send snapshot
            await ws.send(json.dumps(snap))
            print(f"Sent snapshot @ {snap['timestamp']} (price={snap['underlying_price']})")

            # receive and print response
            response = await ws.recv()
            data = json.loads(response)
            print("Received Greeks:")
            print(json.dumps(data, indent=2))

            # simulate real-time gap
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_client())
