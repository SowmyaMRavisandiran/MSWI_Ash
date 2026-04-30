# MSWI Ash – MSW Incineration Ash Estimation Model

Estimation of MSWI (Municipal Solid Waste Incineration) ash bulk quantities for past trends and future projections, including three scenarios: BAU (Business As Usual), REC (Recycling), and CIR (Circular Economy).

**Citation:** DOI: 10.5281/zenodo.17423053

---

## Project Overview

This repository contains a data-driven model for estimating and projecting municipal solid waste incineration ash composition and quantities. The project combines elemental composition data extracted from PDF sources with MSW generation projections to estimate future ash quantities under different waste management scenarios.

---

## Project Structure

### 📁 `model/` – Analysis & Processing Notebooks

**Phase 1: Data Extraction & Processing**
- **1.1 msw_data_processing.ipynb** – Load and clean core MSW generation data
- **1.2 elemental_data.ipynb** – Extract and organize elemental composition data
- **1.3 msw_composition_data.ipynb** – Process MSW waste fraction composition data
- **1.4 elemental_data_2.ipynb** – Advanced elemental data extraction from PDFs

**Phase 2: Scenario Modeling**
- **2.1 BAU_projections.ipynb** – Business-as-usual waste generation projections
- **2.2 scenarios.ipynb** – Compare and model REC and CIR scenarios

**Phase 3: Visualization & Output**
- **3.1 plot.ipynb** – Generate standard analytical plots
- **3.2 plot_final.ipynb** – Create publication-ready visualizations
- **plotting_sample_msw_composition.ipynb** – Visualize MSW composition by fraction

**Utilities**
- **functions.py** – Core model functions and calculations
- **plot.py** – Plotting helper functions
- **plot_final.py** – Final visualization output functions
- **trade_balance.ipynb** – Analysis of waste trade flows

**Supporting Scripts**
- **futuram_formatting/** – Data formatting for FutuRaM project outputs
  - futuram_obs_ash_gen.ipynb
  - futuram_scenarios.ipynb

### 📁 `data/` – Input & Output Data

**external/** – Raw source data
- `msw_oecd.csv` – OECD MSW statistics
- `env_wasgen_linear_*.csv` – Environmental waste generation data
- `locationNUTS-0.csv` – NUTS region classifications
- `country_sample.csv` – Country sample selection
- `elemental_data_gotze.xlsx` – Elemental composition reference (Götze et al.)
- **Population/** – World Bank population projections & historical data
- **GDP/** – OECD GDP data (current and projections)

**processed/** – Cleaned & processed data
- `EU_MSW_Cleaned_Data.csv` – Standardized EU MSW data
- `EU_MSW_percap_Cleaned.csv` – Per capita MSW data
- `elemental_data_gotze.csv` – Processed elemental composition
- `categories_msw_composition.csv` – MSW waste fraction categories
- `eu_gdp_percap_projections_cleaned.csv` – GDP per capita projections
- `eu_population_projections_cleaned.csv` – Population projections
- `inc_proj_parameters.csv` – Income projection model parameters
- `MSW_TCs.csv` – Transfer coefficients for waste flows

**results/** – Model outputs
- `ALL_Scenarios.csv` – Combined results across all scenarios
- `BAU_MSW.csv`, `REC_MSW.csv`, `CIR_MSW.csv` – Scenario-specific MSW projections
- `EU_BAU_2022.csv` – EU base year 2022 data
- **FutuRaM/** – Project-specific output format

### 📁 `plots/` – Generated Visualizations

- `eu27_plus4_map.html` – Interactive regional map
- `msw_gen_plots/` – MSW generation trends
- `msw_gen_projections/` – Projected generation by scenario
- `msw_bau_model/` – BAU scenario analysis plots
- `treatment_plots/` – Waste treatment flow diagrams
- `energy_recovery_plots/` – Energy recovery analysis
- `Incineration_projections/` – MSWI-specific trends

### 📁 `archive/` – Legacy Code & Earlier Versions

Historical notebooks and functions for reference (see version history for details).

---

## Key Workflow

1. **Data Extraction** (Notebooks 1.1–1.4)
   - Extract MSW volumes, composition, and elemental content from multiple sources
   - Parse PDF tables for elemental concentration ranges
   - Clean and standardize country/region data

2. **Data Processing** (functions.py)
   - Match elemental data to waste fractions
   - Calculate per capita metrics
   - Normalize units and handle missing values

3. **Scenario Modeling** (Notebooks 2.1–2.2)
   - Project MSW generation using GDP/population drivers
   - Apply scenario-specific waste composition adjustments
   - Calculate MSWI ash quantity and composition

4. **Visualization & Output** (Notebooks 3.1–3.2)
   - Generate time-series plots for each scenario
   - Create regional comparison maps
   - Export results in FutuRaM format

---

## Scenarios

- **BAU (Business As Usual)** – Baseline trend projections with no policy change
- **REC (Recycling)** – Increased material recovery reducing incineration waste
- **CIR (Circular Economy)** – Maximum recovery and waste prevention scenario

---

## Data Sources

- **MSW Data:** OECD, Eurostat, national waste management statistics
- **Elemental Composition:** Götze et al. reference data (see citations)
- **Projections:** World Bank (population), OECD (GDP)
- **Regional Classifications:** NUTS nomenclature

---

## Requirements

- Python 3.7+
- pandas, numpy, matplotlib, plotly
- pdfplumber (for PDF data extraction)
- See individual notebooks for additional dependencies

---

## Usage

1. Clone the repository and navigate to the `model/` folder
2. Run notebooks in order: 1.1 → 1.2 → 1.3 (or 1.4) → 2.1 → 2.2 → 3.1/3.2
3. Adjust paths and parameters in notebook headers as needed
4. Outputs are saved to `data/processed/` and `plots/`

---

## License & Citation

Please cite this work as:

```bibtex
@dataset{mswi_ash_model,
  title={MSWI Ash Quantity and Composition Model},
  author={[Your Name/Organization]},
  doi={10.5281/zenodo.17423053}
}
```

---

## Notes

- Some notebooks are designed for specific analyses (e.g., FutuRaM output formatting)
- Elemental data extraction from PDFs may require manual review for accuracy
- Large datasets in `data/external/` are ignored by Git; see `.gitignore` for details
