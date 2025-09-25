# realtime_server.py
import asyncio
import json
import logging
from datetime import datetime

import websockets
from concurrent.futures import ThreadPoolExecutor

from greek_engine import parse_iso_datetime, build_iv_surface_from_chain, compute_contract_greeks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("realtime-greeks")

class RealTimeGreeksServer:
    def __init__(self, host="127.0.0.1", port=8765, max_workers=4):
        self.host = host
        self.port = port
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.iv_cache = {}

    async def handler(self, websocket):
        async for msg in websocket:
            try:
                snapshot = json.loads(msg)
                response = await self.process_snapshot(snapshot)
            except Exception as e:
                logger.exception("Error processing snapshot")
                response = {"error": str(e)}
            await websocket.send(json.dumps(response))

    async def process_snapshot(self, snapshot):
        ts = parse_iso_datetime(snapshot.get("timestamp")) or datetime.utcnow()
        key = (snapshot.get("underlying_symbol"), snapshot.get("timestamp"))

        if key not in self.iv_cache:
            iv_func = await asyncio.get_event_loop().run_in_executor(
                self.executor, lambda: build_iv_surface_from_chain(snapshot)
            )
            self.iv_cache[key] = iv_func
        else:
            iv_func = self.iv_cache[key]

        S = snapshot["underlying_price"]
        r = snapshot.get("risk_free_rate", 0.0)

        tasks = [
            asyncio.get_event_loop().run_in_executor(
                self.executor, lambda c=c: compute_contract_greeks(c, iv_func, S, r, ts)
            )
            for c in snapshot.get("data", [])
        ]
        results = await asyncio.gather(*tasks)

        return {
            "symbol": snapshot["underlying_symbol"],
            "timestamp": snapshot["timestamp"],
            "results": results
        }

    async def start(self):
        logger.info(f"Server listening ws://{self.host}:{self.port}")
        async with websockets.serve(self.handler, self.host, self.port):
            await asyncio.Future()

if __name__ == "__main__":
    server = RealTimeGreeksServer()
    asyncio.run(server.start())
