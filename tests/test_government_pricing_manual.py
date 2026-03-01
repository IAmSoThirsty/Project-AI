"""
Manual validation tests for Government Tier Progressive Pricing

Tests the progressive seat-based pricing implementation without pytest.
"""

import sys

from src.app.governance.government_pricing import (
    GovernmentBillingCycle,
    calculate_government_price,
    calculate_government_tier_multiplier,
)


def test_tier_multipliers():
    """Test tier multiplier calculations"""
    print("Testing tier multipliers...")

    test_cases = [
        (1, 1.0, 0, 0.0),  # Tier 0
        (25, 1.0, 0, 0.0),  # Tier 0 boundary
        (26, 1.15, 1, 15.0),  # Tier 1
        (50, 1.15, 1, 15.0),  # Tier 1 boundary
        (51, 1.30, 2, 30.0),  # Tier 2
        (75, 1.30, 2, 30.0),  # Tier 2 boundary
        (100, 1.45, 3, 45.0),  # Tier 3
        (125, 1.60, 4, 60.0),  # Tier 4
        (150, 1.75, 5, 75.0),  # Tier 5
    ]

    passed = 0
    failed = 0

    for seats, expected_mult, expected_tier, expected_increase in test_cases:
        mult, tier, increase = calculate_government_tier_multiplier(seats)
        if (
            mult == expected_mult
            and tier == expected_tier
            and increase == expected_increase
        ):
            print(f"  ✓ {seats} seats: {mult}x, tier {tier}, +{increase}%")
            passed += 1
        else:
            print(
                f"  ✗ {seats} seats: Expected {expected_mult}x, got {mult}x (tier {tier}, +{increase}%)"
            )
            failed += 1

    print(f"  Passed: {passed}/{len(test_cases)}")
    return failed == 0


def test_monthly_pricing():
    """Test monthly pricing calculations"""
    print("\nTesting monthly pricing...")

    test_cases = [
        (10, 2500.0, 0, 0.0),  # Base tier
        (25, 2500.0, 0, 0.0),  # Base tier boundary
        (30, 2875.0, 1, 15.0),  # Tier 1
        (50, 2875.0, 1, 15.0),  # Tier 1 boundary
        (60, 3250.0, 2, 30.0),  # Tier 2
        (75, 3250.0, 2, 30.0),  # Tier 2 boundary
        (100, 3625.0, 3, 45.0),  # Tier 3
        (125, 4000.0, 4, 60.0),  # Tier 4
    ]

    passed = 0
    failed = 0

    for seats, expected_price, expected_tier, expected_increase in test_cases:
        pricing = calculate_government_price(seats, GovernmentBillingCycle.MONTHLY)
        if (
            pricing.total_price == expected_price
            and pricing.tier_number == expected_tier
            and pricing.price_increase_percentage == expected_increase
        ):
            print(
                f"  ✓ {seats} seats: ${pricing.total_price:,.2f} (tier {pricing.tier_number}, +{pricing.price_increase_percentage:.0f}%)"
            )
            passed += 1
        else:
            print(
                f"  ✗ {seats} seats: Expected ${expected_price:,.2f}, got ${pricing.total_price:,.2f}"
            )
            failed += 1

    print(f"  Passed: {passed}/{len(test_cases)}")
    return failed == 0


def test_yearly_pricing():
    """Test yearly pricing calculations"""
    print("\nTesting yearly pricing...")

    test_cases = [
        (10, 10000.0),  # Base tier
        (25, 10000.0),  # Base tier boundary
        (30, 11500.0),  # Tier 1
        (50, 11500.0),  # Tier 1 boundary
        (60, 13000.0),  # Tier 2
        (75, 13000.0),  # Tier 2 boundary
        (100, 14500.0),  # Tier 3
        (125, 16000.0),  # Tier 4
    ]

    passed = 0
    failed = 0

    for seats, expected_price in test_cases:
        pricing = calculate_government_price(seats, GovernmentBillingCycle.YEARLY)
        if pricing.total_price == expected_price:
            print(f"  ✓ {seats} seats: ${pricing.total_price:,.2f}")
            passed += 1
        else:
            print(
                f"  ✗ {seats} seats: Expected ${expected_price:,.2f}, got ${pricing.total_price:,.2f}"
            )
            failed += 1

    print(f"  Passed: {passed}/{len(test_cases)}")
    return failed == 0


def test_pricing_consistency():
    """Test that yearly is 4x monthly"""
    print("\nTesting pricing consistency (yearly = 4x monthly)...")

    test_seats = [10, 25, 50, 75, 100, 125]
    passed = 0
    failed = 0

    for seats in test_seats:
        monthly = calculate_government_price(seats, GovernmentBillingCycle.MONTHLY)
        yearly = calculate_government_price(seats, GovernmentBillingCycle.YEARLY)

        expected_yearly = monthly.total_price * 4.0
        if abs(yearly.total_price - expected_yearly) < 0.01:  # Allow tiny float error
            print(
                f"  ✓ {seats} seats: Monthly ${monthly.total_price:,.2f} × 4 = Yearly ${yearly.total_price:,.2f}"
            )
            passed += 1
        else:
            print(
                f"  ✗ {seats} seats: Expected ${expected_yearly:,.2f}, got ${yearly.total_price:,.2f}"
            )
            failed += 1

    print(f"  Passed: {passed}/{len(test_seats)}")
    return failed == 0


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("\nTesting error handling...")

    try:
        calculate_government_tier_multiplier(0)
        print("  ✗ Should have raised ValueError for 0 seats")
        return False
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError for 0 seats: {e}")

    try:
        calculate_government_tier_multiplier(-10)
        print("  ✗ Should have raised ValueError for negative seats")
        return False
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError for negative seats: {e}")

    try:
        calculate_government_price(0, GovernmentBillingCycle.MONTHLY)
        print("  ✗ Should have raised ValueError for 0 seats in pricing")
        return False
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError for 0 seats in pricing: {e}")

    print("  Passed: 3/3")
    return True


def main():
    """Run all validation tests"""
    print("=" * 70)
    print("Government Tier Progressive Pricing - Validation Tests")
    print("=" * 70)

    all_passed = True

    all_passed &= test_tier_multipliers()
    all_passed &= test_monthly_pricing()
    all_passed &= test_yearly_pricing()
    all_passed &= test_pricing_consistency()
    all_passed &= test_error_handling()

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
