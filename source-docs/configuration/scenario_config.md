# Scenario Configuration Module

**Module**: `src/app/core/scenario_config.py` [[src/app/core/scenario_config.py]]  
**Purpose**: Country lists and regional groupings for global scenario analysis  
**Classification**: Domain Configuration  
**Priority**: P2 - Domain-Specific

---

## Overview

The Scenario Configuration module provides comprehensive country coverage for global risk analysis with 58+ countries organized by regions, economic blocs, development status, and population tiers. It supports the Global Scenario Engine with structured country metadata and flexible filtering capabilities.

### Key Characteristics

- **Coverage**: 58 countries (G20, BRICS+, major emerging markets)
- **Groupings**: 9 regional groups, 7 economic blocs
- **Classifications**: Development status (developed, emerging, developing)
- **Population Tiers**: 4 tiers (mega, large, medium, small)
- **Metadata**: Rich country metadata for analysis

---

## Country List

### Comprehensive Coverage (58 Countries)

**G20 Countries** (20):
- USA, CHN, JPN, DEU, GBR, FRA, IND, ITA, BRA, CAN
- KOR, RUS, AUS, ESP, MEX, IDN, NLD, SAU, TUR, ARG, ZAF

**Major Emerging Markets** (16):
- EGY, IRN, ETH, VNM, BGD, PAK, NGA, PHL, THA
- POL, SWE, BEL, AUT, CHE, NOR, DNK

**Additional Coverage** (22):
- Middle East & North Africa: ARE, ISR, QAT, KWT, DZA, MAR
- Asia-Pacific: SGP, MYS, HKG, TWN, NZL
- Latin America: CHL, COL, PER, VEN
- Sub-Saharan Africa: KEN, GHA
- Eastern Europe & Central Asia: UKR, KAZ, UZB

---

## Regional Groups

### Regional Organization

```python
REGIONAL_GROUPS = {
    "north_america": ["USA", "CAN", "MEX"],
    "south_america": ["BRA", "ARG", "CHL", "COL", "PER", "VEN"],
    "europe": [
        "DEU", "GBR", "FRA", "ITA", "ESP", "NLD",
        "POL", "SWE", "BEL", "AUT", "CHE", "NOR", "DNK"
    ],
    "east_asia": ["CHN", "JPN", "KOR", "TWN", "HKG"],
    "southeast_asia": ["IDN", "THA", "VNM", "PHL", "MYS", "SGP"],
    "south_asia": ["IND", "PAK", "BGD"],
    "middle_east": ["SAU", "TUR", "ARE", "ISR", "IRN", "QAT", "KWT"],
    "africa": ["ZAF", "NGA", "EGY", "ETH", "KEN", "GHA", "DZA", "MAR"],
    "oceania": ["AUS", "NZL"],
    "eurasia": ["RUS", "UKR", "KAZ", "UZB"]
}
```

**Coverage by Region**:
- Europe: 13 countries
- Africa: 8 countries
- Middle East: 7 countries
- Southeast Asia: 6 countries
- South America: 6 countries
- East Asia: 5 countries
- Eurasia: 4 countries
- North America: 3 countries
- South Asia: 3 countries
- Oceania: 2 countries

---

## Economic Blocs

### Economic Groupings

```python
ECONOMIC_BLOCS = {
    "g7": ["USA", "CAN", "GBR", "DEU", "FRA", "ITA", "JPN"],
    "g20": [
        "USA", "CHN", "JPN", "DEU", "GBR", "FRA", "IND", "ITA",
        "BRA", "CAN", "KOR", "RUS", "AUS", "ESP", "MEX", "IDN",
        "NLD", "SAU", "TUR", "ARG", "ZAF"
    ],
    "brics": ["BRA", "RUS", "IND", "CHN", "ZAF"],
    "eu": [
        "DEU", "FRA", "ITA", "ESP", "NLD",
        "POL", "BEL", "SWE", "AUT", "DNK"
    ],
    "asean": ["IDN", "THA", "SGP", "MYS", "PHL", "VNM"],
    "opec": ["SAU", "IRN", "ARE", "KWT", "NGA", "DZA", "VEN"],
    "emerging": [
        "CHN", "IND", "BRA", "RUS", "ZAF", "MEX", "IDN", "TUR",
        "SAU", "ARG", "THA", "MYS", "PHL", "EGY", "PAK", "BGD",
        "VNM", "NGA"
    ]
}
```

