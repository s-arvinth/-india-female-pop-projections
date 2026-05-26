"""Generate India_Female_Population_1991_2100.ipynb — Methodology A clean notebook."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb.metadata = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.9.0"},
}
cells = []

# ─────────────────────────────────────────────────────────────────────────────
# CELL 0 — Title
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
# India Female Population Time Series: 1991–2100
### All 37 States/UTs · 16 Five-Year Age Bands · Annual Resolution

**Methodology A** — a reproducible pipeline that assembles a continuous demographic
time series for India and every state/UT from three authoritative sources, then
extends projections to 2100 using demographically-calibrated models.

---

## Quick Start
```bash
git clone https://github.com/<your-org>/india-female-pop-projections
cd india-female-pop-projections
pip install -r requirements.txt
jupyter notebook notebooks/India_Female_Population_1991_2100.ipynb
```
Run all cells top-to-bottom. Outputs are written to `output/`.

---

## Output files
| File | Contents |
|---|---|
| `output/India_Female_AgeBands_1991_2100.xlsx` | India total — 16 bands × 110 years |
| `output/States/` | 37 individual state Excel files |
| `output/Combined_All_States_1991_2100.xlsx` | All states in one sheet (long format) |
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 1 — Methodology Overview
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Methodology A — Overview

The time series is assembled from **three source segments**:

| Period | Source | How used |
|---|---|---|
| 1991 · 2001 · 2011 | Census of India (Master Age-Sex file) | Anchor points; linear interpolation fills in-between years |
| 2012–2036 | NDMC female projections (NCDIR, 2021) | Actual demographic projections; used as-is |
| 2037–2100 | **Approach B** — Gompertz/Logistic + WPP 2024 | Age-band growth rates anchored to NDMC 2036, adjusted by TFR correction |

### Why three sources?
- **Census** is the gold standard for inter-censal benchmarks but only available at 10-year intervals.
- **NDMC** provides the most India-specific age-structure projections to 2036, using the
  Cohort Component Method with SRS fertility and Coale-Demeny West life tables.
- **WPP 2024** extends demographic dynamics to 2100 using globally consistent scenarios,
  providing age-specific growth trajectories.

### Blending window (2037–2046)
To avoid a sharp inflection at 2036, a 10-year linear blending window smooths the
transition from NDMC's momentum to Approach B's trajectory.
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 2 — Mathematical Framework
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(r"""\
## Mathematical Framework

### Age bands
All projections use the 16 five-year age bands from the NDMC file:
`00-04, 05-09, 10-14, 15-19, 20-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50-54, 55-59, 60-64, 65-69, 70-74, 75+`

---

### Segment 1 — Census Period (1991–2011): Linear Interpolation

For each state $s$ and age band $x$, let $C(s, x, y_k)$ be the census count at anchor
year $y_k \in \{1991, 2001, 2011\}$. For any intermediate year $y \in [y_k, y_{k+1}]$:

$$P(s, x, y) = C(s, x, y_k) + \frac{y - y_k}{y_{k+1} - y_k}
  \bigl[C(s, x, y_{k+1}) - C(s, x, y_k)\bigr]$$

---

### Segment 2 — NDMC Actual (2012–2036)

$$P(s, x, y) = \text{NDMC}(s, x, y) \qquad y \in [2012, 2036]$$

Values from the NCDIR *Statewise Population-NDMC.xlsx* female sheet.

---

### Segment 3 — Approach B Projection (2037–2100)

**Step 1 — WPP growth ratio** for band $x$ at year $y$:

$$\rho(x, y) = \frac{\text{WPP}(x, y)}{\text{WPP}(x, 2036)}$$

WPP values are summed from single-age columns of the UN WPP 2024 India female CSV.

**Step 2 — TFR correction factor** (Gompertz curve, damped):

$$\text{TFR\_factor}(y) = \left(\frac{\text{TFR}_B(y)}{\text{TFR}_B(2036)}\right)^{0.3}$$

where $\text{TFR}_B(y) = L + (U - L) \cdot a^{b^{(y-2010)}}$ (Gompertz) with parameters
fitted to Census 2019 Statement 3 data ($L = 1.667$, $U = 2.5$).

**Step 3 — Approach B projection** for year $y \geq 2047$:

$$\boxed{P_B(s, x, y) = \text{NDMC}(s, x, 2036) \times \rho(x, y) \times \text{TFR\_factor}(y)}$$

**Step 4 — Blending window** for $y \in [2037, 2046]$:

Let $\alpha(y) = (y - 2036)/10$ (rises linearly from 0 to 1).

