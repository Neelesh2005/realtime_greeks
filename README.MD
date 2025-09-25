# Real-Time Options Greeks Engine

This project provides a real-time Greeks computation service for options using a WebSocket server–client architecture. It is designed to handle live option chain data and respond instantly with calculated Greeks.

## Project Structure

```bash
.
├── greeks_engine.py      # Functions for Black-Scholes pricing, Greeks, IV surface
├── realtime_server.py    # WebSocket server exposing Greeks calculation
├── client.py             # Client to test and stream option chain data
└── README.md             # Documentation
```
## Features
- Black–Scholes pricing for European options
- Greeks Computation: Delta (Δ), Gamma (Γ), Theta (Θ/day), Vega, and Rho
- Implied Volatility (IV) Surface construction and interpolation
- WebSocket server providing real-time request/response for Greeks calculation
- Streaming client simulating market feed with multiple option chain snapshots

## Installation

Clone the repository or copy these files into your working folder.

Create and activate a Python virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

Install dependencies:

```bash
pip install websockets numpy scipy
```

## Usage

### 1. Start the WebSocket Server
Run the real-time Greeks WebSocket server:

```bash
python realtime_server.py
```
This starts the server on `ws://127.0.0.1:8765`.

### 2. Run the Sample Client
In another terminal, start the client that streams multiple option chain snapshots spaced by 2 seconds:

```bash
python client.py
```
The client sends snapshots and receives Greeks computed by the server, printing the responses.

## Input Format (JSON Snapshot)
The server expects option chain snapshots in the following JSON format:

```json
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
}
```

### Fields Description:
- **timestamp**: ISO8601 formatted snapshot time  
- **underlying_symbol**: The underlying asset symbol (e.g., "NIFTY")  
- **underlying_price**: Current spot price of the underlying  
- **risk_free_rate**: Annualized risk-free interest rate as a decimal (e.g., 0.0545 for 5.45%)  
- **data**: List of option contracts containing:  
  - **strike**: Strike price of option  
  - **expiry_date**: Expiration date (YYYY-MM-DD)  
  - **call_option / put_option**: Each with implied volatility and last trade price  

## Output Format (JSON Response)
The server replies with Greeks calculations for each option contract:

```json
{
  "symbol": "NIFTY",
  "timestamp": "2025-08-25T16:50:00Z",
  "results": [
    {
      "strike": 24900.0,
      "expiry_date": "2025-08-28",
      "iv": 0.0901,
      "call": {
        "price": 123.79,
        "delta": 0.57,
        "gamma": 0.0003,
        "theta": -8.25,
        "vega": 45.31,
        "rho": 22.12
      },
      "put": {
        "price": 58.71,
        "delta": -0.43,
        "gamma": 0.0003,
        "theta": -4.21,
        "vega": 45.31,
        "rho": -17.65
      }
    },
    {
      "strike": 25000.0,
      "expiry_date": "2025-08-28",
      "iv": 0.078,
      "call": {
        "price": 69.74,
        "delta": 0.48,
        "gamma": 0.00029,
        "theta": -6.92,
        "vega": 42.11,
        "rho": 20.33
      },
      "put": {
        "price": 106.11,
        "delta": -0.52,
        "gamma": 0.00029,
        "theta": -5.10,
        "vega": 42.11,
        "rho": -18.91
      }
    }
  ]
}
```

### Fields Description:
- **symbol**: Underlying asset symbol  
- **timestamp**: Snapshot time of the data  
- **results**: List of option contracts with Greeks  
  - **strike, expiry_date**: Contract parameters  
  - **iv**: Interpolated implied volatility  
  - **call / put**: Each containing Black–Scholes price and Greeks (delta, gamma, theta per day, vega, rho)  





