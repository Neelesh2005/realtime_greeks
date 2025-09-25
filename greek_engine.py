# greeks_engine.py
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from math import log, sqrt, exp, erf, pi
from datetime import datetime

# -------------------------
# Helpers
# -------------------------
def parse_iso_datetime(s):
    if s is None:
        return None
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    return datetime.fromisoformat(s)

def std_cdf(x):
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))

# -------------------------
# IV Surface
# -------------------------
def build_iv_surface_from_chain(option_chain):
    strikes, expiries, vols = [], [], []

    ts = parse_iso_datetime(option_chain.get("timestamp"))
    if ts is None:
        ts = datetime.utcnow()

    for item in option_chain.get("data", []):
        strike = float(item["strike"])
        expiry = datetime.strptime(item["expiry_date"], "%Y-%m-%d")
        days = (expiry.date() - ts.date()).days
        T = max(1e-6, days / 365.0)

        for opt_type in ("call_option", "put_option"):
            opt = item.get(opt_type)
            if opt and opt.get("implied_volatility"):
                strikes.append(strike)
                expiries.append(T)
                vols.append(float(opt["implied_volatility"]))

    if not vols:
        return lambda T, K: 0.2  # fallback

    strikes = np.array(strikes)
    expiries = np.array(expiries)
    vols = np.array(vols)

    unique_strikes = np.unique(strikes)
    unique_expiries = np.unique(expiries)

    grid = np.full((len(unique_strikes), len(unique_expiries)), np.nan)

    for i, K in enumerate(unique_strikes):
        for j, T in enumerate(unique_expiries):
            mask = (strikes == K) & (expiries == T)
            if mask.any():
                grid[i, j] = np.mean(vols[mask])

    mean_iv = np.nanmean(grid)
    grid = np.where(np.isnan(grid), mean_iv, grid)

    interp = RegularGridInterpolator(
        (unique_strikes, unique_expiries),
        grid,
        bounds_error=False,
        fill_value=mean_iv
    )

    def iv_func(T, K):
        return float(interp([[K, max(1e-6, T)]])[0])

    return iv_func

# -------------------------
# Black-Scholes
# -------------------------
def black_scholes_price_and_greeks(S, K, T, r, sigma, option_type):
    if T <= 0 or sigma <= 0:
        if option_type == "C":
            return {"price": max(0, S - K), "delta": 1.0 if S > K else 0.0,
                    "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
        else:
            return {"price": max(0, K - S), "delta": -1.0 if S < K else 0.0,
                    "gamma": 0, "theta": 0, "vega": 0, "rho": 0}

    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    n_d1 = exp(-0.5 * d1 * d1) / sqrt(2 * pi)

    if option_type == "C":
        price = S * std_cdf(d1) - K * exp(-r * T) * std_cdf(d2)
        delta = std_cdf(d1)
        theta = -(S * n_d1 * sigma) / (2 * sqrt(T)) - r * K * exp(-r * T) * std_cdf(d2)
        rho = K * T * exp(-r * T) * std_cdf(d2)
    else:
        price = K * exp(-r * T) * std_cdf(-d2) - S * std_cdf(-d1)
        delta = std_cdf(d1) - 1
        theta = -(S * n_d1 * sigma) / (2 * sqrt(T)) + r * K * exp(-r * T) * std_cdf(-d2)
        rho = -K * T * exp(-r * T) * std_cdf(-d2)

    gamma = n_d1 / (S * sigma * sqrt(T))
    vega = S * n_d1 * sqrt(T)

    return {
        "price": price,
        "delta": delta,
        "gamma": gamma,
        "theta": theta / 365,
        "vega": vega,
        "rho": rho
    }

# -------------------------
# Single contract wrapper
# -------------------------
def compute_contract_greeks(contract, iv_func, S, r, ts):
    K = float(contract["strike"])
    expiry = datetime.strptime(contract["expiry_date"], "%Y-%m-%d")
    days = (expiry.date() - ts.date()).days
    T = max(1e-6, days / 365.0)
    sigma = iv_func(T, K)
    call = black_scholes_price_and_greeks(S, K, T, r, sigma, "C")
    put = black_scholes_price_and_greeks(S, K, T, r, sigma, "P")
    return {"strike": K, "expiry_date": contract["expiry_date"], "iv": sigma, "call": call, "put": put}
