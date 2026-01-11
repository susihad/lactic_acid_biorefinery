"""
Lactic Acid Biorefinery Simulation

Complete process simulation and techno-economic analysis using BioSTEAM.
This is a cleaner, organized version of the original monolithic script.

Process: Glucose → Lactic Acid via Lactobacillus fermentation

Author: Susila Hadiyati
Date: October 2025
"""

import biosteam as bst
import thermosteam as tmo
from biosteam.units import HXutility, SolidsCentrifuge
from thermosteam import Stream
import numpy as np

# Import custom units and config
from units import LacticAcidFermentation, LacticAcidEvaporator
import config

import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# =============================================================================
# Setup BioSTEAM Environment
# =============================================================================

print("="*80)
print("LACTIC ACID BIOREFINERY - BioSTEAM SIMULATION")
print("="*80)
print(f"BioSTEAM version: {bst.__version__}")
print(f"ThermoSTEAM version: {tmo.__version__}")
print("-"*80)

bst.CE = config.CEPCI
bst.PowerUtility.price = config.ELECTRICITY_PRICE
bst.main_flowsheet.set_flowsheet('lactic_acid')

# =============================================================================
# Define Chemicals
# =============================================================================

# Try to load WWTsludge, if not available, create it
try:
    chems = tmo.Chemicals(['Water', 'Glucose', 'LacticAcid', 'Ethanol', 'WWTsludge'])
except:
    print("Note: Creating custom biomass chemical (WWTsludge not in database)")
    from thermosteam import Chemical
    
    # Load standard chemicals
    chems = tmo.Chemicals(['Water', 'Glucose', 'LacticAcid', 'Ethanol'])
    
    # Create biomass as a blank chemical
    WWTsludge = Chemical.blank('WWTsludge', phase='s', formula='CH1.8O0.5N0.2')
    WWTsludge.default()
    
    chems.append(WWTsludge)

tmo.settings.set_thermo(chems)

print("\nChemicals loaded:")
for chem in chems:
    print(f"  - {chem.ID}: {chem.formula}")
print("-"*80)

# =============================================================================
# Display Configuration
# =============================================================================

print(f"\nProduction Target: {config.ANNUAL_PRODUCTION_TARGET:,} MT/year")
print(f"Operating days: {config.OPERATING_DAYS} days/year")
print(f"Required LA production rate: {config.LA_PRODUCTION_RATE:.1f} kg/hr")
print(f"Required glucose feed rate: {config.GLUCOSE_FEED_RATE:.1f} kg/hr")
print("-"*80)

# =============================================================================
# Create Streams
# =============================================================================

glucose_feed = Stream(
    'glucose_feed',
    Glucose=config.GLUCOSE_FEED_RATE,
    Water=config.GLUCOSE_FEED_RATE * 4,  # 20% w/w solution
    T=config.FEED_TEMP_C + 273.15,
    P=101325,
    units='kg/hr'
)

# =============================================================================
# Unit Operations
# =============================================================================

# H101: Feed Sterilization
H101 = HXutility('H101', ins=glucose_feed, T=config.STERILIZATION_TEMP_C + 273.15)

# H102: Cooling to fermentation temperature
H102 = HXutility('H102', ins=H101-0, T=config.FERMENTATION_TEMP_C + 273.15)

# R201: Fermentation Reactor
R201 = LacticAcidFermentation(
    'R201',
    ins=H102-0,
    outs='fermentation_broth',
    tau=config.FERMENTATION_TIME,
    conversion=config.GLUCOSE_CONVERSION,
    biomass_yield=config.BIOMASS_YIELD
)

# S301: Centrifuge (cell separation)
S301 = SolidsCentrifuge(
    'S301',
    ins=R201-0,
    outs=('clarified_broth', 'cell_waste'),
    split=dict(
        Water=config.WATER_SPLIT,
        LacticAcid=config.LACTIC_ACID_SPLIT,
        Glucose=config.GLUCOSE_SPLIT,
        Ethanol=config.ETHANOL_SPLIT,
        WWTsludge=config.BIOMASS_SPLIT
    )
)

