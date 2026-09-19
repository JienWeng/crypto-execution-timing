"""Restricted open-loop liquidation prototype; see analytical_note.md."""
from dataclasses import dataclass
import numpy as np


@dataclass
class ExecutionModel:
    forecast: np.ndarray
    quantity: float = 1.0
    horizon: float = 1.0
    impact: float = 0.05
    risk: float = 0.1

    def __post_init__(self):
        self.forecast = np.asarray(self.forecast, dtype=float)
        if self.forecast.ndim != 1 or len(self.forecast) < 2:
            raise ValueError('forecast must be a vector with at least two intervals')
        if not np.all(np.isfinite(self.forecast)):
            raise ValueError('forecast must be finite')
        params = [self.quantity, self.horizon, self.impact, self.risk]
        if not np.all(np.isfinite(params)) or min(params[:3]) <= 0 or self.risk < 0:
            raise ValueError('positive Q/T/impact and nonnegative risk required')
        self.n = len(self.forecast)
        self.dt = self.horizon / self.n
        self.L = np.tril(np.ones((self.n, self.n)))
        self.H = (2*self.impact/self.dt*np.eye(self.n)
                  + 2*self.risk*self.dt*self.L.T@self.L)
        self.b = 2*self.risk*self.dt*self.quantity*self.L.T@np.ones(self.n)
        self.h = -self.dt*self.L.T@self.forecast
        one = np.ones(self.n)
        hinv_one = np.linalg.solve(self.H, one)
        hinv_b = np.linalg.solve(self.H, self.b)
        self.u0 = hinv_b + hinv_one*(self.quantity-one@hinv_b)/(one@hinv_one)
        hinv_h = np.linalg.solve(self.H, self.h)
        self.direction = hinv_h-hinv_one*(one@hinv_h)/(one@hinv_one)
        self.K = float(self.direction@self.H@self.direction)
        if np.min(self.u0) <= 0:
            raise ValueError('this implementation requires an interior baseline')

    def exposure_limit(self, cap=1.0):
        if not np.isfinite(cap) or cap < 0:
            raise ValueError('cap must be finite and nonnegative')
        negative = self.direction < 0
        feasible = (float(np.min(-self.u0[negative]/self.direction[negative]))
                    if negative.any() else float('inf'))
        return min(cap, feasible)

    def schedule(self, amplitude, cap=1.0):
        if not np.isfinite(amplitude) or not 0 <= amplitude <= self.exposure_limit(cap)+1e-12:
            raise ValueError('amplitude outside permitted feasible ray')
        return self.u0+amplitude*self.direction

    def objective(self, trades, beta):
        trades = np.asarray(trades)
        inventory = self.quantity-self.L@trades
        return float(self.impact/self.dt*(trades@trades)
                     + self.risk*self.dt*(inventory@inventory)
                     - beta*self.dt*(self.forecast@inventory))

    def safe_amplitude(self, lower, upper, cap=1.0):
        if not np.isfinite([lower, upper]).all() or lower > upper:
            raise ValueError('finite, ordered uncertainty interval required')
        return min(self.exposure_limit(cap), max(0.0, lower))
