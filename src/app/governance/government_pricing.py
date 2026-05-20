"""
Government Tier Progressive Pricing Calculator

Pricing model:
  Seats 1-100  → progressive tiered pricing (15% increase per 25-seat band)
  Seats 101+   → per-seat pricing

Tiered band structure:
  Tier 0: seats   1-25   multiplier 1.00  (no increase)
  Tier 1: seats  26-50   multiplier 1.15  (+15%)
  Tier 2: seats  51-75   multiplier 1.30  (+30%)
  Tier 3: seats  76-100  multiplier 1.45  (+45%)
  … continues beyond 100 but seats 101+ switch to per-seat model.

Base rates (tiered):
  Monthly: $2,500  ×  multiplier
  Yearly:  $10,000 ×  multiplier  (= 4× monthly)

Per-seat rates (101+):
  Monthly: $50 / seat
  Yearly:  $400 / seat  (= 8× monthly)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GovernmentBillingCycle(Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


_TIERED_THRESHOLD = 100           # seats ≤ this use tiered model
_SEATS_PER_TIER = 25
_TIER_MULTIPLIER_STEP = 0.15

_BASE_RATES: dict[GovernmentBillingCycle, float] = {
    GovernmentBillingCycle.MONTHLY: 2_500.0,
    GovernmentBillingCycle.YEARLY: 10_000.0,
}

_PER_SEAT_RATES: dict[GovernmentBillingCycle, float] = {
    GovernmentBillingCycle.MONTHLY: 50.0,
    GovernmentBillingCycle.YEARLY: 400.0,
}


@dataclass(frozen=True)
class GovernmentPricing:
    seat_count: int
    billing_cycle: GovernmentBillingCycle
    pricing_model: str                          # "tiered" or "per_seat"
    total_price: float
    base_price: Optional[float]                 # tiered base before multiplier
    tier_multiplier: Optional[float]            # None for per_seat
    tier_number: Optional[int]                  # None for per_seat
    price_increase_percentage: Optional[float]  # None for per_seat
    price_per_seat: Optional[float]             # None for tiered


def calculate_government_tier_multiplier(
    seats: int,
) -> tuple[float, int, float]:
    """Return (multiplier, tier_number, price_increase_percentage) for seat count."""
    if seats < 1:
        raise ValueError("Seat count must be at least 1")
    tier = (seats - 1) // _SEATS_PER_TIER
    multiplier = round(1.0 + _TIER_MULTIPLIER_STEP * tier, 10)
    increase = float(tier * 15)
    return multiplier, tier, increase


def calculate_government_price(
    seat_count: int,
    billing_cycle: GovernmentBillingCycle,
) -> GovernmentPricing:
    """Return a GovernmentPricing for the given seat count and billing cycle."""
    if seat_count < 1:
        raise ValueError("Seat count must be at least 1")

    if seat_count <= _TIERED_THRESHOLD:
        multiplier, tier, increase = calculate_government_tier_multiplier(seat_count)
        base = _BASE_RATES[billing_cycle]
        total = round(base * multiplier, 2)
        return GovernmentPricing(
            seat_count=seat_count,
            billing_cycle=billing_cycle,
            pricing_model="tiered",
            total_price=total,
            base_price=base,
            tier_multiplier=multiplier,
            tier_number=tier,
            price_increase_percentage=increase,
            price_per_seat=None,
        )
    else:
        rate = _PER_SEAT_RATES[billing_cycle]
        total = round(rate * seat_count, 2)
        return GovernmentPricing(
            seat_count=seat_count,
            billing_cycle=billing_cycle,
            pricing_model="per_seat",
            total_price=total,
            base_price=None,
            tier_multiplier=None,
            tier_number=None,
            price_increase_percentage=None,
            price_per_seat=rate,
        )


def get_pricing_tier_range(tier: int) -> tuple[int, int]:
    """Return (min_seats, max_seats) for the given tier number."""
    min_seats = tier * _SEATS_PER_TIER + 1
    max_seats = (tier + 1) * _SEATS_PER_TIER
    return min_seats, max_seats


def format_price(amount: float) -> str:
    """Format a price as a USD string with comma separators."""
    return f"${amount:,.2f}"