**Bloc Sizes**:
- G20: 21 countries
- Emerging Markets: 18 countries
- EU: 10 countries (subset in dataset)
- G7: 7 countries
- ASEAN: 6 countries
- OPEC: 7 countries
- BRICS: 5 countries

---

## Development Categories

### Classification by Development Status

```python
DEVELOPMENT_CATEGORIES = {
    "developed": [
        "USA", "CAN", "GBR", "DEU", "FRA", "ITA", "ESP", "JPN",
        "KOR", "AUS", "NLD", "CHE", "SWE", "NOR", "DNK", "BEL",
        "AUT", "SGP", "NZL", "ISR", "HKG", "TWN"
    ],  # 22 countries
    
    "emerging": [
        "CHN", "IND", "BRA", "RUS", "ZAF", "MEX", "IDN", "TUR",
        "SAU", "ARG", "THA", "MYS", "PHL", "EGY", "PAK", "BGD",
        "VNM", "NGA", "COL", "PER", "MAR", "KEN"
    ],  # 22 countries
    
    "developing": [
        "ETH", "GHA", "UZB", "KAZ", "DZA", "VEN", "UKR", "ARE",
        "QAT", "KWT", "IRN", "CHL", "POL"
    ]  # 13 countries
}
```

**Distribution**:
- Developed: 22 countries (38%)
- Emerging: 22 countries (38%)
- Developing: 13 countries (22%)

---

## Population Tiers

### Classification by Population Size

```python
POPULATION_TIERS = {
    "mega": [  # 100M+
        "CHN", "IND", "USA", "IDN", "PAK",
        "BRA", "NGA", "BGD", "RUS", "MEX"
    ],  # 10 countries
    
    "large": [  # 50-100M
        "JPN", "ETH", "PHL", "EGY", "VNM",
        "TUR", "IRN", "DEU", "THA", "GBR",
        "FRA", "ITA", "ZAF", "KOR", "ESP"
    ],  # 15 countries
    
    "medium": [  # 20-50M
        "COL", "ARG", "DZA", "UKR", "CAN",
        "MAR", "SAU", "UZB", "PER", "MYS",
        "VEN", "GHA", "AUS", "KAZ"
    ],  # 14 countries
    
    "small": [  # <20M
        "NLD", "CHL", "KEN", "POL", "TWN",
        "BEL", "SWE", "CHE", "AUT", "ARE",
        "ISR", "NOR", "SGP", "DNK", "HKG",
        "NZL", "QAT", "KWT"
    ]  # 18 countries
}
```

---

## Core API

### Country List Retrieval

```python
def get_country_list(
    category: str = "comprehensive",
    region: str | None = None,
    bloc: str | None = None
) -> list[str]:
    """Get country list based on category, region, or economic bloc.
    
    Args:
        category: "comprehensive", "g20", "g7", "emerging", etc.
        region: Regional filter (e.g., "europe", "asia")
        bloc: Economic bloc filter (e.g., "eu", "asean")
    
    Returns:
        List of ISO3 country codes
    
    Priority:
        1. bloc (if specified)
        2. region (if specified)
        3. category
    
    Examples:
        >>> get_country_list(category="g20")
        ['USA', 'CHN', 'JPN', ...]
        
        >>> get_country_list(region="europe")
        ['DEU', 'GBR', 'FRA', ...]
        
        >>> get_country_list(bloc="brics")
        ['BRA', 'RUS', 'IND', 'CHN', 'ZAF']
    """
```