# E301: Evaporator
E301 = LacticAcidEvaporator(
    'E301',
    ins=S301-0,
    outs=('concentrated_LA', 'water_vapor'),
    V=config.WATER_REMOVAL_FRACTION,
    P=config.EVAPORATION_PRESSURE_KPA * 1000
)

# H301: Product cooling
H301 = HXutility('H301', ins=E301-0, outs='lactic_acid_product', T=config.PRODUCT_TEMP_C + 273.15)

# =============================================================================
# Create System
# =============================================================================

lactic_acid_sys = bst.System(
    'lactic_acid_sys',
    path=(H101, H102, R201, S301, E301, H301),
    recycle=None
)

print("\nSystem Units:")
for unit in lactic_acid_sys.units:
    print(f"  {unit.ID:6s} - {unit.__class__.__name__}")
print("-"*80)

# =============================================================================
# TEA Class
# =============================================================================

class LacticAcidTEA(bst.TEA):
    """Custom TEA with fixed operating costs and raw materials."""
    
    def _FOC(self, FCI):
        """Fixed operating costs."""
        maintenance = config.MAINTENANCE_FRACTION * FCI
        labor = config.LABOR_COST_ANNUAL
        supervision = config.SUPERVISION_FRACTION * labor
        laboratory = config.LABORATORY_FRACTION * labor
        insurance = config.INSURANCE_FRACTION * FCI
        overhead = config.OVERHEAD_FRACTION * (labor + supervision + maintenance)
        
        return maintenance + labor + supervision + laboratory + insurance + overhead
    
    def _solve_IRR(self):
        """Calculate revenue and solve IRR."""
        product_stream = self.system.flowsheet.stream.lactic_acid_product
        la_production = product_stream.imass['LacticAcid']
        annual_la = la_production * self.operating_hours
        self._sales = annual_la * config.LACTIC_ACID_PRICE
        super()._solve_IRR()

# =============================================================================
# Simulate
# =============================================================================

print("\n" + "="*80)
print("SIMULATING...")
print("="*80)

lactic_acid_sys.simulate()
print("✓ Simulation completed!\n")

# =============================================================================
# Get Key Streams (needed for calculations)
# =============================================================================

product = lactic_acid_sys.flowsheet.stream.lactic_acid_product
feed_glucose = lactic_acid_sys.flowsheet.stream.glucose_feed
broth = lactic_acid_sys.flowsheet.stream.fermentation_broth

# =============================================================================
# Create TEA
# =============================================================================

tea = LacticAcidTEA(
    system=lactic_acid_sys,
    IRR=config.IRR_TARGET,
    duration=(config.PROJECT_START_YEAR, config.PROJECT_END_YEAR),
    depreciation=config.DEPRECIATION,
    income_tax=config.INCOME_TAX_RATE,
    operating_days=config.OPERATING_DAYS,
    lang_factor=config.LANG_FACTOR,
    construction_schedule=config.CONSTRUCTION_SCHEDULE,
    WC_over_FCI=config.WORKING_CAPITAL_FRACTION,
    startup_months=config.STARTUP_MONTHS,
    startup_FOCfrac=config.STARTUP_FOC_FRACTION,
    startup_VOCfrac=config.STARTUP_VOC_FRACTION,
    startup_salesfrac=config.STARTUP_SALES_FRACTION,
    finance_interest=config.FINANCE_INTEREST_RATE,
    finance_years=config.FINANCE_YEARS,
    finance_fraction=config.FINANCE_FRACTION
)

# =============================================================================
# Calculate Operating Costs Manually
# =============================================================================

# Raw material costs (annual)
glucose_cost_annual = feed_glucose.imass['Glucose'] * config.OPERATING_HOURS * config.GLUCOSE_PRICE
nutrients_cost_annual = glucose_cost_annual * 0.05 * config.NUTRIENTS_PRICE / config.GLUCOSE_PRICE

# Utility costs (annual) - from BioSTEAM
utility_cost_annual = tea.utility_cost

# Fixed operating costs (annual) - from TEA
fixed_cost_annual = tea.FOC

# Total operating cost
total_operating_cost = glucose_cost_annual + nutrients_cost_annual + utility_cost_annual + fixed_cost_annual

# =============================================================================
# Display Results
# =============================================================================

