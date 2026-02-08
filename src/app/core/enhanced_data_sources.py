#!/usr/bin/env python3
"""
Enhanced Data Sources - IMF and WHO API Connectors
Global Scenario Engine Data Integration

Implements ETL connectors for:
- IMF (International Monetary Fund) data
- WHO (World Health Organization) data
"""

import logging
from typing import Any

from app.core.global_scenario_engine import DataSource

logger = logging.getLogger(__name__)


class IMFDataSource(DataSource):
    """
    ETL connector for IMF (International Monetary Fund) data.

    Provides access to:
    - World Economic Outlook (WEO) database
    - Fiscal Monitor data
    - Financial indicators
    - Government debt and deficit statistics
    """

    BASE_URL = "http://dataservices.imf.org/REST/SDMX_JSON.svc"

    # IMF indicator mappings
    INDICATORS = {
        "govt_debt": "GGXWDG_NGDP",  # General government gross debt (% of GDP)
        "govt_deficit": "GGXCNL_NGDP",  # General government net lending/borrowing (% of GDP)
        "current_account": "BCA_NGDPD",  # Current account balance (% of GDP)
        "reserves": "FI_RES_TOT_CD",  # Total reserves
        "gdp_nominal": "NGDPD",  # Nominal GDP (US$ billions)
        "gdp_per_capita": "NGDPDPC",  # GDP per capita (US$)
        "inflation_avg": "PCPIPCH",  # Inflation average consumer prices
        "unemployment_rate": "LUR",  # Unemployment rate
        "population": "LP",  # Population (millions)
        "exports": "TX_RPCH",  # Volume of exports of goods and services
        "imports": "TM_RPCH",  # Volume of imports of goods and services
    }

    def fetch_indicator(
        self,
        indicator: str,
        start_year: int,
        end_year: int,
        countries: list[str] | None = None,
    ) -> dict[str, dict[int, float]]:
        """
        Fetch IMF indicator data.

        Args:
            indicator: IMF indicator code
            start_year: Start year
            end_year: End year
            countries: List of ISO3 country codes

        Returns:
            Dictionary mapping country -> {year -> value}
        """
        # IMF API requires specific format
        # CompactData/{database}/{frequency}/{ref-area}/{indicator}
        # Example: CompactData/WEO/A/USA.CHN/GGXWDG_NGDP

        if not countries:
            countries = ["all"]

        country_str = ".".join(countries)

        # Use WEO (World Economic Outlook) database
        url = f"{self.BASE_URL}/CompactData/WEO/A/{country_str}/{indicator}"

        params = {
            "startPeriod": str(start_year),
            "endPeriod": str(end_year),
        }

        data = self.fetch_with_retry(url, params, use_cache=True)

        if not data:
            logger.warning("No IMF data returned for indicator %s", indicator)
            # Return empty dict - IMF API often has limited free access
            # In production, would need proper API credentials
            return {}

        # Parse IMF SDMX-JSON response format
        result = {}

        try:
            if "CompactData" in data and "DataSet" in data["CompactData"]:
                dataset = data["CompactData"]["DataSet"]
                if "Series" in dataset:
                    for series in dataset["Series"]:
                        country_code = series.get("@REF_AREA", "")
                        if "Obs" in series:
                            country_data = {}
                            for obs in series["Obs"]:
                                year = int(obs.get("@TIME_PERIOD", 0))
                                value = float(obs.get("@OBS_VALUE", 0))
                                if year and value:
                                    country_data[year] = value
                            if country_data:
                                result[country_code] = country_data
        except Exception as e:
            logger.warning("Error parsing IMF data: %s", e)
            # For demo purposes, return empty dict
            # In production, this would be handled with proper error recovery

        logger.info("Loaded IMF data for %s countries, indicator %s", len(result), indicator)
        return result

    def fetch_fiscal_data(
        self, start_year: int, end_year: int, countries: list[str] | None = None
    ) -> dict[str, dict[str, dict[int, float]]]:
        """
        Fetch comprehensive fiscal data (debt, deficit, etc.).

        Args:
            start_year: Start year
            end_year: End year
            countries: List of ISO3 country codes

        Returns:
            Dictionary mapping indicator -> country -> {year -> value}
        """
        fiscal_indicators = ["govt_debt", "govt_deficit", "current_account"]
        result = {}

        for indicator_name in fiscal_indicators:
            indicator_code = self.INDICATORS[indicator_name]
            data = self.fetch_indicator(indicator_code, start_year, end_year, countries)
            if data:
                result[indicator_name] = data

        return result