The NDMC momentum is the population that would result from continuing NDMC's own 2031–36 CAGR:

$$P_{\text{mom}}(s, x, y) = P(s, x, y-1) \times (1 + r_{\text{NDMC}}(s, x))$$

$$\boxed{P(s, x, y) = (1 - \alpha) \cdot P_{\text{mom}}(s, x, y) + \alpha \cdot P_B(s, x, y)}$$

After 2046, Approach B is used purely, but scaled to ensure continuity at 2046:

$$P(s, x, y) = P_B(s, x, y) \times \frac{P(s, x, 2046)}{P_B(s, x, 2046)}$$

---

### Gompertz TFR curve (Approach B parameters)

$$\text{TFR}(y) = L + (U - L) \cdot a^{b^{(y-2010)}}$$

| Parameter | Value | Source |
|---|---|---|
| $L$ (lower asymptote) | 1.667 | Census 2019 Statement 3 long-run projection |
| $U$ (upper bound) | 2.50 | SRS 2009–11 baseline TFR |
| $a$, $b$ | fitted | Minimised residuals vs Census 5-period TFR values |

---

### Bifurcated state handling

States that came into existence after 1991 have no census records for earlier years.
Population for those years is estimated using NDMC 2012 split ratios applied to the
parent state's census values:

| New state | Parent state | First census year | Method |
|---|---|---|---|
| Jharkhand | Bihar | 2001 | 2001 NDMC split ratio × Bihar 1991 census |
| Chhattisgarh | Madhya Pradesh | 2001 | Same |
| Uttarakhand | Uttar Pradesh | 2001 | Same |
| Telangana | Andhra Pradesh | 2014 | NDMC 2012 split ratio × AP census for all years |
| Ladakh | Jammu & Kashmir | 2019 | NDMC 2012 split ratio × J&K census; 1991 back-extrapolated |
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 3 — Imports & Paths
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""\
import warnings; warnings.filterwarnings('ignore')
import os, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy.optimize import minimize

# ── Resolve paths relative to this notebook ──────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.abspath("__file__"))   # notebooks/
REPO_ROOT = os.path.normpath(os.path.join(REPO_ROOT, ".."))

