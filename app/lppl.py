from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np

# LPPL model: P(t) = A + B*(tc - t)^m + C*(tc - t)^m * cos(omega * ln(tc - t) + phi)
# We fit log price y = ln(P) to reduce heteroscedasticity in bubbles.

@dataclass
class LPPLParams:
    A: float
    B: float
    C: float
    m: float
    omega: float
    phi: float
    tc: float
    t0: float
    t1: float
    rmse: float


def _lppl_function(t: np.ndarray, p: LPPLParams) -> np.ndarray:
    dt = np.clip(p.tc - t, 1e-9, None)
    return p.A + p.B * dt ** p.m + p.C * dt ** p.m * np.cos(p.omega * np.log(dt) + p.phi)


def fit_lppl(
    times: np.ndarray,
    prices: np.ndarray,
    start_index: Optional[int] = None,
    min_window: int = 60,
    max_window: Optional[int] = None,
    tc_max_expand: float = 0.2,
    omega_bounds: Tuple[float, float] = (6.0, 13.0),
    m_bounds: Tuple[float, float] = (0.1, 0.9),
    random_restarts: int = 8,
    seed: int = 42,
) -> Optional[LPPLParams]:
    """
    Simple heuristic LPPL fit with random restarts using gradient-free search (Nelder-Mead) over (A,B,C,m,omega,phi,tc).
    - times: unix seconds
    - prices: positive prices
    - start_index: if provided, use window [start_index : end]; else auto-search for best window.
    Returns best LPPLParams or None if fails.
    """
    rng = np.random.default_rng(seed)
    n = len(times)
    if max_window is None:
        max_window = n
    if n < min_window:
        return None

    def choose_window():
        if start_index is not None:
            return max(0, min(start_index, n - min_window)), n
        # heuristic: try last 180..n points
        w = max(min_window, min(n, 180))
        return n - w, n

    i0, i1 = choose_window()
    t = times[i0:i1].astype(float)
    y = np.log(np.maximum(prices[i0:i1], 1e-9))
    if len(t) < min_window:
        return None

    t_min, t_max = t[0], t[-1]

    def loss(theta):
        A, B, C, m, omega, phi, tc = theta
        if not (m_bounds[0] <= m <= m_bounds[1]):
            return 1e9
        if not (omega_bounds[0] <= omega <= omega_bounds[1]):
            return 1e9
        if not (tc > t_max and tc < t_max * (1.0 + tc_max_expand)):
            return 1e9
        dt = np.clip(tc - t, 1e-9, None)
        yhat = A + B * dt ** m + C * dt ** m * np.cos(omega * np.log(dt) + phi)
        return float(np.sqrt(np.mean((yhat - y) ** 2)))

    best = None
    def nm_optimize(theta0):
        # Basic Nelder-Mead
        from math import isfinite
        dim = len(theta0)
        simplex = [theta0]
        scale = np.array([1.0, 1.0, 1.0, 0.05, 0.5, 0.5, (t_max - t_min) * 0.1])
        for i in range(dim):
            v = theta0.copy()
            v[i] += scale[i]
            simplex.append(v)
        values = [loss(s) for s in simplex]
        for _ in range(200):
            # order by value
            idx = np.argsort(values)
            simplex = [simplex[i] for i in idx]
            values = [values[i] for i in idx]
            best_theta, best_val = simplex[0], values[0]
            worst_theta, worst_val = simplex[-1], values[-1]
            centroid = np.mean(simplex[:-1], axis=0)
            # reflection
            xr = centroid + (centroid - worst_theta)
            fr = loss(xr)
            if fr < values[0]:
                # expansion
                xe = centroid + 2 * (centroid - worst_theta)
                fe = loss(xe)
                if fe < fr:
                    simplex[-1], values[-1] = xe, fe
                else:
                    simplex[-1], values[-1] = xr, fr
            elif fr < values[-2]:
                simplex[-1], values[-1] = xr, fr
            else:
                # contraction
                xc = centroid + 0.5 * (worst_theta - centroid)
                fc = loss(xc)
                if fc < worst_val:
                    simplex[-1], values[-1] = xc, fc
                else:
                    # shrink
                    for i in range(1, len(simplex)):
                        simplex[i] = simplex[0] + 0.5 * (simplex[i] - simplex[0])
                        values[i] = loss(simplex[i])
        return simplex[0], values[0]

    # initial guesses
    A0 = float(np.mean(y))
    B0 = -1.0
    C0 = 0.1
    m0 = 0.5
    omega0 = 8.0
    phi0 = 0.0
    tc0 = t_max * 1.05

    candidates = []
    for _ in range(max(1, random_restarts)):
        theta0 = np.array([
            A0 + rng.normal(scale=0.1),
            B0 + rng.normal(scale=0.5),
            C0 + rng.normal(scale=0.2),
            np.clip(m0 + rng.normal(scale=0.1), *m_bounds),
            np.clip(omega0 + rng.normal(scale=1.5), *omega_bounds),
            phi0 + rng.normal(scale=1.0),
            t_max * (1.02 + abs(rng.normal(scale=0.05)))
        ], dtype=float)
        th, val = nm_optimize(theta0)
        candidates.append((th, val))

    if not candidates:
        return None
    th, val = min(candidates, key=lambda x: x[1])
    A, B, C, m, omega, phi, tc = map(float, th)
    params = LPPLParams(A=A, B=B, C=C, m=m, omega=omega, phi=phi, tc=tc, t0=float(t_min), t1=float(t_max), rmse=float(val))
    return params
