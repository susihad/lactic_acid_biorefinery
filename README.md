# Lactic Acid Biorefinery - BioSTEAM Simulation

**Techno-Economic Analysis of Lactic Acid Production from Glucose**

Author: Susila Hadiyati  
Date: October 2025

## Overview

This project uses **BioSTEAM** to simulate and analyze a 50,000 MT/year lactic acid biorefinery.

**Process:** Glucose → Lactic Acid via *Lactobacillus* fermentation

**What's included:**
- Complete process simulation (fermentation, separation, evaporation)
- Custom unit operations for fermentation and evaporation
- Techno-economic analysis (capital costs, operating costs, profitability)
- Clean, modular code structure

## Installation

```bash
# Install dependencies
pip install biosteam thermosteam numpy matplotlib

# Or use requirements.txt
pip install -r requirements.txt
```

## Quick Start

```bash
# Run the simulation
python run_simulation.py
```

That's it! Results will print to console.

## Project Structure

```
lactic_acid_biorefinery/
├── config.py              # All process parameters
├── units/                 # Custom unit operations
│   ├── fermentation.py    # Fermentation reactor
│   └── evaporation.py     # Vacuum evaporator
└── run_simulation.py      # Main simulation script
```

## Modifying Parameters

Edit `config.py` to change:
- Production capacity
- Fermentation conditions (temperature, time, conversion)
- Economic assumptions (prices, IRR target)

Example:
```python
# In config.py
ANNUAL_PRODUCTION_TARGET = 100000  # Change to 100,000 MT/year
GLUCOSE_PRICE = 0.30              # Change glucose price
FERMENTATION_TIME = 36            # Reduce fermentation time
```

## Understanding the Code

### 1. Configuration (`config.py`)
All parameters in one place - easy to modify without touching simulation code.

### 2. Custom Units (`units/`)
Two custom BioSTEAM units:
- **Fermentation:** Converts glucose to lactic acid with Lactobacillus
- **Evaporation:** Concentrates product by removing water

### 3. Main Simulation (`run_simulation.py`)
Puts everything together:
1. Setup chemicals and flowsheet
2. Create feed streams
3. Connect unit operations
4. Run simulation
5. Calculate economics
6. Display results

## Key Results

The simulation calculates:
- **Mass balances:** Production rates, yields, concentrations
- **Energy requirements:** Heating, cooling, electricity
- **Capital costs:** Equipment purchase and installation
- **Operating costs:** Raw materials, utilities, labor
- **Profitability:** NPV, IRR, minimum selling price