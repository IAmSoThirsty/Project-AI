#!/usr/bin/env python3
"""
Scenario Configuration - Country Lists and Regional Groupings
Global Scenario Engine Configuration Module

Provides comprehensive country coverage for global risk analysis with:
- G20 countries
- Major emerging markets
- Regional representatives
- Economic blocs
"""

from typing import Any

# Complete list of 50+ countries for comprehensive global coverage
COMPREHENSIVE_COUNTRY_LIST = [
    # G20 Countries (19 members + EU)
    "USA",  # United States
    "CHN",  # China
    "JPN",  # Japan
    "DEU",  # Germany
    "GBR",  # United Kingdom
    "FRA",  # France
    "IND",  # India
    "ITA",  # Italy
    "BRA",  # Brazil
    "CAN",  # Canada
    "KOR",  # South Korea
    "RUS",  # Russia
    "AUS",  # Australia
    "ESP",  # Spain
    "MEX",  # Mexico
    "IDN",  # Indonesia
    "NLD",  # Netherlands
    "SAU",  # Saudi Arabia
    "TUR",  # Turkey
    "ARG",  # Argentina
    "ZAF",  # South Africa
    # Major Emerging Markets (BRICS+)
    # (BRA, RUS, IND, CHN, ZAF already in G20)
    "EGY",  # Egypt
    "IRN",  # Iran
    "ETH",  # Ethiopia
    "VNM",  # Vietnam
    "BGD",  # Bangladesh
    "PAK",  # Pakistan
    "NGA",  # Nigeria
    "PHL",  # Philippines
    "THA",  # Thailand
    # European Union Representatives
    "POL",  # Poland
    "SWE",  # Sweden
    "BEL",  # Belgium
    "AUT",  # Austria
    "CHE",  # Switzerland
    "NOR",  # Norway
    "DNK",  # Denmark
    # Middle East & North Africa
    "ARE",  # United Arab Emirates
    "ISR",  # Israel
    "QAT",  # Qatar
    "KWT",  # Kuwait
    "DZA",  # Algeria
    "MAR",  # Morocco
    # Asia-Pacific
    "SGP",  # Singapore
    "MYS",  # Malaysia
    "HKG",  # Hong Kong
    "TWN",  # Taiwan
    "NZL",  # New Zealand
    # Latin America
    "CHL",  # Chile
    "COL",  # Colombia
    "PER",  # Peru
    "VEN",  # Venezuela
    # Sub-Saharan Africa
    "KEN",  # Kenya
    "GHA",  # Ghana
    # Eastern Europe & Central Asia
    "UKR",  # Ukraine
    "KAZ",  # Kazakhstan
    "UZB",  # Uzbekistan
]

# Regional groupings for analysis
REGIONAL_GROUPS = {
    "north_america": ["USA", "CAN", "MEX"],
    "south_america": ["BRA", "ARG", "CHL", "COL", "PER", "VEN"],
    "europe": [
        "DEU",
        "GBR",
        "FRA",
        "ITA",
        "ESP",
        "NLD",
        "POL",
        "SWE",
        "BEL",
        "AUT",
        "CHE",
        "NOR",
        "DNK",
    ],
    "east_asia": ["CHN", "JPN", "KOR", "TWN", "HKG"],
    "southeast_asia": ["IDN", "THA", "VNM", "PHL", "MYS", "SGP"],
    "south_asia": ["IND", "PAK", "BGD"],
    "middle_east": ["SAU", "TUR", "ARE", "ISR", "IRN", "QAT", "KWT"],
    "africa": ["ZAF", "NGA", "EGY", "ETH", "KEN", "GHA", "DZA", "MAR"],
    "oceania": ["AUS", "NZL"],
    "eurasia": ["RUS", "UKR", "KAZ", "UZB"],
}

# Economic bloc groupings
ECONOMIC_BLOCS = {
    "g7": ["USA", "CAN", "GBR", "DEU", "FRA", "ITA", "JPN"],
    "g20": [
        "USA",
        "CHN",
        "JPN",
        "DEU",
        "GBR",
        "FRA",
        "IND",
        "ITA",
        "BRA",
        "CAN",
        "KOR",
        "RUS",
        "AUS",
        "ESP",
        "MEX",
        "IDN",
        "NLD",
        "SAU",
        "TUR",
        "ARG",
        "ZAF",
    ],
    "brics": ["BRA", "RUS", "IND", "CHN", "ZAF"],
    "eu": ["DEU", "FRA", "ITA", "ESP", "NLD", "POL", "BEL", "SWE", "AUT", "DNK"],
    "asean": ["IDN", "THA", "SGP", "MYS", "PHL", "VNM"],
    "opec": ["SAU", "IRN", "ARE", "KWT", "NGA", "DZA", "VEN"],
    "emerging": [
        "CHN",
        "IND",
        "BRA",
        "RUS",
        "ZAF",
        "MEX",
        "IDN",
        "TUR",
        "SAU",
        "ARG",
        "THA",
        "MYS",
        "PHL",
        "EGY",
        "PAK",
        "BGD",
        "VNM",
        "NGA",
    ],
}