# Production metrics
la_production = product.imass['LacticAcid']
annual_production = la_production * config.OPERATING_HOURS / 1000
glucose_consumed = feed_glucose.imass['Glucose'] - broth.imass['Glucose']
# Get actual masses (not molar)
glucose_consumed = feed_glucose.imass['Glucose'] - broth.imass['Glucose']  # kg/hr
la_produced = product.imass['LacticAcid']  # kg/hr

# This should account for biomass and byproducts
overall_yield = la_produced / glucose_consumed if glucose_consumed > 0 else 0

# Also calculate theoretical yield percentage
theoretical_yield = 1.0  # kg LA per kg glucose (stoichiometry)
yield_efficiency = overall_yield / theoretical_yield * 100

print("="*80)
print("PRODUCTION METRICS")
print("="*80)
print(f"Lactic Acid Production:          {la_production:.2f} kg/hr")
print(f"Annual Production:               {annual_production:.2f} MT/year")
print(f"Target Achievement:              {annual_production/config.ANNUAL_PRODUCTION_TARGET*100:.1f}%")
print(f"Product Concentration:           {product.imass['LacticAcid']/product.F_mass*100:.1f}% w/w")
print(f"Fermentation Broth Conc:         {broth.imass['LacticAcid']/broth.F_mass*100:.1f}% w/w")
print(f"Overall Yield:                   {overall_yield:.2f} kg LA/kg glucose ({yield_efficiency:.0f}% of theoretical)")

# Energy
total_heating = sum([u.heat_utilities[0].duty for u in lactic_acid_sys.units 
                     if u.heat_utilities and len(u.heat_utilities) > 0 and u.heat_utilities[0].duty > 0]) / 1e6
total_cooling = sum([abs(u.heat_utilities[0].duty) for u in lactic_acid_sys.units 
                     if u.heat_utilities and len(u.heat_utilities) > 0 and u.heat_utilities[0].duty < 0]) / 1e6
total_power = sum([u.power_utility.consumption for u in lactic_acid_sys.units 
                   if hasattr(u, 'power_utility') and u.power_utility]) / 1e3

print(f"\n{'='*80}")
print("ENERGY REQUIREMENTS")
print("="*80)
print(f"Heating Duty:                    {total_heating:.3f} MW")
print(f"Cooling Duty:                    {total_cooling:.3f} MW")
print(f"Electric Power:                  {total_power:.3f} MW")
if la_production > 0:
    print(f"Specific Energy:                 {total_power*1000/la_production:.2f} kWh/ton LA")

# Economics
print(f"\n{'='*80}")
print("CAPITAL INVESTMENT")
print("="*80)
print(f"Total Capital Investment:        ${tea.TCI/1e6:.2f} million")
print(f"Fixed Capital Investment:        ${tea.FCI/1e6:.2f} million")
print(f"Working Capital:                 ${tea.working_capital/1e6:.2f} million")
if annual_production > 0:
    print(f"Specific Investment:             ${tea.TCI/(annual_production*1000):.2f}/kg annual capacity")

# Equipment costs
print(f"\n{'='*80}")
print("EQUIPMENT COSTS")
print("="*80)
print(f"{'Unit':<10} {'Equipment':<30} {'Purchase ($k)':>15} {'Installed ($k)':>15}")
print("-"*80)
total_purchase = 0
total_installed = 0
for unit in lactic_acid_sys.units:
    if hasattr(unit, 'purchase_cost') and unit.purchase_cost > 0:
        installed = unit.installed_cost if hasattr(unit, 'installed_cost') else unit.purchase_cost * 2.5
        print(f"{unit.ID:<10} {unit.__class__.__name__:<30} "
              f"{unit.purchase_cost/1e3:>15.1f} {installed/1e3:>15.1f}")
        total_purchase += unit.purchase_cost
        total_installed += installed
print("-"*80)
print(f"{'TOTAL':<42} {total_purchase/1e6:>14.2f}M {total_installed/1e6:>14.2f}M")

# Operating costs breakdown
unit_cost = total_operating_cost / (annual_production * 1000) if annual_production > 0 else 0

