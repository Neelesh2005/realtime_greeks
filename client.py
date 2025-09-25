import asyncio
import websockets
import json


# Replace with your actual URLs
LIVE_FEED_URI = "ws://LIVE_FEED_HOST:PORT"      # Live option chain feed
GREEKS_SERVER_URI = "ws://127.0.0.1:8765"      # Your Greeks server


async def live_feed_reader(live_feed_ws):
    """
    Async generator that yields each option chain snapshot from the live feed socket.
    """
    async for message in live_feed_ws:
        try:
            snapshot = json.loads(message)
            yield snapshot
        except json.JSONDecodeError:
            print("Received invalid JSON from live feed, skipping...")


async def run_client():
    # Connect to both sockets
    async with websockets.connect(LIVE_FEED_URI) as live_feed_ws, \
               websockets.connect(GREEKS_SERVER_URI) as greeks_ws:

        print(f"Connected to live feed: {LIVE_FEED_URI}")
        print(f"Connected to Greeks server: {GREEKS_SERVER_URI}")

        # Process each snapshot from live feed
        async for snapshot in live_feed_reader(live_feed_ws):
            print(f"\nReceived option chain snapshot @ {snapshot.get('timestamp')}")

            # Send snapshot to Greeks server
            await greeks_ws.send(json.dumps(snapshot))

            # Receive computed Greeks
            response_json = await greeks_ws.recv()
            greeks = json.loads(response_json)

            print("Greeks computed:")
            print(json.dumps(greeks, indent=2))


if __name__ == "__main__":
    asyncio.run(run_client())