# Development status classifications
DEVELOPMENT_CATEGORIES = {
    "developed": [
        "USA",
        "CAN",
        "GBR",
        "DEU",
        "FRA",
        "ITA",
        "ESP",
        "JPN",
        "KOR",
        "AUS",
        "NLD",
        "CHE",
        "SWE",
        "NOR",
        "DNK",
        "BEL",
        "AUT",
        "SGP",
        "NZL",
        "ISR",
        "HKG",
        "TWN",
    ],
    "emerging": [
        "CHN",
        "IND",
        "BRA",
        "RUS",
        "ZAF",
        "MEX",
        "IDN",
        "TUR",
        "SAU",
        "ARG",
        "THA",
        "MYS",
        "PHL",
        "EGY",
        "PAK",
        "BGD",
        "VNM",
        "NGA",
        "COL",
        "PER",
        "MAR",
        "KEN",
    ],
    "developing": [
        "ETH",
        "GHA",
        "UZB",
        "KAZ",
        "DZA",
        "VEN",
        "UKR",
        "ARE",
        "QAT",
        "KWT",
        "IRN",
        "CHL",
        "POL",
    ],
}

# Population tiers for weighted analysis
POPULATION_TIERS = {
    "mega": [
        "CHN",
        "IND",
        "USA",
        "IDN",
        "PAK",
        "BRA",
        "NGA",
        "BGD",
        "RUS",
        "MEX",
    ],  # 100M+
    "large": [
        "JPN",
        "ETH",
        "PHL",
        "EGY",
        "VNM",
        "TUR",
        "IRN",
        "DEU",
        "THA",
        "GBR",
        "FRA",
        "ITA",
        "ZAF",
        "KOR",
        "ESP",
    ],  # 50-100M
    "medium": [
        "COL",
        "ARG",
        "DZA",
        "UKR",
        "CAN",
        "MAR",
        "SAU",
        "UZB",
        "PER",
        "MYS",
        "VEN",
        "GHA",
        "AUS",
        "KAZ",
    ],  # 20-50M
    "small": [
        "NLD",
        "CHL",
        "KEN",
        "POL",
        "TWN",
        "BEL",
        "SWE",
        "CHE",
        "AUT",
        "ARE",
        "ISR",
        "NOR",
        "SGP",
        "DNK",
        "HKG",
        "NZL",
        "QAT",
        "KWT",
    ],  # <20M
}


def get_country_list(
    category: str = "comprehensive", region: str | None = None, bloc: str | None = None
) -> list[str]:
    """
    Get country list based on category, region, or economic bloc.

    Args:
        category: "comprehensive", "g20", "g7", "emerging", etc.
        region: Regional filter (e.g., "europe", "asia")
        bloc: Economic bloc filter (e.g., "eu", "asean")

    Returns:
        List of ISO3 country codes
    """
    if bloc and bloc in ECONOMIC_BLOCS:
        return ECONOMIC_BLOCS[bloc]

    if region and region in REGIONAL_GROUPS:
        return REGIONAL_GROUPS[region]

    if category == "comprehensive":
        return COMPREHENSIVE_COUNTRY_LIST
    elif category in ECONOMIC_BLOCS:
        return ECONOMIC_BLOCS[category]
    elif category in DEVELOPMENT_CATEGORIES:
        return DEVELOPMENT_CATEGORIES[category]
    else:
        return COMPREHENSIVE_COUNTRY_LIST


def get_country_metadata(country_code: str) -> dict[str, Any]:
    """
    Get metadata for a country.

    Args:
        country_code: ISO3 country code

    Returns:
        Dictionary with country metadata
    """
    metadata = {
        "code": country_code,
        "regions": [],
        "blocs": [],
        "development": None,
        "population_tier": None,
    }

    # Find regions
    for region, countries in REGIONAL_GROUPS.items():
        if country_code in countries:
            metadata["regions"].append(region)

    # Find economic blocs
    for bloc, countries in ECONOMIC_BLOCS.items():
        if country_code in countries:
            metadata["blocs"].append(bloc)

    # Find development category
    for category, countries in DEVELOPMENT_CATEGORIES.items():
        if country_code in countries:
            metadata["development"] = category
            break

    # Find population tier
    for tier, countries in POPULATION_TIERS.items():
        if country_code in countries:
            metadata["population_tier"] = tier
            break

    return metadata


# Default configuration for demo
DEFAULT_DEMO_CONFIG = {
    "countries": COMPREHENSIVE_COUNTRY_LIST[:20],  # Start with 20 for faster demo
    "full_countries": COMPREHENSIVE_COUNTRY_LIST,  # All 58 countries
    "sample_countries": [
        "USA",
        "CHN",
        "GBR",
        "DEU",
        "FRA",
        "IND",
        "BRA",
        "RUS",
    ],  # Original 8
}
