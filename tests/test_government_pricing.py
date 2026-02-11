"""
Unit tests for Government Tier Progressive Pricing Calculator

Tests the progressive seat-based pricing implementation:
- 15% price increase for every 25 seats
- Base pricing validation
- Tier calculation accuracy
- Edge cases and error handling
"""

import pytest

from src.app.governance.government_pricing import (
    GovernmentBillingCycle,
    calculate_government_price,
    calculate_government_tier_multiplier,
    format_price,
    get_pricing_tier_range,
)


class TestGovernmentTierMultiplier:
    """Test tier multiplier calculation"""

    def test_tier_0_single_seat(self):
        """Test tier 0 with 1 seat (minimum)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(1)
        assert multiplier == 1.0
        assert tier == 0
        assert increase == 0.0

    def test_tier_0_boundary(self):
        """Test tier 0 boundary (25 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(25)
        assert multiplier == 1.0
        assert tier == 0
        assert increase == 0.0

    def test_tier_1_start(self):
        """Test tier 1 start (26 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(26)
        assert multiplier == 1.15
        assert tier == 1
        assert increase == 15.0

    def test_tier_1_boundary(self):
        """Test tier 1 boundary (50 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(50)
        assert multiplier == 1.15
        assert tier == 1
        assert increase == 15.0

    def test_tier_2_start(self):
        """Test tier 2 start (51 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(51)
        assert multiplier == 1.30
        assert tier == 2
        assert increase == 30.0

    def test_tier_3_boundary(self):
        """Test tier 3 (100 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(100)
        assert multiplier == 1.45
        assert tier == 3
        assert increase == 45.0

    def test_tier_4(self):
        """Test tier 4 (125 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(125)
        assert multiplier == 1.60
        assert tier == 4
        assert increase == 60.0

    def test_tier_5(self):
        """Test tier 5 (150 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(150)
        assert multiplier == 1.75
        assert tier == 5
        assert increase == 75.0

    def test_tier_10_large_deployment(self):
        """Test large deployment (250 seats)"""
        multiplier, tier, increase = calculate_government_tier_multiplier(250)
        assert multiplier == 2.50
        assert tier == 9
        assert increase == 135.0

    def test_invalid_seat_count_zero(self):
        """Test error handling for zero seats"""
        with pytest.raises(ValueError, match="Seat count must be at least 1"):
            calculate_government_tier_multiplier(0)

    def test_invalid_seat_count_negative(self):
        """Test error handling for negative seats"""
        with pytest.raises(ValueError, match="Seat count must be at least 1"):
            calculate_government_tier_multiplier(-10)


class TestGovernmentPricing:
    """Test government pricing calculation"""

    def test_monthly_base_tier(self):
        """Test monthly pricing for base tier (1-25 seats)"""
        pricing = calculate_government_price(10, GovernmentBillingCycle.MONTHLY)
        assert pricing.seat_count == 10
        assert pricing.billing_cycle == GovernmentBillingCycle.MONTHLY
        assert pricing.base_price == 2500.0
        assert pricing.tier_multiplier == 1.0
        assert pricing.total_price == 2500.0
        assert pricing.tier_number == 0
        assert pricing.price_increase_percentage == 0.0

    def test_yearly_base_tier(self):
        """Test yearly pricing for base tier (1-25 seats)"""
        pricing = calculate_government_price(25, GovernmentBillingCycle.YEARLY)
        assert pricing.seat_count == 25
        assert pricing.billing_cycle == GovernmentBillingCycle.YEARLY
        assert pricing.base_price == 10000.0
        assert pricing.tier_multiplier == 1.0
        assert pricing.total_price == 10000.0
        assert pricing.tier_number == 0
        assert pricing.price_increase_percentage == 0.0

    def test_monthly_tier_1(self):
        """Test monthly pricing for tier 1 (26-50 seats)"""
        pricing = calculate_government_price(30, GovernmentBillingCycle.MONTHLY)
        assert pricing.seat_count == 30
        assert pricing.total_price == 2875.0  # 2500 * 1.15
        assert pricing.tier_number == 1
        assert pricing.price_increase_percentage == 15.0

    def test_yearly_tier_1(self):
        """Test yearly pricing for tier 1 (26-50 seats)"""
        pricing = calculate_government_price(50, GovernmentBillingCycle.YEARLY)
        assert pricing.seat_count == 50
        assert pricing.total_price == 11500.0  # 10000 * 1.15
        assert pricing.tier_number == 1
        assert pricing.price_increase_percentage == 15.0

    def test_monthly_tier_2(self):
        """Test monthly pricing for tier 2 (51-75 seats)"""
        pricing = calculate_government_price(60, GovernmentBillingCycle.MONTHLY)
        assert pricing.seat_count == 60
        assert pricing.total_price == 3250.0  # 2500 * 1.30
        assert pricing.tier_number == 2
        assert pricing.price_increase_percentage == 30.0

    def test_yearly_tier_2(self):
        """Test yearly pricing for tier 2 (51-75 seats)"""
        pricing = calculate_government_price(75, GovernmentBillingCycle.YEARLY)
        assert pricing.seat_count == 75
        assert pricing.total_price == 13000.0  # 10000 * 1.30
        assert pricing.tier_number == 2
        assert pricing.price_increase_percentage == 30.0

    def test_monthly_tier_3(self):
        """Test monthly pricing for tier 3 (76-100 seats)"""
        pricing = calculate_government_price(100, GovernmentBillingCycle.MONTHLY)
        assert pricing.seat_count == 100
        assert pricing.total_price == 3625.0  # 2500 * 1.45
        assert pricing.tier_number == 3
        assert pricing.price_increase_percentage == 45.0

    def test_yearly_tier_4(self):
        """Test yearly pricing for tier 4 (101-125 seats)"""
        pricing = calculate_government_price(125, GovernmentBillingCycle.YEARLY)
        assert pricing.seat_count == 125
        assert pricing.total_price == 16000.0  # 10000 * 1.60
        assert pricing.tier_number == 4
        assert pricing.price_increase_percentage == 60.0

    def test_invalid_seat_count(self):
        """Test error handling for invalid seat count"""
        with pytest.raises(ValueError):
            calculate_government_price(0, GovernmentBillingCycle.MONTHLY)

    def test_pricing_consistency(self):
        """Test that yearly pricing is 4x monthly pricing"""
        for seats in [10, 25, 50, 75, 100, 125]:
            monthly = calculate_government_price(seats, GovernmentBillingCycle.MONTHLY)
            yearly = calculate_government_price(seats, GovernmentBillingCycle.YEARLY)
            # Yearly should be 4x monthly
            assert yearly.total_price == pytest.approx(monthly.total_price * 4.0)


class TestPricingTierRange:
    """Test pricing tier range helper"""

    def test_tier_0_range(self):
        """Test tier 0 range"""
        min_seats, max_seats = get_pricing_tier_range(0)
        assert min_seats == 1
        assert max_seats == 25

    def test_tier_1_range(self):
        """Test tier 1 range"""
        min_seats, max_seats = get_pricing_tier_range(1)
        assert min_seats == 26
        assert max_seats == 50

    def test_tier_2_range(self):
        """Test tier 2 range"""
        min_seats, max_seats = get_pricing_tier_range(2)
        assert min_seats == 51
        assert max_seats == 75

    def test_tier_5_range(self):
        """Test tier 5 range"""
        min_seats, max_seats = get_pricing_tier_range(5)
        assert min_seats == 126
        assert max_seats == 150


class TestPriceFormatting:
    """Test price formatting"""

    def test_format_base_price(self):
        """Test formatting base price"""
        assert format_price(2500.0) == "$2,500.00"

    def test_format_tier_1_price(self):
        """Test formatting tier 1 price"""
        assert format_price(2875.0) == "$2,875.00"

    def test_format_large_price(self):
        """Test formatting large price"""
        assert format_price(16000.0) == "$16,000.00"

    def test_format_decimal_price(self):
        """Test formatting price with cents"""
        assert format_price(2500.50) == "$2,500.50"


class TestProgressivePricingFormula:
    """Test the progressive pricing formula accuracy"""

    def test_formula_at_boundaries(self):
        """Test formula at tier boundaries"""
        # Formula: Price = Base × (1 + 0.15 × floor((seats - 1) / 25))
        test_cases = [
            (1, 2500.0),  # Tier 0: 2500 × 1.0
            (25, 2500.0),  # Tier 0: 2500 × 1.0
            (26, 2875.0),  # Tier 1: 2500 × 1.15
            (50, 2875.0),  # Tier 1: 2500 × 1.15
            (51, 3250.0),  # Tier 2: 2500 × 1.30
            (75, 3250.0),  # Tier 2: 2500 × 1.30
            (76, 3625.0),  # Tier 3: 2500 × 1.45
            (100, 3625.0),  # Tier 3: 2500 × 1.45
            (101, 4000.0),  # Tier 4: 2500 × 1.60
        ]

        for seats, expected_price in test_cases:
            pricing = calculate_government_price(seats, GovernmentBillingCycle.MONTHLY)
            assert (
                pricing.total_price == expected_price
            ), f"Failed for {seats} seats: got {pricing.total_price}, expected {expected_price}"

    def test_15_percent_increase_per_tier(self):
        """Test that each tier increases by exactly 15%"""
        base_monthly = 2500.0

        for tier in range(10):  # Test first 10 tiers
            seats = (tier * 25) + 1  # First seat of each tier
            pricing = calculate_government_price(seats, GovernmentBillingCycle.MONTHLY)

            expected_multiplier = 1.0 + (0.15 * tier)
            expected_price = base_monthly * expected_multiplier

            assert pricing.tier_multiplier == expected_multiplier
            assert pricing.total_price == expected_price
            assert pricing.price_increase_percentage == tier * 15.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
