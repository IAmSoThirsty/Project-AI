"""
Government Tier Progressive Pricing Calculator

Implements tiered pricing for government tier:
- Seats 1-100: Progressive pricing (15% increase for every 25 seats)
- Seats 101+: Per-seat pricing ($50/seat/month or $400/seat/year)
- Base pricing: $2,500/month or $10,000/year (1-25 seats)
"""

from dataclasses import dataclass
from enum import StrEnum


class GovernmentBillingCycle(StrEnum):
    """Government billing cycle options"""

    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class GovernmentPricing:
    """Government pricing calculation result"""

    seat_count: int
    billing_cycle: GovernmentBillingCycle
    base_price: float
    tier_multiplier: float | None  # None for per-seat pricing (101+ seats)
    total_price: float
    tier_number: int | None  # None for per-seat pricing (101+ seats)
    price_increase_percentage: float
    pricing_model: str  # "tiered" or "per_seat"
    price_per_seat: float | None  # Only for per-seat pricing (101+ seats)


def calculate_government_tier_multiplier(seat_count: int) -> tuple[float, int, float]:
    """
    Calculate the pricing tier multiplier based on seat count.

    Progressive pricing: 15% increase for every 25 seats.

    Args:
        seat_count: Number of seats (must be >= 1)

    Returns:
        tuple: (multiplier, tier_number, increase_percentage)
            - multiplier: Price multiplier (1.0, 1.15, 1.30, etc.)
            - tier_number: Which 25-seat tier (0-based)
            - increase_percentage: Total percentage increase from base

    Examples:
        >>> calculate_government_tier_multiplier(10)
        (1.0, 0, 0.0)
        >>> calculate_government_tier_multiplier(30)
        (1.15, 1, 15.0)
        >>> calculate_government_tier_multiplier(60)
        (1.30, 2, 30.0)
    """
    if seat_count < 1:
        raise ValueError(f"Seat count must be at least 1, got {seat_count}")

    # Calculate which tier: 0-indexed (0 = 1-25, 1 = 26-50, 2 = 51-75, etc.)
    tier_number = (seat_count - 1) // 25

    # Calculate multiplier: 1.0 + (0.15 * tier_number)
    multiplier = 1.0 + (0.15 * tier_number)

    # Calculate percentage increase
    increase_percentage = tier_number * 15.0

    return multiplier, tier_number, increase_percentage


def calculate_government_price(
    seat_count: int,
    billing_cycle: GovernmentBillingCycle = GovernmentBillingCycle.MONTHLY,
) -> GovernmentPricing:
    """
    Calculate government tier pricing for given seat count and billing cycle.

    Pricing Models:
    - Seats 1-100: Progressive pricing (15% increase for every 25 seats)
        - Base pricing (1-25 seats):
            - Monthly: $2,500/month
            - Yearly: $10,000/year
        - Progressive increase: +15% for every 25 seats
    - Seats 101+: Per-seat pricing
        - Monthly: $50/seat/month
        - Yearly: $400/seat/year

    Args:
        seat_count: Number of seats (must be >= 1)
        billing_cycle: MONTHLY or YEARLY

    Returns:
        GovernmentPricing: Detailed pricing calculation

    Raises:
        ValueError: If seat_count < 1

    Examples:
        >>> # Progressive pricing (1-100 seats)
        >>> pricing = calculate_government_price(25, GovernmentBillingCycle.MONTHLY)
        >>> pricing.total_price
        2500.0
        >>> pricing.pricing_model
        'tiered'

        >>> pricing = calculate_government_price(50, GovernmentBillingCycle.MONTHLY)
        >>> pricing.total_price
        2875.0

        >>> # Per-seat pricing (101+ seats)
        >>> pricing = calculate_government_price(150, GovernmentBillingCycle.MONTHLY)
        >>> pricing.total_price
        7500.0
        >>> pricing.pricing_model
        'per_seat'
    """
    if seat_count < 1:
        raise ValueError(f"Seat count must be at least 1, got {seat_count}")

    # Base pricing
    base_price_monthly = 2500.0
    base_price_yearly = 10000.0

    # Select base price based on billing cycle
    if billing_cycle == GovernmentBillingCycle.MONTHLY:
        base_price = base_price_monthly
    else:  # YEARLY
        base_price = base_price_yearly

    # Determine pricing model based on seat count
    if seat_count <= 100:
        # Progressive pricing for seats 1-100
        multiplier, tier_number, increase_percentage = (
            calculate_government_tier_multiplier(seat_count)
        )
        total_price = base_price * multiplier
        pricing_model = "tiered"
        price_per_seat = None
    else:
        # Per-seat pricing for seats 101+
        if billing_cycle == GovernmentBillingCycle.MONTHLY:
            price_per_seat = 50.0
        else:  # YEARLY
            price_per_seat = 400.0

        total_price = price_per_seat * seat_count
        multiplier = None
        tier_number = None
        increase_percentage = 0.0
        pricing_model = "per_seat"

    return GovernmentPricing(
        seat_count=seat_count,
        billing_cycle=billing_cycle,
        base_price=base_price,
        tier_multiplier=multiplier,
        total_price=total_price,
        tier_number=tier_number,
        price_increase_percentage=increase_percentage,
        pricing_model=pricing_model,
        price_per_seat=price_per_seat,
    )


