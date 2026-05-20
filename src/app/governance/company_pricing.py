"""
Company Tier Pricing Calculator

Pricing model:
  < 250 employees  → flat rate  (independent of seat count)
  ≥ 250 employees  → per-seat   (enterprise tier)

Rates:
  Billing    Flat rate    Per seat
  Weekly     $250         $6.25
  Monthly    $1,000       $25.00
  Yearly     $8,000       $200.00

Yearly is priced at 8× monthly (≈38.5% discount vs 52 × weekly).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CompanyBillingCycle(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


_FLAT_RATES: dict[CompanyBillingCycle, float] = {
    CompanyBillingCycle.WEEKLY: 250.0,
    CompanyBillingCycle.MONTHLY: 1_000.0,
    CompanyBillingCycle.YEARLY: 8_000.0,
}

_PER_SEAT_RATES: dict[CompanyBillingCycle, float] = {
    CompanyBillingCycle.WEEKLY: 6.25,
    CompanyBillingCycle.MONTHLY: 25.0,
    CompanyBillingCycle.YEARLY: 200.0,
}

_ENTERPRISE_THRESHOLD = 250


@dataclass(frozen=True)
class CompanyPricing:
    employee_count: int
    seat_count: int
    billing_cycle: CompanyBillingCycle
    is_enterprise: bool
    pricing_model: str          # "flat_rate" or "per_seat"
    total_price: float
    price_per_seat: Optional[float]


def calculate_company_price(
    employee_count: int,
    seat_count: int,
    billing_cycle: CompanyBillingCycle,
) -> CompanyPricing:
    """Return a CompanyPricing for the given parameters."""
    if employee_count < 1:
        raise ValueError("Employee count must be at least 1")
    if seat_count < 1:
        raise ValueError("Seat count must be at least 1")

    is_enterprise = employee_count >= _ENTERPRISE_THRESHOLD

    if is_enterprise:
        rate = _PER_SEAT_RATES[billing_cycle]
        return CompanyPricing(
            employee_count=employee_count,
            seat_count=seat_count,
            billing_cycle=billing_cycle,
            is_enterprise=True,
            pricing_model="per_seat",
            total_price=round(rate * seat_count, 2),
            price_per_seat=rate,
        )
    else:
        return CompanyPricing(
            employee_count=employee_count,
            seat_count=seat_count,
            billing_cycle=billing_cycle,
            is_enterprise=False,
            pricing_model="flat_rate",
            total_price=_FLAT_RATES[billing_cycle],
            price_per_seat=None,
        )


def format_price(amount: float) -> str:
    """Format a price as a USD string with comma separators."""
    return f"${amount:,.2f}"
