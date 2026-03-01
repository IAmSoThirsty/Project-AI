"""
Unit tests for Company Tier Pricing Calculator

Tests the tiered pricing implementation:
- Companies with <250 employees: Flat rate
- Companies with 250+ employees: Per-seat pricing
"""

import pytest

from src.app.governance.company_pricing import (
    CompanyBillingCycle,
    calculate_company_price,
    format_price,
)


class TestCompanyFlatRatePricing:
    """Test flat rate pricing for companies with <250 employees"""

    def test_small_company_weekly(self):
        """Test weekly pricing for small company"""
        pricing = calculate_company_price(10, 5, CompanyBillingCycle.WEEKLY)
        assert pricing.employee_count == 10
        assert pricing.seat_count == 5
        assert pricing.billing_cycle == CompanyBillingCycle.WEEKLY
        assert pricing.is_enterprise is False
        assert pricing.pricing_model == "flat_rate"
        assert pricing.total_price == 250.0
        assert pricing.price_per_seat is None

    def test_small_company_monthly(self):
        """Test monthly pricing for small company"""
        pricing = calculate_company_price(50, 10, CompanyBillingCycle.MONTHLY)
        assert pricing.employee_count == 50
        assert pricing.seat_count == 10
        assert pricing.total_price == 1000.0
        assert pricing.pricing_model == "flat_rate"
        assert pricing.is_enterprise is False

    def test_small_company_yearly(self):
        """Test yearly pricing for small company"""
        pricing = calculate_company_price(100, 50, CompanyBillingCycle.YEARLY)
        assert pricing.employee_count == 100
        assert pricing.seat_count == 50
        assert pricing.total_price == 8000.0
        assert pricing.pricing_model == "flat_rate"
        assert pricing.is_enterprise is False

    def test_flat_rate_independent_of_seats(self):
        """Test that flat rate is independent of seat count"""
        # All should have the same price regardless of seats
        pricing_5_seats = calculate_company_price(100, 5, CompanyBillingCycle.MONTHLY)
        pricing_50_seats = calculate_company_price(100, 50, CompanyBillingCycle.MONTHLY)
        pricing_100_seats = calculate_company_price(
            100, 100, CompanyBillingCycle.MONTHLY
        )

        assert pricing_5_seats.total_price == 1000.0
        assert pricing_50_seats.total_price == 1000.0
        assert pricing_100_seats.total_price == 1000.0

    def test_boundary_just_below_enterprise(self):
        """Test pricing for company with 249 employees (just below threshold)"""
        pricing = calculate_company_price(249, 200, CompanyBillingCycle.MONTHLY)
        assert pricing.is_enterprise is False
        assert pricing.pricing_model == "flat_rate"
        assert pricing.total_price == 1000.0


