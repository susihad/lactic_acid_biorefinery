"""
Vacuum evaporator for concentrating lactic acid.
Simple custom BioSTEAM unit for water removal under vacuum.
"""
import biosteam as bst


class LacticAcidEvaporator(bst.Unit):
    """
    Vacuum evaporator to concentrate lactic acid solution.
    
    Removes water under vacuum to concentrate product from ~10% to ~25-50%.
    
    Parameters
    ----------
    V : float
        Fraction of water to evaporate (0-1)
    P : float
        Operating pressure (Pa)
    """
    
    _N_ins = 1  # Feed
    _N_outs = 2  # Concentrate and vapor
    _units = {'Evaporator volume': 'm3', 'Heat transfer area': 'm2'}
    
    def __init__(self, ID='', ins=(), outs=(), V=0.70, P=20000):
        super().__init__(ID, ins, outs)
        self.V = V  # Fraction of water to remove
        self.P = P  # Vacuum pressure
        
    def _run(self):
        """Calculate mass balance."""
        feed = self.ins[0]
        concentrate = self.outs[0]
        vapor = self.outs[1]
        
        # Water evaporation
        water_evaporated = feed.imol['Water'] * self.V
        
        # Concentrate (liquid product)
        concentrate.copy_flow(feed)
        concentrate.imol['Water'] -= water_evaporated
        concentrate.T = 80 + 273.15
        concentrate.P = self.P
        concentrate.phase = 'l'
        
        # Vapor (water)
        vapor.empty()
        vapor.imol['Water'] = water_evaporated
        vapor.T = 80 + 273.15
        vapor.P = self.P
        vapor.phase = 'g'
        
    def _design(self):
        """Size equipment."""
        feed = self.ins[0]
        
        # Volume (2 hour residence time)
        self.design_results['Evaporator volume'] = feed.F_vol * 2
        
        # Heat transfer area
        water_evap = self.outs[1].imol['Water']
        Hvap = 40.66  # kJ/mol
        Q = water_evap * Hvap * 1000 / 3600  # kW
        
        U = 0.5  # kW/m²/K
        LMTD = 30  # K
        A = Q / (U * LMTD) if LMTD > 0 else 0
        
        self.design_results['Heat transfer area'] = A
        
        # FIXED: Store Q for use in heat utilities
        self._evaporation_duty = Q
        
    def _cost(self):
        """Calculate costs."""
        V = self.design_results['Evaporator volume']
        A = self.design_results['Heat transfer area']
        
        # Vessel cost
        vessel_cost = 80000 * (V / 50)**0.6 if V > 0 else 0
        
        # Heat exchanger cost
        hx_cost = 15000 * (A / 100)**0.65 if A > 0 else 0
        
        total_purchase = vessel_cost + hx_cost
        
        self.baseline_purchase_costs['Evaporator'] = total_purchase
        self.purchase_costs['Evaporator'] = total_purchase
        self.installed_costs['Evaporator'] = total_purchase * 3.2
        
        # FIXED: Add heat utility properly
        # Create heat utility for steam (heating)
        hu = bst.HeatUtility()
        hu.load_agent(bst.UtilityAgent('low_pressure_steam'))
        hu(self._evaporation_duty, 150 + 273.15)  # kW at 150°C
        self.heat_utilities = (hu,)