"""
Company Tier Pricing Calculator

Implements tiered pricing for company tier:
- Companies with <250 employees: Flat rate ($1,000/month or $8,000/year)
- Companies with 250+ employees: Per-seat pricing ($40/seat/month or $320/seat/year)
"""

from dataclasses import dataclass
from enum import StrEnum


class CompanyBillingCycle(StrEnum):
    """Company billing cycle options"""

    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class CompanyPricing:
    """Company pricing calculation result"""

    employee_count: int
    seat_count: int
    billing_cycle: CompanyBillingCycle
    is_enterprise: bool  # True if 250+ employees
    price_per_seat: float | None  # Only for enterprise
    total_price: float
    pricing_model: str  # "flat_rate" or "per_seat"


def calculate_company_price(
    employee_count: int,
    seat_count: int,
    billing_cycle: CompanyBillingCycle = CompanyBillingCycle.MONTHLY,
) -> CompanyPricing:
    """
    Calculate company tier pricing based on employee count and seat count.

    Pricing Models:
    - Companies with <250 employees: Flat rate regardless of seats
        - Weekly: $250/week
        - Monthly: $1,000/month
        - Yearly: $8,000/year
    - Companies with 250+ employees: Per-seat pricing
        - Weekly: $6.25/seat/week
        - Monthly: $25/seat/month
        - Yearly: $200/seat/year

    Args:
        employee_count: Number of employees in the company (must be >= 1)
        seat_count: Number of seats needed (must be >= 1)
        billing_cycle: WEEKLY, MONTHLY, or YEARLY

    Returns:
        CompanyPricing: Detailed pricing calculation

    Raises:
        ValueError: If employee_count < 1 or seat_count < 1

    Examples:
        >>> # Small company (flat rate)
        >>> pricing = calculate_company_price(50, 10, CompanyBillingCycle.MONTHLY)
        >>> pricing.total_price
        1000.0
        >>> pricing.pricing_model
        'flat_rate'

        >>> # Large company (per-seat)
        >>> pricing = calculate_company_price(300, 100, CompanyBillingCycle.MONTHLY)
        >>> pricing.total_price
        2500.0
        >>> pricing.pricing_model
        'per_seat'
    """
    if employee_count < 1:
        raise ValueError(f"Employee count must be at least 1, got {employee_count}")
    if seat_count < 1:
        raise ValueError(f"Seat count must be at least 1, got {seat_count}")

    # Determine if this is an enterprise-tier company (250+ employees)
    is_enterprise = employee_count >= 250

    if is_enterprise:
        # Per-seat pricing for companies with 250+ employees
        if billing_cycle == CompanyBillingCycle.WEEKLY:
            price_per_seat = 6.25
        elif billing_cycle == CompanyBillingCycle.MONTHLY:
            price_per_seat = 25.0
        else:  # YEARLY
            price_per_seat = 200.0

        total_price = price_per_seat * seat_count
        pricing_model = "per_seat"
    else:
        # Flat rate for companies with <250 employees
        if billing_cycle == CompanyBillingCycle.WEEKLY:
            total_price = 250.0
        elif billing_cycle == CompanyBillingCycle.MONTHLY:
            total_price = 1000.0
        else:  # YEARLY
            total_price = 8000.0

        price_per_seat = None
        pricing_model = "flat_rate"

    return CompanyPricing(
        employee_count=employee_count,
        seat_count=seat_count,
        billing_cycle=billing_cycle,
        is_enterprise=is_enterprise,
        price_per_seat=price_per_seat,
        total_price=total_price,
        pricing_model=pricing_model,
    )


def format_price(price: float) -> str:
    """
    Format price as currency string.

    Args:
        price: Price in dollars

    Returns:
        str: Formatted price (e.g., "$1,000.00")

    Examples:
        >>> format_price(1000.0)
        '$1,000.00'
        >>> format_price(2500.0)
        '$2,500.00'
    """
    return f"${price:,.2f}"


# Example pricing table (for reference/documentation)
COMPANY_PRICING_TABLE = {
    "flat_rate": {
        "employee_threshold": "< 250 employees",
        "pricing": [
            {"cycle": "weekly", "price": 250, "notes": "Unlimited seats"},
            {"cycle": "monthly", "price": 1000, "notes": "Unlimited seats"},
            {"cycle": "yearly", "price": 8000, "notes": "Unlimited seats"},
        ],
    },
    "per_seat": {
        "employee_threshold": "250+ employees",
        "pricing": [
            {"cycle": "weekly", "price_per_seat": 6.25, "notes": "Cost per seat"},
            {"cycle": "monthly", "price_per_seat": 25.0, "notes": "Cost per seat"},
            {"cycle": "yearly", "price_per_seat": 200.0, "notes": "Cost per seat"},
        ],
    },
    "formula": {
        "flat_rate": "Price = Base_Price (independent of seat count)",
        "per_seat": "Price = Price_Per_Seat × seat_count",
    },
}


if __name__ == "__main__":
    # Demo/validation
    print("Company Tier Pricing Calculator")
    print("=" * 70)
    print()

    # Test cases: (employee_count, seat_count, billing_cycle)
    test_cases = [
        (10, 5, CompanyBillingCycle.MONTHLY, "Small company, few seats"),
        (50, 50, CompanyBillingCycle.MONTHLY, "Medium company, many seats"),
        (200, 100, CompanyBillingCycle.MONTHLY, "Large company below threshold"),
        (250, 50, CompanyBillingCycle.MONTHLY, "Enterprise threshold, few seats"),
        (300, 100, CompanyBillingCycle.MONTHLY, "Enterprise, 100 seats"),
        (500, 500, CompanyBillingCycle.MONTHLY, "Large enterprise, 500 seats"),
        (1000, 1000, CompanyBillingCycle.YEARLY, "Very large enterprise, yearly"),
    ]

    for employee_count, seat_count, billing_cycle, description in test_cases:
        pricing = calculate_company_price(employee_count, seat_count, billing_cycle)

        print(f"{description}")
        print(f"  Employees: {employee_count} | Seats: {seat_count}")
        print(f"  Model: {pricing.pricing_model}")
        if pricing.is_enterprise:
            print(
                f"  Price: {format_price(pricing.total_price)} "
                f"({format_price(pricing.price_per_seat)}/seat × {seat_count} seats)"
            )
        else:
            print(f"  Price: {format_price(pricing.total_price)} (flat rate)")
        print()
