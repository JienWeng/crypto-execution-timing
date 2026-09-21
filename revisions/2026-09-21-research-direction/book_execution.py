"""Observed-depth sale accounting; replay results are hypothetical, not live fills.

Continuous quantities, no passive queue model, no endogenous market response.
The planner uses independent future snapshots. Replay can apply a conservative
observed-replenishment ledger as a separate sensitivity assumption.
"""
from dataclasses import dataclass
import numpy as np


def _levels(prices, sizes):
    p, s = np.asarray(prices, float), np.asarray(sizes, float)
    if (p.ndim != 1 or len(p) == 0 or p.shape != s.shape or
            not np.isfinite(p).all() or not np.isfinite(s).all() or
            np.any(p <= 0) or np.any(s < 0) or np.any(np.diff(p) >= 0)):
        raise ValueError('positive strictly descending bids and nonnegative sizes required')
    return p, s


@dataclass(frozen=True)
class Book:
    timestamp: int  # seconds since epoch / local availability time in adapters
    bids: np.ndarray
    sizes: np.ndarray
    ask: float

    def __post_init__(self):
        p, s = _levels(self.bids, self.sizes)
        if not np.isfinite(self.ask) or self.ask <= p[0] or s[0] <= 0 or not np.isfinite(self.timestamp):
            raise ValueError('finite timestamp and uncrossed positive spread required')
        object.__setattr__(self, 'bids', p.copy())
        object.__setattr__(self, 'sizes', s.copy())

    @property
    def mid(self):
        return (self.ask + self.bids[0]) / 2


def walk(prices, sizes, quantity):
    p, s = _levels(prices, sizes)
    if not np.isfinite(quantity) or quantity < 0:
        raise ValueError('nonnegative finite quantity required')
    fills = np.minimum(s, np.maximum(0., quantity - np.r_[0., np.cumsum(s)[:-1]]))
    return float(p @ fills), float(fills.sum())


def allocate(prices, sizes, quantity, child_cap):
    """Exact separable concave proceeds maximization with equal-price tie sharing.

    Truncate each time's book at the common child cap; rank all remaining
    marginal bid segments. Price ordering ensures prefix feasibility. Tied
    marginal prices are shared equally across times subject to segment capacity.
    """
    prices, sizes = np.asarray(prices, float), np.asarray(sizes, float)
    if prices.ndim != 2 or prices.shape != sizes.shape:
        raise ValueError('matching time by level arrays required')
    if not np.isfinite([quantity, child_cap]).all() or min(quantity, child_cap) <= 0:
        raise ValueError('positive finite quantity/cap required')
    segments = []
    for t, (p, s) in enumerate(zip(prices, sizes)):
        _levels(p, s)
        cap = child_cap
        for price, size in zip(p, s):
            take = min(cap, size)
            if take > 0:
                segments.append((float(price), t, take))
            cap -= take
            if cap <= 0:
                break
    if sum(x[2] for x in segments) < quantity - 1e-10 * quantity:
        raise ValueError('insufficient forecast depth; no extrapolation permitted')
    segments.sort(reverse=True)
    q = np.zeros(len(prices))
    remaining = quantity
    i = 0
    while remaining > 1e-12 * quantity and i < len(segments):
        j = i + 1
        while j < len(segments) and segments[j][0] == segments[i][0]:
            j += 1
        group = segments[i:j]
        capacities = np.array([x[2] for x in group])
        take = min(remaining, float(capacities.sum()))
        # Water fill ties; equal volumes, rather than favoring earlier indices.
        if take >= capacities.sum():
            portions = capacities
        elif len(group) == 1:
            portions = np.array([take])
        else:
            lo, hi = 0., float(capacities.max())
            for _ in range(55):
                mid = (lo + hi) / 2
                if np.minimum(capacities, mid).sum() < take:
                    lo = mid
                else:
                    hi = mid
            portions = np.minimum(capacities, hi)
        for (_, t, _), amount in zip(group, portions):
            q[t] += amount
        remaining -= float(portions.sum())
        i = j
    return q