### Country Metadata

```python
def get_country_metadata(country_code: str) -> dict[str, Any]:
    """Get metadata for a country.
    
    Args:
        country_code: ISO3 country code
    
    Returns:
        {
            "code": str,
            "regions": list[str],
            "blocs": list[str],
            "development": str,
            "population_tier": str
        }
    
    Example:
        >>> get_country_metadata("USA")
        {
            'code': 'USA',
            'regions': ['north_america'],
            'blocs': ['g7', 'g20'],
            'development': 'developed',
            'population_tier': 'mega'
        }
    """
```

---

## Default Configurations

### Demo Configurations

```python
DEFAULT_DEMO_CONFIG = {
    # Quick demo (20 countries)
    "countries": COMPREHENSIVE_COUNTRY_LIST[:20],
    
    # Full analysis (58 countries)
    "full_countries": COMPREHENSIVE_COUNTRY_LIST,
    
    # Original sample (8 countries)
    "sample_countries": [
        "USA", "CHN", "GBR", "DEU",
        "FRA", "IND", "BRA", "RUS"
    ]
}
```

---

## Usage Patterns

### Pattern 1: Regional Analysis

```python
from src.app.core.scenario_config import get_country_list

# Analyze Europe
european_countries = get_country_list(region="europe")
for country in european_countries:
    analyze_risk(country)

# Analyze Southeast Asia
sea_countries = get_country_list(region="southeast_asia")
```

### Pattern 2: Economic Bloc Analysis

```python
# G20 analysis
g20_countries = get_country_list(bloc="g20")

# BRICS analysis
brics_countries = get_country_list(bloc="brics")

# Emerging markets
emerging_countries = get_country_list(category="emerging")
```

### Pattern 3: Development-Based Filtering

```python
# Developed countries only
developed = get_country_list(category="developed")

# Emerging markets
emerging = get_country_list(category="emerging")

# All developing
developing = get_country_list(category="developing")
```

### Pattern 4: Population-Weighted Analysis

```python
from src.app.core.scenario_config import (
    POPULATION_TIERS,
    get_country_metadata
)

# Focus on high-population countries
mega_countries = POPULATION_TIERS["mega"]
for country in mega_countries:
    # Weight by population
    metadata = get_country_metadata(country)
    analyze_with_weight(country, weight=10.0)
```

### Pattern 5: Multi-Dimensional Filtering

```python
# Get all European emerging markets
european_countries = set(get_country_list(region="europe"))
emerging_countries = set(get_country_list(category="emerging"))
european_emerging = european_countries & emerging_countries
# Result: ['POL']

# Get G20 members in Asia
g20 = set(get_country_list(bloc="g20"))
east_asia = set(get_country_list(region="east_asia"))
southeast_asia = set(get_country_list(region="southeast_asia"))
asian_g20 = g20 & (east_asia | southeast_asia)
# Result: ['CHN', 'JPN', 'KOR', 'IDN']
```

---

## Analysis Scenarios

### Scenario 1: Global Economic Crisis

```python
# Focus on systemically important economies
g20_countries = get_country_list(bloc="g20")
financial_centers = ["USA", "GBR", "JPN", "CHN", "DEU", "FRA"]

# Analyze contagion risk
for country in g20_countries:
    metadata = get_country_metadata(country)
    risk_score = calculate_systemic_risk(country, metadata)
```

### Scenario 2: Regional Conflict

```python
# Analyze specific region + neighbors
region_countries = get_country_list(region="middle_east")

# Include economically connected countries
for country in region_countries:
    metadata = get_country_metadata(country)
    # Expand to include trade partners
    trade_partners = get_trade_partners(country)
```

### Scenario 3: Climate Change Impact

```python
# Population-weighted analysis
for tier_name, countries in POPULATION_TIERS.items():
    tier_weight = {
        "mega": 4,
        "large": 3,
        "medium": 2,
        "small": 1
    }[tier_name]
    
    for country in countries:
        assess_climate_risk(country, weight=tier_weight)
```

