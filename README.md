# India Female Population Projections 1991–2100

Annual female population time series for **India and all 37 States/UTs**, spanning 1991–2100, broken into 16 NDMC age bands. Built from Census anchor years, NDMC state-level projections, and WPP-calibrated long-run projections.

---

## Quick Start

```bash
git clone https://github.com/<your-username>/india-female-pop-projections.git
cd india-female-pop-projections
pip install -r requirements.txt
python notebooks/generate_notebook.py      # regenerates the .ipynb
jupyter notebook notebooks/India_Female_Population_1991_2100.ipynb
# Run All Cells — output Excel files appear in output/
```

---

## Repository Structure

```
india-female-pop-projections/
├── data/
│   ├── wpp/
│   │   └── India_Population_TimeSeries_Female.csv   # UN WPP 2022 single-year data
│   ├── census/
│   │   └── Census_Master_AgeSex_1991_2001_2011.xlsx # Census 1991/2001/2011 age-sex tables
│   └── ndmc/
│       └── Statewise Population-NDMC.xlsx           # NDMC state-level 5-year projections 2012–2036
├── notebooks/
│   ├── generate_notebook.py                         # script to (re)generate the .ipynb
│   └── India_Female_Population_1991_2100.ipynb      # main analysis notebook
├── output/                                          # created by notebook at runtime
│   ├── India_Female_AgeBands_1991_2100.xlsx
│   ├── Combined_All_States_1991_2100.xlsx
│   └── States/
│       └── <State>.xlsx  (37 files)
├── requirements.txt
└── README.md
```

---

## Methodology A — Three-Segment Pipeline

### Segment 1: Census Anchor Years + Linear Interpolation (1991–2011)

Census 1991, 2001, and 2011 provide decadal female population by 5-year age group. Between census years, each age band is linearly interpolated year-by-year:

$$P(\text{band},\, t) = P(\text{band},\, t_0) + \frac{t - t_0}{t_1 - t_0}\bigl[P(\text{band},\, t_1) - P(\text{band},\, t_0)\bigr]$$

Census age bands (`0-4`, `5-9`, …, `75-79`, `80+`) are mapped to NDMC bands, with `75-79` and `80+` merged into `75+`.

### Segment 2: NDMC Actual Projections (2012–2036)

The NDMC (*National Commission on Population*) published state-level female population projections in 5-year steps (2012, 2017, 2022, 2027, 2032, 2036). These are linearly interpolated to annual values.

**Bifurcated states** — states created after 2000 lack their own 2001 Census data; the following split ratios are applied:

| New State | Parent State | Split Data Source |
|-----------|-------------|------------------|
| Jharkhand | Bihar | NDMC 2001 ratio |
| Chhattisgarh | Madhya Pradesh | NDMC 2001 ratio |
| Uttarakhand | Uttar Pradesh | NDMC 2001 ratio |
| Telangana | Andhra Pradesh | NDMC 2012 ratio |
| Ladakh | Jammu & Kashmir | NDMC 2012 ratio |

### Segment 3: Long-Run Projections — Approach B (2037–2100)

#### WPP Scaling Factor

For each age band $x$ and year $t$:

$$\rho(x,\, t) = \frac{P_{\text{WPP}}(x,\, t)}{P_{\text{WPP}}(x,\, 2036)}$$

This captures how UN WPP 2022 projects each band's *relative* trajectory from the 2036 base.

#### Gompertz TFR Curve

Total Fertility Rate is modelled with a Gompertz decline:

$$\text{TFR}(t) = L + (U - L)\cdot a^{\,b^{(t-2010)}}$$

Parameters ($L=1.667$, $U=2.5$, $a$, $b$) are fitted to Census SRS / Sample Registration System data. TFR at 2036 provides the base:

$$\text{TFR}_{2036} = \text{TFR}(2036)$$

#### Approach B Formula

$$P_B(\text{band},\, t) = P_{\text{NDMC}}(\text{band},\, 2036)\;\times\;\rho(\text{band},\, t)\;\times\;\left(\frac{\text{TFR}(t)}{\text{TFR}_{2036}}\right)^{0.3}$$

The exponent 0.3 dampens the fertility adjustment — most of the long-run dynamics are captured by the WPP scaling factor.

#### Blending Window (2037–2046)

A 10-year linear blend transitions from NDMC momentum to Approach B, avoiding discontinuities at 2036:

$$\alpha(t) = \frac{t - 2036}{10}, \quad t \in [2037,\,2046]$$

$$P(\text{band},\, t) = (1-\alpha)\,P_{\text{mom}}(t) + \alpha\,P_B(\text{band},\, t)$$

where $P_{\text{mom}}(t) = P(t-1)\cdot(1 + r_{\text{NDMC}})$ continues the NDMC growth rate.

After 2046, the series scales to Approach B with a continuity correction:

$$P(\text{band},\, t) = P_B(\text{band},\, t)\;\times\;\frac{P(2046)}{P_B(2046)}, \quad t > 2046$$

---

## Age Bands

All 16 NDMC age bands are produced:

`00-04` · `05-09` · `10-14` · `15-17` · `18-19` · `20-24` · `25-29` · `30-34` · `35-39` · `40-44` · `45-49` · `50-54` · `55-59` · `60-64` · `65-74` · `75+`

---

## Data Sources

| Dataset | Source | Years |
|---------|--------|-------|
| UN World Population Prospects 2022 | [UNDESA WPP](https://population.un.org/wpp/) | 1950–2100 |
| Census of India (Age × Sex tables) | Office of the Registrar General, India | 1991, 2001, 2011 |
| NDMC State-level Projections | National Commission on Population, MoHFW | 2012–2036 |
| SRS Statistical Report 2022 | Office of the Registrar General, India | TFR/ASFR inputs |

---

## Output Format

Each Excel file (India + 37 state files + combined file) has columns:

| Year | 00-04 | 05-09 | 10-14 | 15-17 | 18-19 | 20-24 | … | 75+ | Total |
|------|-------|-------|-------|-------|-------|-------|---|-----|-------|
| 1991 | … | … | … | … | … | … | … | … | … |
| … | | | | | | | | | |
| 2100 | … | … | … | … | … | … | … | … | … |

All values are **female population in thousands**.

---

## Citation

If you use this dataset or methodology, please cite:

> Bhat, N. et al. (2026). *India Female Population Projections 1991–2100: Methodology A.* GitHub repository. https://github.com/<your-username>/india-female-pop-projections

---

## License

MIT License. Data from government and UN sources retain their original terms of use.