def get_pricing_tier_range(tier_number: int) -> tuple[int, int]:
    """
    Get the seat range for a given pricing tier.

    Args:
        tier_number: 0-based tier number (0 = 1-25, 1 = 26-50, etc.)

    Returns:
        tuple: (min_seats, max_seats) for the tier

    Examples:
        >>> get_pricing_tier_range(0)
        (1, 25)
        >>> get_pricing_tier_range(1)
        (26, 50)
        >>> get_pricing_tier_range(2)
        (51, 75)
    """
    min_seats = (tier_number * 25) + 1
    max_seats = (tier_number + 1) * 25
    return min_seats, max_seats


def format_price(price: float) -> str:
    """
    Format price as currency string.

    Args:
        price: Price in dollars

    Returns:
        str: Formatted price (e.g., "$2,500.00")

    Examples:
        >>> format_price(2500.0)
        '$2,500.00'
        >>> format_price(2875.0)
        '$2,875.00'
    """
    return f"${price:,.2f}"


# Example pricing table (for reference/documentation)
GOVERNMENT_PRICING_TABLE = {
    "tiered_pricing": {
        "range": "1-100 seats",
        "tiers": [
            {
                "range": "1-25",
                "monthly": 2500,
                "yearly": 10000,
                "increase": "Base (100%)",
            },
            {
                "range": "26-50",
                "monthly": 2875,
                "yearly": 11500,
                "increase": "+15% (115%)",
            },
            {
                "range": "51-75",
                "monthly": 3250,
                "yearly": 13000,
                "increase": "+30% (130%)",
            },
            {
                "range": "76-100",
                "monthly": 3625,
                "yearly": 14500,
                "increase": "+45% (145%)",
            },
        ],
        "formula": "Price = Base_Price × (1 + 0.15 × floor((seats - 1) / 25))",
    },
    "per_seat_pricing": {
        "range": "101+ seats",
        "monthly_per_seat": 50,
        "yearly_per_seat": 400,
        "formula": "Price = Price_Per_Seat × seat_count",
    },
}


if __name__ == "__main__":
    # Demo/validation
    print("Government Tier Pricing Calculator")
    print("=" * 70)
    print()

    test_cases = [10, 25, 26, 50, 51, 75, 76, 100, 101, 125, 150, 200, 500]

    for seats in test_cases:
        monthly = calculate_government_price(seats, GovernmentBillingCycle.MONTHLY)
        yearly = calculate_government_price(seats, GovernmentBillingCycle.YEARLY)

        print(f"Seats: {seats:3d} | Model: {monthly.pricing_model}")
        if monthly.pricing_model == "tiered":
            print(
                f"  Monthly: {format_price(monthly.total_price)} "
                f"(Tier {monthly.tier_number}, +{monthly.price_increase_percentage:.0f}%)"
            )
            print(
                f"  Yearly:  {format_price(yearly.total_price)} "
                f"(Tier {yearly.tier_number}, +{yearly.price_increase_percentage:.0f}%)"
            )
        else:  # per_seat
            print(
                f"  Monthly: {format_price(monthly.total_price)} "
                f"({format_price(monthly.price_per_seat)}/seat × {seats} seats)"
            )
            print(
                f"  Yearly:  {format_price(yearly.total_price)} "
                f"({format_price(yearly.price_per_seat)}/seat × {seats} seats)"
            )
        print()
