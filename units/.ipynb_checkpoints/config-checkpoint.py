"""
Configuration file for lactic acid biorefinery simulation.

All process parameters, economic assumptions, and settings in one place.
Modify these values to run different scenarios - no need to touch the simulation code!

Author: Susila Hadiyati
Date: October 2025
"""

# =============================================================================
# PRODUCTION TARGETS
# =============================================================================
ANNUAL_PRODUCTION_TARGET = 50000  # metric tons/year of lactic acid
OPERATING_DAYS = 330  # days/year (accounting for maintenance)

# =============================================================================
# FERMENTATION PARAMETERS
# =============================================================================
FERMENTATION_TEMP_C = 37  # °C - Optimal for Lactobacillus
FERMENTATION_TIME = 48  # hours - Batch fermentation time
GLUCOSE_CONVERSION = 0.90  # 90% conversion efficiency (0-1)
BIOMASS_YIELD = 0.08  # g biomass / g glucose consumed

# =============================================================================
# FEED CONDITIONS
# =============================================================================
GLUCOSE_CONCENTRATION = 0.20  # 20% w/w glucose solution
STERILIZATION_TEMP_C = 121  # °C - Autoclave temperature
FEED_TEMP_C = 30  # °C - Ambient temperature

# =============================================================================
# SEPARATION (Centrifuge splits - fraction to liquid phase)
# =============================================================================
WATER_SPLIT = 0.97  # 97% water to liquid
LACTIC_ACID_SPLIT = 0.99  # 99% lactic acid to liquid
GLUCOSE_SPLIT = 0.97
ETHANOL_SPLIT = 0.95
BIOMASS_SPLIT = 0.01  # 99% biomass to solids

# =============================================================================
# EVAPORATION
# =============================================================================
WATER_REMOVAL_FRACTION = 0.70  # Remove 70% of water
EVAPORATION_PRESSURE_KPA = 20  # 20 kPa vacuum
EVAPORATION_TEMP_C = 80  # °C - Boiling point at reduced pressure

# =============================================================================
# PRODUCT
# =============================================================================
PRODUCT_TEMP_C = 25  # °C - Final product temperature

# =============================================================================
# ECONOMIC PARAMETERS (2019 USD)
# =============================================================================

# Prices ($/kg)
GLUCOSE_PRICE = 0.35  # Industrial glucose
LACTIC_ACID_PRICE = 1.50  # 80-88% industrial grade
NUTRIENTS_PRICE = 0.20  # Yeast extract, minerals

# TEA Settings
IRR_TARGET = 0.10  # 10% target internal rate of return
PROJECT_START_YEAR = 2026
PROJECT_END_YEAR = 2046  # 20-year project lifetime
INCOME_TAX_RATE = 0.21  # 21% corporate tax
DEPRECIATION = "MACRS7"  # 7-year MACRS

# Capital & Construction
LANG_FACTOR = 3.0  # Installed cost = 3.0 × Equipment cost
CONSTRUCTION_SCHEDULE = (0.4, 0.6)  # 40% year 1, 60% year 2
WORKING_CAPITAL_FRACTION = 0.05  # 5% of FCI

# Startup
STARTUP_MONTHS = 3
STARTUP_FOC_FRACTION = 1.0  # 100% fixed costs during startup
STARTUP_VOC_FRACTION = 0.75  # 75% variable costs
STARTUP_SALES_FRACTION = 0.5  # 50% sales during startup

# Financing
FINANCE_INTEREST_RATE = 0.08  # 8% interest on debt
FINANCE_YEARS = 10  # 10-year loan
FINANCE_FRACTION = 0.4  # 40% debt, 60% equity

# Fixed Operating Costs
LABOR_COST_ANNUAL = 2500000  # $2.5M/year
MAINTENANCE_FRACTION = 0.03  # 3% of FCI
INSURANCE_FRACTION = 0.007  # 0.7% of FCI
SUPERVISION_FRACTION = 0.20  # 20% of labor
LABORATORY_FRACTION = 0.15  # 15% of labor
OVERHEAD_FRACTION = 0.60  # 60% of (labor + supervision + maintenance)

# =============================================================================
# UTILITY PRICES
# =============================================================================
ELECTRICITY_PRICE = 0.0685  # $/kWh
CEPCI = 607.5  # Chemical Engineering Plant Cost Index (2019)

# =============================================================================
# EQUIPMENT SIZING PARAMETERS
# =============================================================================

# Fermentation Reactor
REACTOR_SIZE_M3 = 100  # Standard reactor size
REACTOR_BASE_COST = 200000  # $ for 100 m³ reactor
REACTOR_INSTALLATION_FACTOR = 2.8

# Evaporator
EVAPORATOR_BASE_COST = 80000  # $ for base size
EVAPORATOR_BASE_VOLUME = 50  # m³
EVAPORATOR_INSTALLATION_FACTOR = 3.2
HEAT_TRANSFER_COEFF = 0.5  # kW/m²/K
LMTD = 30  # K - Log mean temperature difference

# =============================================================================
# CALCULATED PARAMETERS (Don't modify these)
# =============================================================================
OPERATING_HOURS = OPERATING_DAYS * 24
LA_PRODUCTION_RATE = (ANNUAL_PRODUCTION_TARGET * 1000) / OPERATING_HOURS  # kg/hr
GLUCOSE_FEED_RATE = LA_PRODUCTION_RATE / GLUCOSE_CONVERSION  # kg/hr