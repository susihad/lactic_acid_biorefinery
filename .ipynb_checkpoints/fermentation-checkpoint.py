"""
Lactic acid fermentation reactor.

Simple custom BioSTEAM unit for glucose → lactic acid fermentation.
"""

import biosteam as bst
import numpy as np


class LacticAcidFermentation(bst.Unit):
    """
    Fermentation reactor for lactic acid production.
    
    Reaction: C6H12O6 → 2 C3H6O3 (Glucose → Lactic Acid)
    
    Parameters
    ----------
    tau : float
        Fermentation time (hours)
    conversion : float
        Glucose conversion efficiency (0-1)
    biomass_yield : float
        g biomass / g glucose
    """
    
    _N_ins = 1  # One inlet
    _N_outs = 1  # One outlet
    _units = {'Reactor volume': 'm3', 'Number of reactors': ''}
    
    def __init__(self, ID='', ins=(), outs=(), tau=48, conversion=0.90, biomass_yield=0.08):
        super().__init__(ID, ins, outs)
        self.tau = tau
        self.conversion = conversion
        self.biomass_yield = biomass_yield
        
    def _run(self):
        """Calculate mass balance."""
        feed = self.ins[0]
        broth = self.outs[0]
        
        # Start with feed composition
        broth.copy_flow(feed)
        
        # Glucose consumption
        glucose_reacted = feed.imol['Glucose'] * self.conversion
        
        # Products
        lactic_acid_produced = glucose_reacted * 2  # 1 glucose → 2 lactic acid
        
        # Biomass
        glucose_mass_reacted = glucose_reacted * 180  # MW glucose = 180
        biomass_mass = glucose_mass_reacted * self.biomass_yield
        biomass_produced = biomass_mass / 25  # Assume MW=25 for biomass
        
        # Byproduct ethanol (~2%)
        ethanol_produced = glucose_reacted * 0.02
        
        # Update broth composition
        broth.imol['Glucose'] -= glucose_reacted
        broth.imol['LacticAcid'] += lactic_acid_produced
        broth.imol['WWTsludge'] += biomass_produced
        broth.imol['Ethanol'] += ethanol_produced
        
        # Set conditions
        broth.T = 37 + 273.15  # 37°C
        broth.P = feed.P
        
    def _design(self):
        """Size equipment."""
        broth = self.outs[0]
        
        # Total volume = Flow rate × Residence time
        total_volume = broth.F_vol * self.tau
        
        # Use 100 m³ reactors
        reactor_size = 100
        n_reactors = np.ceil(total_volume / reactor_size)
        
        self.design_results['Reactor volume'] = total_volume
        self.design_results['Number of reactors'] = n_reactors
        
    def _cost(self):
        """Calculate costs."""
        V = self.design_results['Reactor volume']
        n = self.design_results['Number of reactors']
        
        V_per_reactor = V / n if n > 0 else V
        
        # Six-tenths rule scaling
        base_cost = 200000  # $ for 100 m³
        unit_cost = base_cost * (V_per_reactor / 100)**0.65
        total_purchase = unit_cost * n
        
        # Store costs
        self.baseline_purchase_costs['Fermentation reactors'] = total_purchase
        self.purchase_costs['Fermentation reactors'] = total_purchase
        self.installed_costs['Fermentation reactors'] = total_purchase * 2.8