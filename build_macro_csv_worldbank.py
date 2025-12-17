"""
Build a CSV of macro indicators (GDP growth, inflation CPI, unemployment)
for ASEAN + selected comparator countries by pulling from the World Bank API.

Run:
  python build_macro_csv_worldbank.py

Output:
  data/macro_indicators_worldbank_latest.csv
"""

from __future__ import annotations

import os
import time
import requests
import pandas as pd

OUT_PATH = "data/macro_indicators_worldbank_latest.csv"

# Countries (ISO3)
COUNTRIES = [
    # ASEAN
    "BRN", "KHM", "IDN", "LAO", "MYS", "MMR", "PHL", "SGP", "THA", "VNM",
    # Comparators (optional)
    "USA", "JPN", "CHN", "DEU",
]

# World Bank indicator codes
INDICATORS = {
    "gdp_growth_pct": "NY.GDP.MKTP.KD.ZG",   # GDP growth (annual %)
    "inflation_cpi_pct": "FP.CPI.TOTL.ZG",   # Inflation, CPI (annual %)
    "unemployment_pct": "SL.UEM.TOTL.ZS",    # Unemployment, total (% of labor force) (modeled ILO)
}

API = "https://api.worldbank.org/v2"


def fetch_indicator(country_list: list[str], indicator_code: str) -> pd.DataFrame:
    """
    Fetch indicator series for multiple countries from World Bank.
    Returns columns: iso3, country, year, value
    """
    c_str = ";".join(country_list)
    url = f"{API}/country/{c_str}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 20000}

    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    payload = r.json()

    data = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    rows = []
    for item in data:
        if not item:
            continue
        rows.append(
            {
                "iso3": item.get("countryiso3code"),
                "country": (item.get("country") or {}).get("value"),
                "year": int(item.get("date")) if item.get("date") else None,
                "value": item.get("value"),
            }
        )

    return pd.DataFrame(rows)


def latest_complete_row(gdp: pd.DataFrame, inf: pd.DataFrame, u: pd.DataFrame) -> pd.DataFrame:
    """
    Merge 3 indicators per (iso3, year) and pick the latest year where all 3 exist.
    If no complete year exists, fallback to latest available GDP year.
    """
    # rename value columns
    gdp = gdp.rename(columns={"value": "gdp_growth_pct"})
    inf = inf.rename(columns={"value": "inflation_cpi_pct"})
    u = u.rename(columns={"value": "unemployment_pct"})

    # merge with country carried from gdp (avoid country_x/country_y)
    m = (
        gdp[["iso3", "country", "year", "gdp_growth_pct"]]
        .merge(inf[["iso3", "year", "inflation_cpi_pct"]], on=["iso3", "year"], how="left")
        .merge(u[["iso3", "year", "unemployment_pct"]], on=["iso3", "year"], how="left")
    )

    out_rows = []
    for iso3, grp in m.groupby("iso3"):
        grp = grp.sort_values("year", ascending=False)

        complete = grp.dropna(subset=["gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct"])
        pick = complete.iloc[0] if not complete.empty else grp.iloc[0]
        out_rows.append(pick)

    out = pd.DataFrame(out_rows)
    out = out[["country", "iso3", "year", "gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct"]]
    return out.sort_values("country")


def main() -> None:
    os.makedirs("data", exist_ok=True)

    # fetch indicators
    gdp = fetch_indicator(COUNTRIES, INDICATORS["gdp_growth_pct"])
    time.sleep(0.2)
    inf = fetch_indicator(COUNTRIES, INDICATORS["inflation_cpi_pct"])
    time.sleep(0.2)
    u = fetch_indicator(COUNTRIES, INDICATORS["unemployment_pct"])

    if gdp.empty:
        raise RuntimeError("No GDP data returned from World Bank API. Check internet/indicator code.")

    df = latest_complete_row(gdp, inf, u)

    # numeric conversion
    for c in ["gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df.to_csv(OUT_PATH, index=False)
    print(f"Saved: {OUT_PATH} (rows={len(df)})")


if __name__ == "__main__":
    main()