class TestCompanyPerSeatPricing:
    """Test per-seat pricing for companies with 250+ employees"""

    def test_enterprise_threshold_weekly(self):
        """Test weekly pricing at enterprise threshold (250 employees)"""
        pricing = calculate_company_price(250, 50, CompanyBillingCycle.WEEKLY)
        assert pricing.employee_count == 250
        assert pricing.seat_count == 50
        assert pricing.is_enterprise is True
        assert pricing.pricing_model == "per_seat"
        assert pricing.price_per_seat == 6.25
        assert pricing.total_price == 312.50  # 50 * 6.25

    def test_enterprise_threshold_monthly(self):
        """Test monthly pricing at enterprise threshold (250 employees)"""
        pricing = calculate_company_price(250, 50, CompanyBillingCycle.MONTHLY)
        assert pricing.employee_count == 250
        assert pricing.is_enterprise is True
        assert pricing.pricing_model == "per_seat"
        assert pricing.price_per_seat == 25.0
        assert pricing.total_price == 1250.0  # 50 * 25

    def test_enterprise_threshold_yearly(self):
        """Test yearly pricing at enterprise threshold (250 employees)"""
        pricing = calculate_company_price(250, 50, CompanyBillingCycle.YEARLY)
        assert pricing.employee_count == 250
        assert pricing.is_enterprise is True
        assert pricing.pricing_model == "per_seat"
        assert pricing.price_per_seat == 200.0
        assert pricing.total_price == 10000.0  # 50 * 200

    def test_large_enterprise_100_seats(self):
        """Test pricing for large enterprise with 100 seats"""
        pricing = calculate_company_price(300, 100, CompanyBillingCycle.MONTHLY)
        assert pricing.employee_count == 300
        assert pricing.seat_count == 100
        assert pricing.is_enterprise is True
        assert pricing.total_price == 2500.0  # 100 * 25

    def test_large_enterprise_500_seats(self):
        """Test pricing for large enterprise with 500 seats"""
        pricing = calculate_company_price(500, 500, CompanyBillingCycle.MONTHLY)
        assert pricing.employee_count == 500
        assert pricing.seat_count == 500
        assert pricing.is_enterprise is True
        assert pricing.total_price == 12500.0  # 500 * 25

    def test_very_large_enterprise_1000_seats(self):
        """Test pricing for very large enterprise with 1000 seats"""
        pricing = calculate_company_price(1000, 1000, CompanyBillingCycle.YEARLY)
        assert pricing.employee_count == 1000
        assert pricing.seat_count == 1000
        assert pricing.is_enterprise is True
        assert pricing.total_price == 200000.0  # 1000 * 200

    def test_per_seat_scales_linearly(self):
        """Test that per-seat pricing scales linearly with seat count"""
        pricing_50 = calculate_company_price(300, 50, CompanyBillingCycle.MONTHLY)
        pricing_100 = calculate_company_price(300, 100, CompanyBillingCycle.MONTHLY)
        pricing_200 = calculate_company_price(300, 200, CompanyBillingCycle.MONTHLY)

        assert pricing_50.total_price == 1250.0  # 50 * 25
        assert pricing_100.total_price == 2500.0  # 100 * 25
        assert pricing_200.total_price == 5000.0  # 200 * 25
        # Verify linear relationship
        assert pricing_100.total_price == 2 * pricing_50.total_price
        assert pricing_200.total_price == 4 * pricing_50.total_price


class TestCompanyPricingValidation:
    """Test input validation"""

    def test_invalid_employee_count_zero(self):
        """Test error handling for zero employees"""
        with pytest.raises(ValueError, match="Employee count must be at least 1"):
            calculate_company_price(0, 10, CompanyBillingCycle.MONTHLY)

    def test_invalid_employee_count_negative(self):
        """Test error handling for negative employees"""
        with pytest.raises(ValueError, match="Employee count must be at least 1"):
            calculate_company_price(-10, 10, CompanyBillingCycle.MONTHLY)

    def test_invalid_seat_count_zero(self):
        """Test error handling for zero seats"""
        with pytest.raises(ValueError, match="Seat count must be at least 1"):
            calculate_company_price(100, 0, CompanyBillingCycle.MONTHLY)

    def test_invalid_seat_count_negative(self):
        """Test error handling for negative seats"""
        with pytest.raises(ValueError, match="Seat count must be at least 1"):
            calculate_company_price(100, -5, CompanyBillingCycle.MONTHLY)