---

## Metadata Examples

### Country Metadata Samples

**United States**:
```python
{
    'code': 'USA',
    'regions': ['north_america'],
    'blocs': ['g7', 'g20'],
    'development': 'developed',
    'population_tier': 'mega'
}
```

**China**:
```python
{
    'code': 'CHN',
    'regions': ['east_asia'],
    'blocs': ['g20', 'brics', 'emerging'],
    'development': 'emerging',
    'population_tier': 'mega'
}
```

**Poland**:
```python
{
    'code': 'POL',
    'regions': ['europe'],
    'blocs': ['eu'],
    'development': 'developing',
    'population_tier': 'small'
}
```

**Singapore**:
```python
{
    'code': 'SGP',
    'regions': ['southeast_asia'],
    'blocs': ['asean'],
    'development': 'developed',
    'population_tier': 'small'
}
```

---

## Testing

### Unit Testing

```python
import pytest
from src.app.core.scenario_config import (
    get_country_list,
    get_country_metadata,
    COMPREHENSIVE_COUNTRY_LIST
)

def test_comprehensive_list():
    countries = get_country_list()
    assert len(countries) == len(COMPREHENSIVE_COUNTRY_LIST)
    assert "USA" in countries
    assert "CHN" in countries

def test_regional_filtering():
    europe = get_country_list(region="europe")
    assert "DEU" in europe
    assert "FRA" in europe
    assert "USA" not in europe

def test_bloc_filtering():
    g7 = get_country_list(bloc="g7")
    assert len(g7) == 7
    assert "USA" in g7
    assert "CHN" not in g7

def test_country_metadata():
    metadata = get_country_metadata("USA")
    assert metadata["code"] == "USA"
    assert "north_america" in metadata["regions"]
    assert "g7" in metadata["blocs"]
    assert metadata["development"] == "developed"
    assert metadata["population_tier"] == "mega"

def test_development_category():
    developed = get_country_list(category="developed")
    emerging = get_country_list(category="emerging")
    developing = get_country_list(category="developing")
    
    # No overlap
    assert not (set(developed) & set(emerging))
    assert not (set(developed) & set(developing))
    assert not (set(emerging) & set(developing))
```

---

## Best Practices

1. **Use ISO3 Codes**: Always use 3-letter ISO country codes
2. **Check Metadata**: Use `get_country_metadata()` for rich context
3. **Cache Results**: Cache country lists for repeated queries
4. **Validate Codes**: Check returned codes exist before use
5. **Document Groupings**: Document custom groupings in code
6. **Population Weighting**: Consider population when aggregating
7. **Regional Context**: Include neighboring regions for complete analysis
8. **Development Status**: Consider development level in risk assessment
9. **Economic Blocs**: Account for bloc membership in contagion analysis
10. **Update Regularly**: Review country classifications annually

---

## Related Modules

- **Global Scenario Engine**: `src/app/core/global_scenario_engine.py` [[src/app/core/global_scenario_engine.py]] - Uses country lists
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - General configuration
- **Constitutional Scenario Engine**: `src/app/core/constitutional_scenario_engine.py` [[src/app/core/constitutional_scenario_engine.py]] - Scenario analysis

---

## Future Enhancements

1. **Dynamic Updates**: Fetch country data from external sources
2. **GDP Weighting**: Add GDP tiers for economic weighting
3. **Trade Networks**: Include trade relationship data
4. **Alliance Networks**: Military alliance memberships
5. **Climate Zones**: Climate classification for risk analysis
6. **Natural Resources**: Resource dependency data
7. **Demographic Data**: Age distribution, urbanization
8. **Political Stability**: Stability indices
9. **Custom Groupings**: User-defined country groups
10. **Historical Data**: Track country classification changes over time


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/scenario_config.py]]