class DepletionLedger:
    """Retain consumed depth at each price until that price leaves the snapshot.

    Snapshot data do not identify true replenishment. This is a sensitivity
    convention, not an inferred order-by-order reconstruction.
    """
    def __init__(self):
        self.previous, self.debt = {}, {}
        self.prices, self.available = np.empty(0), np.empty(0)

    def update(self, prices, sizes):
        p, s = _levels(prices, sizes)
        current = dict(zip(p, s))
        self.debt = {price: self.debt.get(price, 0.) for price in current}
        self.previous = current
        self.prices = p.copy()
        self.available = np.array([max(0., size-self.debt[price]) for price, size in current.items()])

    def sell(self, quantity):
        if not len(self.prices):
            raise ValueError('update ledger before selling')
        revenue, filled = walk(self.prices, self.available, quantity)
        left = quantity
        for i, price in enumerate(self.prices):
            amount = min(left, self.available[i])
            self.available[i] -= amount
            self.debt[price] += amount
            left -= amount
        return revenue, filled


def forecast_books(current, price_bps, log_spread_ratio, log_depth_ratio,
                   use_price, use_liquidity):
    """Transform the common observed book using only caller-supplied predictions.

    Price shifts use arrival mid; liquidity changes half-spread and horizontal
    depth scale, preserving the current shape beyond the best bid. This is a
    restricted forecast family, not a claim of complete future-book prediction.
    """
    p, sp, d = map(lambda x: np.asarray(x, float),
                   (price_bps, log_spread_ratio, log_depth_ratio))
    if p.ndim != 1 or p.shape != sp.shape or p.shape != d.shape or not np.isfinite([p, sp, d]).all():
        raise ValueError('matching finite one-dimensional predictions required')
    mid = current.mid + (current.mid * p / 1e4 if use_price else np.zeros(len(p)))
    halfspread = (current.ask-current.bids[0])/2
    spread = halfspread * (np.exp(sp) if use_liquidity else np.ones(len(p)))
    depth = np.exp(d) if use_liquidity else np.ones(len(p))
    prices = mid[:, None] - spread[:, None] - (current.bids[0]-current.bids)[None, :]
    sizes = depth[:, None] * current.sizes[None, :]
    for x, y in zip(prices, sizes):
        _levels(x, y)
    return prices, sizes


def replay(arrival_mid, books, schedule, fee_bps=0., depletion=True, child_cap=None):
    """Sell planned quantities; carry shortages forward, report any unfinished sale.

    Each snapshot is used once. A carried shortage respects child_cap when set.
    No invented terminal fill or mark is substituted for unsupported depth.
    """
    schedule = np.asarray(schedule, float)
    if (len(books) != len(schedule) or not len(books) or np.any(schedule < 0) or
            not np.isfinite(schedule).all() or not np.isfinite([arrival_mid, fee_bps]).all() or
            arrival_mid <= 0 or fee_bps < 0 or fee_bps >= 1e4):
        raise ValueError('valid matching schedule/books, reference and fees required')
    if any(b.timestamp <= a.timestamp for a, b in zip(books, books[1:])):
        raise ValueError('strictly increasing snapshot times required')
    if child_cap is not None and (not np.isfinite(child_cap) or child_cap <= 0):
        raise ValueError('positive finite child cap required')
    ledger = DepletionLedger()
    revenue = filled = timing = spread = depth = backlog = max_backlog = 0.
    child_fills = []
    for b, planned in zip(books, schedule):
        request = planned+backlog
        if child_cap is not None:
            request = min(request, child_cap)
        if depletion:
            ledger.update(b.bids, b.sizes)
            proceeds, done = ledger.sell(request)
        else:
            proceeds, done = walk(b.bids, b.sizes, request)
        child_fills.append(done)
        backlog = max(0., planned+backlog-done)
        max_backlog = max(backlog, max_backlog)
        revenue += proceeds
        filled += done
        timing += done * (b.mid-arrival_mid)
        spread += done * (b.mid-b.bids[0])
        depth += done*b.bids[0]-proceeds
    fee = revenue*fee_bps/1e4
    quantity = float(schedule.sum())
    complete = backlog <= 1e-10*max(quantity, 1e-12)
    shortfall = filled*arrival_mid-revenue+fee
    return dict(quantity=quantity, filled=filled, unfilled=backlog,
                max_backlog=max_backlog, proceeds=revenue, fee_dollars=fee,
                child_fills=child_fills,
                timing_dollars=timing, timing_shortfall_dollars=-timing,
                spread_dollars=spread, depth_dollars=depth,
                book_cost_dollars=spread+depth,
                filled_quantity_shortfall_dollars=shortfall,
                shortfall_dollars=shortfall if complete else None,
                shortfall_bps=1e4*shortfall/(quantity*arrival_mid) if complete and quantity > 0 else None)