class TestCompanyPricingConsistency:
    """Test pricing consistency across billing cycles"""

    def test_yearly_equals_52_weeks_flat_rate(self):
        """Test that yearly price equals ~52 weeks for flat rate"""
        weekly = calculate_company_price(100, 10, CompanyBillingCycle.WEEKLY)
        yearly = calculate_company_price(100, 10, CompanyBillingCycle.YEARLY)

        # 250 * 52 = 13000, but yearly is discounted to 8000
        # Yearly discount: (13000 - 8000) / 13000 = 38.5% discount
        assert weekly.total_price * 52 == pytest.approx(13000.0)
        assert yearly.total_price == 8000.0

    def test_yearly_equals_52_weeks_per_seat(self):
        """Test that yearly price equals ~52 weeks for per-seat pricing"""
        weekly = calculate_company_price(300, 100, CompanyBillingCycle.WEEKLY)
        yearly = calculate_company_price(300, 100, CompanyBillingCycle.YEARLY)

        # 6.25 * 100 * 52 = 32500, but yearly is 200 * 100 = 20000
        # Yearly discount: (32500 - 20000) / 32500 = 38.5% discount
        assert weekly.total_price * 52 == pytest.approx(32500.0)
        assert yearly.total_price == 20000.0

    def test_monthly_to_yearly_ratio_flat_rate(self):
        """Test monthly to yearly conversion for flat rate"""
        monthly = calculate_company_price(100, 10, CompanyBillingCycle.MONTHLY)
        yearly = calculate_company_price(100, 10, CompanyBillingCycle.YEARLY)

        # Yearly should be 8x monthly (33% discount vs 12 months)
        assert yearly.total_price == monthly.total_price * 8

    def test_monthly_to_yearly_ratio_per_seat(self):
        """Test monthly to yearly conversion for per-seat pricing"""
        monthly = calculate_company_price(300, 100, CompanyBillingCycle.MONTHLY)
        yearly = calculate_company_price(300, 100, CompanyBillingCycle.YEARLY)

        # Yearly should be 8x monthly (25 * 8 = 200)
        assert yearly.total_price == monthly.total_price * 8


class TestPriceFormatting:
    """Test price formatting"""

    def test_format_small_price(self):
        """Test formatting small price"""
        assert format_price(250.0) == "$250.00"

    def test_format_medium_price(self):
        """Test formatting medium price"""
        assert format_price(1000.0) == "$1,000.00"

    def test_format_large_price(self):
        """Test formatting large price"""
        assert format_price(12500.0) == "$12,500.00"

    def test_format_decimal_price(self):
        """Test formatting price with cents"""
        assert format_price(1250.50) == "$1,250.50"


class TestCompanyPricingTransitionPoint:
    """Test the transition point between flat rate and per-seat pricing"""

    def test_cost_comparison_at_transition(self):
        """Test cost comparison at the transition point (250 employees)"""
        # Just below threshold (flat rate)
        small = calculate_company_price(249, 40, CompanyBillingCycle.MONTHLY)
        # At threshold (per-seat)
        enterprise = calculate_company_price(250, 40, CompanyBillingCycle.MONTHLY)

        assert small.total_price == 1000.0  # Flat rate
        assert enterprise.total_price == 1000.0  # 40 * 25

        # At 40 seats, the pricing is the same at the transition
        # Above 40 seats, per-seat becomes more expensive
        enterprise_60 = calculate_company_price(250, 60, CompanyBillingCycle.MONTHLY)
        assert enterprise_60.total_price == 1500.0  # 60 * 25

    def test_breakeven_point_monthly(self):
        """Test that breakeven point is at 40 seats for monthly billing"""
        # For companies at 250 employees:
        # Flat rate (if it applied): $1,000/month
        # Per-seat: $25/seat/month
        # Breakeven: $1,000 / $25 = 40 seats

        # Below breakeven: per-seat is cheaper
        below = calculate_company_price(250, 30, CompanyBillingCycle.MONTHLY)
        assert below.total_price == 750.0  # 30 * 25 < 1000

        # At breakeven: same price
        at_breakeven = calculate_company_price(250, 40, CompanyBillingCycle.MONTHLY)
        assert at_breakeven.total_price == 1000.0  # 40 * 25 = 1000

        # Above breakeven: per-seat is more expensive
        above = calculate_company_price(250, 50, CompanyBillingCycle.MONTHLY)
        assert above.total_price == 1250.0  # 50 * 25 > 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