WPP_CSV    = os.path.join(REPO_ROOT, "data", "wpp",    "India_Population_TimeSeries_Female.csv")
CENSUS_XL  = os.path.join(REPO_ROOT, "data", "census", "Census_Master_AgeSex_1991_2001_2011.xlsx")
NDMC_XL    = os.path.join(REPO_ROOT, "data", "ndmc",   "Statewise Population-NDMC.xlsx")
OUT_DIR    = os.path.join(REPO_ROOT, "output")
STATES_DIR = os.path.join(OUT_DIR, "States")
os.makedirs(STATES_DIR, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────
# 16 NDMC age bands (canonical names used throughout)
BANDS = ['00-04','05-09','10-14','15-19','20-24','25-29',
         '30-34','35-39','40-44','45-49','50-54','55-59',
         '60-64','65-69','70-74','75+']

CENSUS_YEARS  = [1991, 2001, 2011]
NDMC_YEARS    = list(range(2012, 2037))
PROJ_YEARS    = list(range(2037, 2101))
ALL_YEARS     = list(range(1991, 2101))

T_BLEND = 10   # blending window length (years)

plt.rcParams.update({
    "figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False,
})
print("Setup complete.  Repo root:", REPO_ROOT)
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 4 — Section header
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 1: Data Loading

Three files are read:
1. **WPP 2024 CSV** — India female single-age population 1950–2101 (UN World Population Prospects)
2. **NDMC Excel** — State-wise female population by 5-year age band, 2012–2036
3. **Census Master Excel** — Age-sex distribution for all states, census years 1991/2001/2011
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 5 — Load WPP
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""\
# ── 1A. WPP 2024: India female single-age, 1991–2100 ─────────────────────────
wpp_raw = pd.read_csv(WPP_CSV).rename(columns={"Time": "Year"})
wpp_raw = wpp_raw[wpp_raw["Year"].between(1991, 2100)].set_index("Year")

age_cols = [c for c in wpp_raw.columns if c.startswith("Age")]

# Aggregate single ages into 16 NDMC-compatible 5-year bands
BAND_AGES = {
    "00-04": range(0,   5),  "05-09": range(5,  10),
    "10-14": range(10, 15),  "15-19": range(15, 20),
    "20-24": range(20, 25),  "25-29": range(25, 30),
    "30-34": range(30, 35),  "35-39": range(35, 40),
    "40-44": range(40, 45),  "45-49": range(45, 50),
    "50-54": range(50, 55),  "55-59": range(55, 60),
    "60-64": range(60, 65),  "65-69": range(65, 70),
    "70-74": range(70, 75),  "75+":   range(75, 101),
}

wpp_bands = pd.DataFrame(index=wpp_raw.index)
for band, ages in BAND_AGES.items():
    cols = [f"Age{a}" if a < 100 else "Age100+" for a in ages]
    cols = [c for c in cols if c in wpp_raw.columns]
    wpp_bands[band] = wpp_raw[cols].sum(axis=1) / 1e3   # thousands → millions

# WPP scaling factors relative to 2036 (used for post-2036 projections)
wpp_sf = wpp_bands.div(wpp_bands.loc[2036])   # ratio = 1.0 at 2036

print("WPP loaded:")
print(f"  Years: {wpp_raw.index.min()}–{wpp_raw.index.max()}")
print(f"  India female total 2036: {wpp_bands.loc[2036].sum():.2f} M")
print(f"  India female total 2100: {wpp_bands.loc[2100].sum():.2f} M")
wpp_sf.loc[[2036, 2050, 2070, 2100], ["00-04","20-24","45-49","75+"]].round(4)
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 6 — Load NDMC
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""\
# ── 1B. NDMC: state-wise female population 2012–2036 ─────────────────────────
ndmc_raw = pd.read_excel(NDMC_XL, sheet_name="Female", header=0)
ndmc_raw.rename(columns={"Population": "State"}, inplace=True)
ndmc_raw["Year"] = ndmc_raw["Year"].astype(int)

STATES = sorted(ndmc_raw["State"].unique().tolist())

# India: sum all 37 states
ndmc_india = ndmc_raw.groupby("Year")[BANDS].sum() / 1e6   # absolute → millions

print(f"NDMC loaded: {len(STATES)} states, years {ndmc_raw['Year'].min()}–{ndmc_raw['Year'].max()}")
print(f"India female total at 2036: {ndmc_india.loc[2036].sum():.2f} M")
print(f"States: {', '.join(STATES[:6])}, ...")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 7 — Load Census Master
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""\
# ── 1C. Census Master: age-sex distribution 1991/2001/2011 ───────────────────
cen_raw = pd.read_excel(CENSUS_XL, sheet_name="Master_Long")

# Normalise state names to match NDMC canonical names
NAME_FIX = {
    "Andaman And Nicobar Islands": "Andaman & Nicobar",
    "Dadra And Nagar Haveli":      "Dadra & Nagar Haveli",
    "Daman And Diu":               "Daman & Diu",
    "NCT OF DELHI":                "Delhi",
}
cen_raw["State"] = cen_raw["State"].replace(NAME_FIX)

# Census age band → NDMC band mapping (combine 75-79 and 80+ into 75+)
CEN_TO_NDMC = {
    "00-04":"00-04","05-09":"05-09","10-14":"10-14","15-19":"15-19",
    "20-24":"20-24","25-29":"25-29","30-34":"30-34","35-39":"35-39",
    "40-44":"40-44","45-49":"45-49","50-54":"50-54","55-59":"55-59",
    "60-64":"60-64","65-69":"65-69","70-74":"70-74",
    "75-79":"75+",  "80+":  "75+",
    # older-format labels
    "0-4":"00-04",  "5-9":"05-09",  "75-79":"75+",
}

def build_state_census(df_state):
    \"\"\"Aggregate census rows for one state-year into NDMC-band dict.\"\"\"
    out = {b: 0.0 for b in BANDS}
    for _, row in df_state.iterrows():
        ndmc_b = CEN_TO_NDMC.get(str(row["AgeGroup"]).strip())
        if ndmc_b:
            out[ndmc_b] += float(row.get("TotalFemales", 0) or 0)
    return out

# Build census_bands[state][year][band] in ABSOLUTE values
census_bands = {}
for (state, year), grp in cen_raw.groupby(["State", "Year"]):
    if "India" in str(state):
        continue
    census_bands.setdefault(state, {})[year] = build_state_census(grp)

# India: handle 1991 special name
census_bands["India"] = {}
for yr, lbl in [(1991, "India (Excluding J&K)"), (2001, "India"), (2011, "India")]:
    grp = cen_raw[(cen_raw["State"] == lbl) & (cen_raw["Year"] == yr)]
    census_bands["India"][yr] = build_state_census(grp)

print(f"Census bands loaded for {len([s for s in census_bands if s!='India'])} states + India")
print(f"Sample — India 2011 total: {sum(census_bands['India'][2011].values())/1e6:.2f} M")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 8 — Handle bifurcated states
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 2: Bifurcated State Estimation (Census Period)

Five states/UTs were carved out of existing states after 1991.
Their historical census populations are back-estimated using NDMC 2012 split ratios.
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── 2A. NDMC 2012 split ratios (used for bifurcated states) ──────────────────
ndmc_2012 = ndmc_raw[ndmc_raw["Year"] == 2012].set_index("State")

def split_ratio_2012(child, parent):
    \"\"\"Fraction of (child + parent) that belongs to child, per band, at NDMC 2012.\"\"\"
    ratios = {}
    for b in BANDS:
        c_val = float(ndmc_2012.loc[child, b]) if child in ndmc_2012.index else 0.0
        p_val = float(ndmc_2012.loc[parent, b]) if parent in ndmc_2012.index else 0.0
        tot = c_val + p_val
        ratios[b] = c_val / tot if tot > 0 else 0.0
    return ratios

# ── 2B. Jharkhand / Chhattisgarh / Uttarakhand — formed 2000, missing 1991 ──
SPLITS_2000 = {
    "Jharkhand":   "Bihar",
    "Chattisgarh": "Madhya Pradesh",
    "Uttarakhand": "Uttar Pradesh",
}
for child, parent in SPLITS_2000.items():
    r = split_ratio_2012(child, parent)
    census_bands[child][1991] = {}
    for b in BANDS:
        parent_1991 = census_bands[parent][1991][b]
        census_bands[child][1991][b]  = parent_1991 * r[b]
        census_bands[parent][1991][b] = parent_1991 * (1 - r[b])

# ── 2C. Telangana — formed 2014, not in any census ───────────────────────────
r_tel = split_ratio_2012("Telangana", "Andhra Pradesh")
census_bands["Telangana"] = {}
for yr in CENSUS_YEARS:
    census_bands["Telangana"][yr] = {}
    for b in BANDS:
        ap_val = census_bands["Andhra Pradesh"][yr][b]
        census_bands["Telangana"][yr][b]       = ap_val * r_tel[b]
        census_bands["Andhra Pradesh"][yr][b]  = ap_val * (1 - r_tel[b])

# ── 2D. Ladakh — formed 2019, not in any census ──────────────────────────────
r_lad = split_ratio_2012("Ladakh", "Jammu & Kashmir")
census_bands["Ladakh"] = {}
for yr in [2001, 2011]:
    census_bands["Ladakh"][yr] = {}
    for b in BANDS:
        jk_val = census_bands["Jammu & Kashmir"][yr][b]
        census_bands["Ladakh"][yr][b]           = jk_val * r_lad[b]
        census_bands["Jammu & Kashmir"][yr][b]  = jk_val * (1 - r_lad[b])
# Ladakh 1991: back-extrapolate using 2001-2011 growth rate
census_bands["Ladakh"][1991] = {}
census_bands["Jammu & Kashmir"][1991] = {}
for b in BANDS:
    lad_01 = census_bands["Ladakh"][2001][b]
    lad_11 = census_bands["Ladakh"][2011][b]
    rate   = (lad_11 / lad_01) ** (1/10) if lad_01 > 0 else 1.0
    census_bands["Ladakh"][1991][b] = lad_01 / (rate ** 10)

    jk_01  = census_bands["Jammu & Kashmir"][2001][b]
    jk_11  = census_bands["Jammu & Kashmir"][2011][b]
    rate_jk = (jk_11 / jk_01) ** (1/10) if jk_01 > 0 else 1.0
    census_bands["Jammu & Kashmir"][1991][b] = jk_01 / (rate_jk ** 10)

print("Bifurcated state estimates complete.")
n_states = len([s for s in census_bands if s != "India"])
print(f"States with census data: {n_states} (should be 37)")

# ── 2E. Validate population conservation ─────────────────────────────────────
for yr in [2001, 2011]:
    state_sum = sum(
        sum(census_bands[s][yr][b] for b in BANDS)
        for s in census_bands if s != "India"
    )
    india_sum = sum(census_bands["India"][yr][b] for b in BANDS)
    pct = 100 * (state_sum / india_sum - 1)
    print(f"  {yr}: sum of states = {state_sum/1e6:.2f} M | India census = {india_sum/1e6:.2f} M | diff = {pct:+.3f}%")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 10 — Gompertz TFR fit
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 3: Approach B Parameter Fitting

### 3.1 Gompertz TFR Curve

Fit to five Census 2019 (Table 3) projected TFR values for 5-year periods 2011–2035.
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── 3.1  Gompertz TFR — fit to Census 2019 data ──────────────────────────────
# Source: Census of India 2019 — Population Projections Report, Table 3
census_yrs = np.array([2013.0, 2018.0, 2023.0, 2028.0, 2033.0])  # period midpoints
census_tfr = np.array([2.34,   2.13,   1.94,   1.81,   1.73  ])

L_TFR = 1.667   # long-run floor (Census Statement 3 end-period TFR)
U_TFR = 2.50    # SRS 2009-11 baseline

def gompertz_tfr(year, a, b):
    t = year - 2010
    return L_TFR + (U_TFR - L_TFR) * (a ** (b ** t))

def loss_gompertz(params):
    a, b = params
    if not (0 < a < 1 and 0 < b < 1): return 1e10
    pred = gompertz_tfr(census_yrs, a, b)
    return np.sum((pred - census_tfr) ** 2)

res = minimize(loss_gompertz, x0=[0.65, 0.85], method="Nelder-Mead",
               options={"xatol": 1e-9, "fatol": 1e-11})
A_OPT, B_OPT = res.x

def tfr_b(year):
    \"\"\"Approach B TFR at a given year (Gompertz).\"\"\"
    return gompertz_tfr(year, A_OPT, B_OPT)

TFR_2036 = tfr_b(2036)
print(f"Gompertz fit:  L={L_TFR}, U={U_TFR}, a={A_OPT:.5f}, b={B_OPT:.5f}")
print(f"Fit error: {res.fun:.7f}")
print()
print("TFR trajectory (Census source vs fitted Gompertz):")
print(f"  {'Year':>6}  {'Census':>8}  {'Fitted':>8}  {'Error':>8}")
for yr, obs in zip(census_yrs, census_tfr):
    fit = tfr_b(yr)
    print(f"  {yr:>6.0f}  {obs:>8.3f}  {fit:>8.3f}  {fit-obs:>+8.4f}")
print()
for yr in [2036, 2050, 2070, 2100]:
    print(f"  TFR({yr}) = {tfr_b(yr):.3f}")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 11 — Approach B projections (all 16 bands, India)
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 4: Approach B India Projections (2037–2100)

Using the formula:
$$P_B(x, y) = \\text{NDMC}(x, 2036) \\times \\rho(x, y) \\times \\left(\\frac{\\text{TFR}_B(y)}{\\text{TFR}_B(2036)}\\right)^{0.3}$$

Then blended with NDMC momentum over 2037–2046.
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── 4.1  Pure Approach B for each band (India) ───────────────────────────────
approach_b = {}
for band in BANDS:
    ndmc_2036 = ndmc_india.loc[2036, band]   # NDMC anchor (millions)
    series = {}
    for yr in PROJ_YEARS:
        rho         = wpp_sf.loc[yr, band] if yr in wpp_sf.index else 1.0
        tfr_factor  = (tfr_b(yr) / TFR_2036) ** 0.3
        series[yr]  = ndmc_2036 * rho * tfr_factor
    approach_b[band] = pd.Series(series)

# ── 4.2  NDMC CAGR 2031–2036 per band ────────────────────────────────────────
r_ndmc = {}
for band in BANDS:
    v36 = ndmc_india.loc[2036, band]
    v31 = ndmc_india.loc[2031, band]
    r_ndmc[band] = (v36 / v31) ** (1/5) - 1

# ── 4.3  Blended Approach B ──────────────────────────────────────────────────
# 2037-2046: blend NDMC momentum (alpha=0) → Approach B (alpha=1)
# 2047-2100: pure Approach B, scaled to match blended endpoint at 2046
blended_b = {}
for band in BANDS:
    series = dict(ndmc_india[band].to_dict())   # start with NDMC 2012-2036
    for yr in range(2037, 2047):                 # blending window
        t     = yr - 2036
        alpha = t / T_BLEND
        p_mom = series[yr - 1] * (1 + r_ndmc[band])
        p_b   = approach_b[band].loc[yr]
        series[yr] = (1 - alpha) * p_mom + alpha * p_b
    # Scale factor to ensure continuity at 2046
    v2046_blend = series[2046]
    v2046_b     = approach_b[band].loc[2046]
    scale       = v2046_blend / v2046_b if v2046_b > 0 else 1.0
    for yr in range(2047, 2101):
        series[yr] = approach_b[band].loc[yr] * scale
    blended_b[band] = pd.Series(series)

print("Approach B projections built for all 16 bands (2012-2100).")
print("\\nIndia totals at key years (millions):")
for yr in [2036, 2050, 2070, 2100]:
    tot = sum(blended_b[b].loc[yr] for b in BANDS)
    print(f"  {yr}: {tot:.2f} M")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 12 — State-wise projections
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 5: State-wise Projections (2037–2100)

India-level scaling factors from Approach B are applied to each state's NDMC 2036 base.
This preserves each state's relative demographic structure as calibrated by NDMC.
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── 5.1  Build state-wise NDMC actual (2012-2036) in millions ─────────────────
ndmc_states = {}   # state -> DataFrame (Year x BANDS)
for state in STATES:
    sub = ndmc_raw[ndmc_raw["State"] == state].set_index("Year")[BANDS] / 1e6
    ndmc_states[state] = sub

# ── 5.2  Scaling factors from blended Approach B ─────────────────────────────
b_scale = {}   # band -> {yr: scale}
for band in BANDS:
    b_scale[band] = {
        yr: blended_b[band].loc[yr] / blended_b[band].loc[2036]
        for yr in PROJ_YEARS
    }

# ── 5.3  State CAGR 2031-2036 ────────────────────────────────────────────────
r_state = {}   # state -> {band -> cagr}
for state in STATES:
    r_state[state] = {}
    for band in BANDS:
        v36 = ndmc_states[state].loc[2036, band]
        v31 = ndmc_states[state].loc[2031, band]
        r_state[state][band] = (v36 / v31) ** (1/5) - 1 if v31 > 0 else 0.0

# ── 5.4  Project each state 2037-2100 (blended then scaled Approach B) ────────
state_proj = {}   # state -> {year: {band: value_millions}}
for state in STATES:
    ser = {yr: dict(ndmc_states[state].loc[yr]) for yr in NDMC_YEARS}
    # Blending window 2037-2046
    for yr in range(2037, 2047):
        t = yr - 2036
        alpha = t / T_BLEND
        ser[yr] = {}
        for band in BANDS:
            p_mom = ser[yr-1][band] * (1 + r_state[state][band])
            p_b   = ndmc_states[state].loc[2036, band] * b_scale[band][yr]
            ser[yr][band] = (1-alpha)*p_mom + alpha*p_b
    # Continuity scale at 2046, then pure Approach B scale
    for band in BANDS:
        v_blend_2046 = ser[2046][band]
        v_b_2046     = ndmc_states[state].loc[2036, band] * b_scale[band][2046]
        sc            = v_blend_2046 / v_b_2046 if v_b_2046 > 0 else 1.0
        for yr in range(2047, 2101):
            ser[yr][band] = ndmc_states[state].loc[2036, band] * b_scale[band][yr] * sc
    state_proj[state] = ser

print(f"State projections built for {len(state_proj)} states (2012-2100).")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 13 — Census linear interpolation
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 6: Census Period (1991–2011) — Linear Interpolation

For each state and age band, linearly interpolate between the three census anchor
years (1991, 2001, 2011) to produce annual values.
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── 6.1  Linear interpolation between census anchor years ────────────────────
def interp_census(bands_dict):
    \"\"\"
    bands_dict: {year: {band: value}} for anchor years.
    Returns {year: {band: value}} for every year from min to max anchor.
    \"\"\"
    anchors = sorted(bands_dict.keys())
    out = {}
    for k in range(len(anchors) - 1):
        y0, y1 = anchors[k], anchors[k+1]
        b0, b1 = bands_dict[y0], bands_dict[y1]
        for yr in range(y0, y1 + 1):
            t = (yr - y0) / (y1 - y0) if y1 > y0 else 0.0
            out[yr] = {b: b0[b] + t * (b1[b] - b0[b]) for b in BANDS}
    return out

# Build census period for all states
census_annual = {}
for state in census_bands:
    if state == "India": continue
    anchors = {yr: census_bands[state][yr] for yr in CENSUS_YEARS
               if yr in census_bands[state]}
    if len(anchors) >= 2:
        census_annual[state] = interp_census(anchors)
    else:
        print(f"  WARNING: {state} has fewer than 2 census anchors")

# India
census_annual["India"] = interp_census(
    {yr: census_bands["India"][yr] for yr in CENSUS_YEARS
     if yr in census_bands["India"]}
)

print(f"Census annual interpolation done for {len(census_annual)-1} states + India.")
print(f"Years covered: 1991–2011")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 14 — Assemble complete time series
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("""\
## Section 7: Assemble Complete Time Series (1991–2100)

Concatenate:
1. Census interpolated (1991–2011, absolute values)
2. NDMC actual (2012–2036, absolute values — convert from millions to absolute)
3. Approach B projections (2037–2100, millions → absolute)
"""))