class WHODataSource(DataSource):
    """
    ETL connector for WHO (World Health Organization) data.

    Provides access to:
    - Global Health Observatory (GHO) data
    - COVID-19 statistics
    - Disease surveillance data
    - Health system indicators
    """

    BASE_URL = "https://ghoapi.azureedge.net/api"

    # WHO indicator mappings
    INDICATORS = {
        "life_expectancy": "WHOSIS_000001",  # Life expectancy at birth
        "infant_mortality": "MDG_0000000001",  # Infant mortality rate
        "maternal_mortality": "MDG_0000000026",  # Maternal mortality ratio
        "tuberculosis": "MDG_0000000020",  # Tuberculosis incidence
        "hiv_prevalence": "MDG_0000000029",  # HIV prevalence
        "malaria_incidence": "MALARIA003",  # Malaria incidence
        "health_expenditure": "GHED_CHE_pc_PPP_SHA2011",  # Health expenditure per capita
        "hospital_beds": "HWF_0006",  # Hospital beds per 10,000 population
        "physicians": "HWF_0001",  # Physicians per 10,000 population
        "nurses": "HWF_0002",  # Nurses per 10,000 population
    }

    def fetch_indicator(
        self,
        indicator: str,
        start_year: int | None = None,
        end_year: int | None = None,
        countries: list[str] | None = None,
    ) -> dict[str, dict[int, float]]:
        """
        Fetch WHO indicator data.

        Args:
            indicator: WHO indicator code
            start_year: Start year (optional for WHO API)
            end_year: End year (optional for WHO API)
            countries: List of ISO3 country codes

        Returns:
            Dictionary mapping country -> {year -> value}
        """
        # WHO GHO API format: /api/{indicator}
        url = f"{self.BASE_URL}/{indicator}"

        params = {}
        if countries:
            params["$filter"] = f"SpatialDim in ({','.join(countries)})"

        data = self.fetch_with_retry(url, params, use_cache=True)

        if not data or "value" not in data:
            logger.warning("No WHO data returned for indicator %s", indicator)
            return {}

        # Parse WHO API response
        result = {}

        try:
            for entry in data["value"]:
                country_code = entry.get("SpatialDim", "")
                year = entry.get("TimeDim")
                value = entry.get("NumericValue")

                if country_code and year and value is not None:
                    year = int(year)
                    value = float(value)

                    # Filter by year range if specified
                    if start_year and year < start_year:
                        continue
                    if end_year and year > end_year:
                        continue

                    if country_code not in result:
                        result[country_code] = {}
                    result[country_code][year] = value
        except Exception as e:
            logger.warning("Error parsing WHO data: %s", e)

        logger.info("Loaded WHO data for %s countries, indicator %s", len(result), indicator)
        return result

    def fetch_covid19_data(
        self, start_date: str, end_date: str, countries: list[str] | None = None
    ) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """
        Fetch COVID-19 statistics.

        Note: WHO COVID-19 data is available through a separate API.
        This is a placeholder for future implementation.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            countries: List of ISO3 country codes

        Returns:
            Dictionary with COVID-19 case and death data
        """
        # Placeholder - COVID-19 data requires different endpoint
        # https://covid19.who.int/WHO-COVID-19-global-data.csv
        logger.info("COVID-19 data fetch requested - using placeholder")

        # In production, would implement CSV parsing from WHO COVID-19 dashboard
        return {"cases": {}, "deaths": {}, "vaccinations": {}}

    def fetch_health_indicators(
        self, start_year: int, end_year: int, countries: list[str] | None = None
    ) -> dict[str, dict[str, dict[int, float]]]:
        """
        Fetch comprehensive health indicators.

        Args:
            start_year: Start year
            end_year: End year
            countries: List of ISO3 country codes

        Returns:
            Dictionary mapping indicator -> country -> {year -> value}
        """
        health_indicators = [
            "life_expectancy",
            "infant_mortality",
            "health_expenditure",
        ]

        result = {}

        for indicator_name in health_indicators:
            indicator_code = self.INDICATORS[indicator_name]
            data = self.fetch_indicator(indicator_code, start_year, end_year, countries)
            if data:
                result[indicator_name] = data

        return result


# Integration helper functions


def integrate_imf_data(
    engine, start_year: int, end_year: int, countries: list[str] | None = None
) -> bool:
    """
    Integrate IMF data into the Global Scenario Engine.

    Args:
        engine: GlobalScenarioEngine instance
        start_year: Start year
        end_year: End year
        countries: List of country codes

    Returns:
        bool: Success status
    """
    from app.core.simulation_contingency_root import RiskDomain

    try:
        cache_dir = engine.data_dir / "cache" / "imf"
        imf = IMFDataSource(str(cache_dir))

        # Fetch fiscal data
        fiscal_data = imf.fetch_fiscal_data(start_year, end_year, countries)

        # Integrate government debt into FINANCIAL domain
        if "govt_debt" in fiscal_data:
            if RiskDomain.FINANCIAL not in engine.historical_data:
                engine.historical_data[RiskDomain.FINANCIAL] = {}
            # Merge with existing financial data
            for country, years in fiscal_data["govt_debt"].items():
                if country not in engine.historical_data[RiskDomain.FINANCIAL]:
                    engine.historical_data[RiskDomain.FINANCIAL][country] = {}
                engine.historical_data[RiskDomain.FINANCIAL][country].update(years)

        logger.info("IMF data integration completed")
        return True

    except Exception as e:
        logger.error("Failed to integrate IMF data: %s", e)
        return False


def integrate_who_data(
    engine, start_year: int, end_year: int, countries: list[str] | None = None
) -> bool:
    """
    Integrate WHO data into the Global Scenario Engine.

    Args:
        engine: GlobalScenarioEngine instance
        start_year: Start year
        end_year: End year
        countries: List of country codes

    Returns:
        bool: Success status
    """
    from app.core.simulation_contingency_root import RiskDomain

    try:
        cache_dir = engine.data_dir / "cache" / "who"
        who = WHODataSource(str(cache_dir))

        # Fetch health indicators
        health_data = who.fetch_health_indicators(start_year, end_year, countries)

        # Integrate into PANDEMIC domain
        if "life_expectancy" in health_data:
            if RiskDomain.PANDEMIC not in engine.historical_data:
                engine.historical_data[RiskDomain.PANDEMIC] = {}
            for country, years in health_data["life_expectancy"].items():
                if country not in engine.historical_data[RiskDomain.PANDEMIC]:
                    engine.historical_data[RiskDomain.PANDEMIC][country] = {}
                # Invert life expectancy to risk metric (lower = higher risk)
                for year, value in years.items():
                    engine.historical_data[RiskDomain.PANDEMIC][country][year] = (
                        100 - value
                    )

        logger.info("WHO data integration completed")
        return True

    except Exception as e:
        logger.error("Failed to integrate WHO data: %s", e)
        return False