print(f"\n{'='*80}")
print("ANNUAL OPERATING COSTS")
print("="*80)
print(f"Raw Materials:")
print(f"  Glucose (${config.GLUCOSE_PRICE:.2f}/kg):          ${glucose_cost_annual/1e6:.2f} million/year")
print(f"  Nutrients & pH control:          ${nutrients_cost_annual/1e6:.2f} million/year")
print(f"Utilities (steam, cooling, power): ${utility_cost_annual/1e6:.2f} million/year")
print(f"Fixed costs (labor, maintenance):  ${fixed_cost_annual/1e6:.2f} million/year")
print(f"{'-'*80}")
print(f"Total Annual Operating Cost:       ${total_operating_cost/1e6:.2f} million/year")
print(f"\nUnit Production Cost:              ${unit_cost:.3f}/kg")

# Profitability
annual_revenue = annual_production * 1000 * config.LACTIC_ACID_PRICE
annual_profit = annual_revenue - total_operating_cost
gross_margin = (annual_profit / annual_revenue * 100) if annual_revenue > 0 else 0

# NPV calculation (use actual operating cost)
years = config.PROJECT_END_YEAR - config.PROJECT_START_YEAR
annual_cash_flow = (annual_revenue - total_operating_cost) * (1 - tea.income_tax)
NPV = -tea.TCI
for year in range(1, years + 1):
    NPV += annual_cash_flow / ((1 + tea.IRR) ** year)

# MSP (minimum selling price to achieve target IRR)
# MSP = (Total Operating Cost + Required Return) / Production
required_annual_return = tea.TCI * tea.IRR
min_selling_price = (total_operating_cost + required_annual_return) / (annual_production * 1000)

print(f"\n{'='*80}")
print(f"PROJECT ECONOMICS (LA price: ${config.LACTIC_ACID_PRICE:.2f}/kg)")
print("="*80)
print(f"Annual Revenue:                  ${annual_revenue/1e6:.2f} million")
print(f"Annual Profit (before tax):      ${annual_profit/1e6:.2f} million")
print(f"Gross Margin:                    {gross_margin:.1f}%")
print(f"\nMinimum Selling Price (MSP):     ${min_selling_price:.3f}/kg")
print(f"Net Present Value (NPV):         ${NPV/1e6:.2f} million")
print(f"Internal Rate of Return (IRR):   {tea.IRR*100:.2f}%")

if annual_profit > 0:
    simple_payback = tea.TCI / annual_profit if annual_profit > 0 else 0
    print(f"Simple Payback Period:           {simple_payback:.2f} years")

print(f"\n{'='*80}")
print("KEY PERFORMANCE INDICATORS")
print("="*80)
print(f"Production Capacity:             {config.ANNUAL_PRODUCTION_TARGET:,} MT/year")
print(f"Capacity Utilization:            {config.OPERATING_DAYS/365*100:.1f}%")
print(f"Glucose-to-LA Yield:             {overall_yield:.2f} kg/kg ({overall_yield/1.0*100:.0f}% theoretical)")
print(f"Product Concentration:           {product.imass['LacticAcid']/product.F_mass*100:.0f}% w/w")
if la_production > 0:
    # FIX: Convert MW to kW, then divide by tons/hr (not kg/hr)
    print(f"Energy Intensity:                {(total_power*1000)/(la_production/1000):.1f} kWh/ton LA")
if annual_production > 0:
    # FIX: TCI is already in dollars, divide by MT (not kg)
    print(f"CAPEX per Annual Ton:            ${tea.TCI/(annual_production):.0f}/ton")
print(f"OPEX per kg LA:                  ${unit_cost:.2f}/kg")
print(f"Profit Margin:                   {gross_margin:.1f}%")
print(f"ROI (IRR):                       {tea.IRR*100:.1f}%")
print(f"NPV (20 years):                  ${NPV/1e6:.1f} million")

print(f"\n{'='*80}")
print("SIMULATION COMPLETE")
print("="*80)
print(f"\n✓ Process: Glucose → Lactic Acid ({config.ANNUAL_PRODUCTION_TARGET:,} MT/year)")
print(f"✓ Economics: NPV = ${NPV/1e6:.1f}M, IRR = {tea.IRR*100:.1f}%, MSP = ${min_selling_price:.2f}/kg")
print("="*80 + "\n")