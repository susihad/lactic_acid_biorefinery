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
        
        # Glucose consumption (molar basis)
        glucose_reacted = feed.imol['Glucose'] * self.conversion
        
        # Convert to mass for distribution
        glucose_mass_reacted = glucose_reacted * 180  # kg/hr
        
        # Distribute glucose carbon to products (mass basis)
        # Total should equal glucose_mass_reacted for mass balance
        
        # Biomass: 8% of glucose mass
        biomass_mass = glucose_mass_reacted * self.biomass_yield  # 8% = 0.08
        biomass_produced = biomass_mass / 25  # kmol/hr (assume MW=25)
        
        # Ethanol: 2% of glucose mass (byproduct)
        ethanol_mass = glucose_mass_reacted * 0.02  # 2%
        ethanol_produced = ethanol_mass / 46  # kmol/hr (MW ethanol = 46)
        
        # Lactic acid: Remaining glucose (90%)
        # This is the key fix: don't use stoichiometry directly
        la_fraction = 1.0 - self.biomass_yield - 0.02  # 1.0 - 0.08 - 0.02 = 0.90
        lactic_acid_mass = glucose_mass_reacted * la_fraction  # 90%
        lactic_acid_produced = lactic_acid_mass / 90  # kmol/hr (MW LA = 90)
        
        # Update broth composition
        broth.imol['Glucose'] -= glucose_reacted
        broth.imol['LacticAcid'] += lactic_acid_produced
        broth.imol['WWTsludge'] += biomass_produced
        broth.imol['Ethanol'] += ethanol_produced
        
        # Set conditions
        broth.T = 37 + 273.15
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