cells.append(nbf.v4.new_code_cell("""\
# ── 7.1  Assemble full series for all 37 states + India ──────────────────────
# final_pop[state][year][band] = population (absolute count)

final_pop = {}

for state in STATES + ["India"]:
    series = {}

    # Segment 1: Census 1991-2011 (absolute)
    for yr in range(1991, 2012):
        if yr in census_annual.get(state, {}):
            series[yr] = {b: census_annual[state][yr][b] for b in BANDS}

    # Segment 2: NDMC 2012-2036 (convert millions → absolute)
    if state == "India":
        for yr in NDMC_YEARS:
            series[yr] = {b: ndmc_india.loc[yr, b] * 1e6 for b in BANDS}
    else:
        for yr in NDMC_YEARS:
            if yr in ndmc_states.get(state, pd.DataFrame()).index:
                series[yr] = {b: ndmc_states[state].loc[yr, b] * 1e6 for b in BANDS}

    # Segment 3: Approach B 2037-2100 (millions → absolute)
    if state == "India":
        for yr in PROJ_YEARS:
            series[yr] = {b: blended_b[b].loc[yr] * 1e6 for b in BANDS}
    else:
        for yr in PROJ_YEARS:
            series[yr] = {b: state_proj[state][yr][b] * 1e6 for b in BANDS}

    final_pop[state] = series

# ── 7.2  Convert to tidy DataFrames ──────────────────────────────────────────
def to_df(state):
    rows = []
    for yr in sorted(final_pop[state].keys()):
        row = {"State": state, "Year": yr}
        row.update(final_pop[state][yr])
        row["Total"] = sum(final_pop[state][yr][b] for b in BANDS)
        row["Source"] = (
            "Census-Interpolated" if yr <= 2011 else
            "NDMC-Actual"         if yr <= 2036 else
            "Approach-B"
        )
        rows.append(row)
    return pd.DataFrame(rows)

df_india = to_df("India")
print(f"India series: {len(df_india)} rows ({df_india['Year'].min()}–{df_india['Year'].max()})")
print("\\nIndia total female population (millions) at key years:")
for yr in [1991, 2001, 2011, 2020, 2036, 2050, 2070, 2100]:
    row = df_india[df_india["Year"]==yr]
    if len(row):
        print(f"  {yr}: {row['Total'].values[0]/1e6:.2f} M  [{row['Source'].values[0]}]")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 15 — Export
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## Section 8: Export Results"))

cells.append(nbf.v4.new_code_cell("""\
# ── 8.1  Export India ─────────────────────────────────────────────────────────
india_out = os.path.join(OUT_DIR, "India_Female_AgeBands_1991_2100.xlsx")
df_india.to_excel(india_out, index=False)
print(f"Saved: {india_out}")

# ── 8.2  Export all states individually ──────────────────────────────────────
all_dfs = []
for state in STATES:
    df_s = to_df(state)
    fname = state.replace(" ", "_").replace("&", "and").replace("/", "-") + ".xlsx"
    df_s.to_excel(os.path.join(STATES_DIR, fname), index=False)
    all_dfs.append(df_s)

print(f"Saved {len(STATES)} state files to {STATES_DIR}/")

# ── 8.3  Combined long-format file ───────────────────────────────────────────
df_combined = pd.concat([df_india] + all_dfs, ignore_index=True)
combined_out = os.path.join(OUT_DIR, "Combined_All_States_1991_2100.xlsx")
df_combined.to_excel(combined_out, index=False)
print(f"Saved combined: {combined_out}  ({len(df_combined):,} rows)")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 16 — Validation
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## Section 9: Validation"))

cells.append(nbf.v4.new_code_cell("""\
# ── 9.1  India total population trajectory ───────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
for src, color, ls in [
    ("Census-Interpolated", "#C00000", "-"),
    ("NDMC-Actual",         "#ED7D31", "-"),
    ("Approach-B",          "#2E75B6", "--"),
]:
    sub = df_india[df_india["Source"] == src]
    ax.plot(sub["Year"], sub["Total"]/1e6, color=color, lw=2, ls=ls, label=src)
ax.axvline(2036, color="gray", lw=0.8, ls=":", label="2036 handoff")
ax.set_title("India Total Female Population 1991-2100", fontweight="bold")
ax.set_ylabel("Population (millions)")
ax.set_xlabel("Year")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}M"))
ax.legend(fontsize=8)

# ── 9.2  India TFR trajectory ────────────────────────────────────────────────
ax2 = axes[1]
yrs_plot = list(range(2010, 2101))
ax2.plot(yrs_plot, [tfr_b(y) for y in yrs_plot], color="#2E75B6", lw=2, label="Gompertz TFR (Approach B)")
ax2.scatter(census_yrs, census_tfr, color="#C00000", s=50, zorder=5, label="Census data points")
ax2.axhline(L_TFR, color="gray", lw=0.8, ls="--", alpha=0.7, label=f"Floor = {L_TFR}")
ax2.set_title("TFR Trajectory (Gompertz, Census-fitted)", fontweight="bold")
ax2.set_ylabel("Total Fertility Rate")
ax2.set_xlabel("Year")
ax2.legend(fontsize=8)
ax2.set_ylim(1.0, 2.8)

plt.tight_layout()
plt.show()

# ── 9.3  Band-sum vs Total check ─────────────────────────────────────────────
df_india["band_sum"] = df_india[BANDS].sum(axis=1)
max_err = (df_india["band_sum"] - df_india["Total"]).abs().max()
print(f"\\nValidation: max |band_sum - Total| = {max_err:.4f}  (should be ~0)")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 17 — Summary visualisation
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""\
# ── 9.4  Selected age bands 1991-2100 ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))
HIGHLIGHT_BANDS = {
    "00-04": ("#e41a1c", "0-4 (children)"),
    "15-19": ("#377eb8", "15-19"),
    "20-24": ("#4daf4a", "20-24"),
    "25-29": ("#984ea3", "25-29"),
    "40-44": ("#ff7f00", "40-44"),
    "65-69": ("#a65628", "65-69"),
    "75+":   ("#f781bf", "75+"),
}
for band, (color, label) in HIGHLIGHT_BANDS.items():
    ax.plot(df_india["Year"], df_india[band]/1e6, color=color, lw=1.8, label=label)
ax.axvline(2011, color="gray", lw=0.7, ls=":", alpha=0.6)
ax.axvline(2036, color="gray", lw=0.7, ls=":", alpha=0.6, label="Census/NDMC handoffs")
ax.set_title("India Female Population by Age Band — Methodology A (1991-2100)", fontweight="bold")
ax.set_ylabel("Population (millions)")
ax.set_xlabel("Year")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}M"))
ax.legend(fontsize=8, ncol=2)
plt.tight_layout()
plt.show()
"""))

# ─────────────────────────────────────────────────────────────────────────────
# CELL 18 — 37-state overview
# ─────────────────────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell("""\
# ── 9.5  All 37 states — total female population 1991-2100 ────────────────────
ncols, nrows = 7, 6
fig, axes = plt.subplots(nrows, ncols, figsize=(22, 18), sharey=False)
axes_flat = axes.flatten()

for i, state in enumerate(STATES):
    ax = axes_flat[i]
    df_s = to_df(state)
    for src, color, ls in [
        ("Census-Interpolated", "#C00000", "-"),
        ("NDMC-Actual",         "#ED7D31", "-"),
        ("Approach-B",          "#2E75B6", "--"),
    ]:
        sub = df_s[df_s["Source"] == src]
        ax.plot(sub["Year"], sub["Total"]/1e6, color=color, lw=1.4, ls=ls)
    ax.axvline(2036, color="gray", lw=0.5, ls=":", alpha=0.5)
    ax.set_title(state, fontsize=7.5, fontweight="bold", pad=2)
    ax.tick_params(labelsize=5.5)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:.0f}M"))
    ax.set_xlim(1988, 2103)

for j in range(len(STATES), len(axes_flat)):
    axes_flat[j].set_visible(False)

handles = [
    plt.Line2D([0],[0], color="#C00000", lw=1.4, label="Census (1991-2011)"),
    plt.Line2D([0],[0], color="#ED7D31", lw=1.4, label="NDMC (2012-2036)"),
    plt.Line2D([0],[0], color="#2E75B6", lw=1.4, ls="--", label="Approach B (2037-2100)"),
]
fig.legend(handles=handles, loc="lower right", fontsize=9, ncol=3,
           bbox_to_anchor=(0.98, 0.01), frameon=True)
fig.suptitle("Total Female Population 1991-2100 — All 37 States/UTs (Methodology A)",
             fontsize=13, fontweight="bold", y=1.005)
plt.tight_layout()
plt.show()

print("\\nDone! All outputs written to the output/ directory.")
"""))

# ─────────────────────────────────────────────────────────────────────────────
# Assemble and write
# ─────────────────────────────────────────────────────────────────────────────
nb.cells = cells

import os
NB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "India_Female_Population_1991_2100.ipynb"
)
nbf.write(nb, NB_PATH)
print(f"Notebook written: {NB_PATH}  ({len(cells)} cells)")
