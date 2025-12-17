import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================
# CONFIG: World Bank (WDI) indicators
# =========================
INDICATORS = {
    "Female Secondary Enrollment (gross, %)": {
        "code": "SE.SEC.ENRR.FE",
        "unit": "percent",
        "desc": "Gross enrollment ratio, secondary, female (%). Source: World Bank WDI.",
    },
    "Female Labor Force Participation (%, ages 15+)": {
        "code": "SL.TLF.CACT.FE.ZS",
        "unit": "percent",
        "desc": "Labor force participation rate, female (% of female population ages 15+). Source: World Bank WDI.",
    },
    "Maternal Mortality Ratio (per 100,000 live births)": {
        "code": "SH.STA.MMRT",
        "unit": "per_100k",
        "desc": "Maternal mortality ratio (modeled estimate, per 100,000 live births). Source: World Bank WDI.",
    },
}

WB_COUNTRY_URL = "https://api.worldbank.org/v2/country"
WB_IND_URL = "https://api.worldbank.org/v2/country/all/indicator/{code}"

HEADERS = {"User-Agent": "streamlit-women-dashboard/1.0"}

# =========================
# Helpers
# =========================
def _wb_get(url: str, params: dict):
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=24 * 3600, show_spinner=False)
def fetch_countries() -> pd.DataFrame:
    """
    Return: iso3, country, region, income, lending
    """
    js = _wb_get(WB_COUNTRY_URL, {"format": "json", "per_page": 400})
    if not isinstance(js, list) or len(js) < 2 or not isinstance(js[1], list):
        return pd.DataFrame(columns=["iso3", "country", "region", "income", "lending"])

    rows = []
    for c in js[1]:
        iso3 = c.get("id")  # ISO3
        name = c.get("name")
        region = (c.get("region") or {}).get("value")
        income = (c.get("incomeLevel") or {}).get("value")
        lending = (c.get("lendingType") or {}).get("value")
        if iso3 and name:
            rows.append(
                {"iso3": iso3, "country": name, "region": region, "income": income, "lending": lending}
            )
    return pd.DataFrame(rows)

def fetch_indicator(code: str, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Return: iso3, country, year, value
    """
    url = WB_IND_URL.format(code=code)
    params = {
        "format": "json",
        "per_page": 20000,
        "date": f"{start_year}:{end_year}",
        "page": 1,
    }

    rows = []

    js = _wb_get(url, params)
    if not isinstance(js, list) or len(js) < 2:
        return pd.DataFrame(columns=["iso3", "country", "year", "value"])

    meta = js[0] if isinstance(js[0], dict) else {}
    pages = int(meta.get("pages") or 1)

    def _consume(items):
        if not isinstance(items, list):
            return
        for r in items:
            if not isinstance(r, dict):
                continue
            iso3 = r.get("countryiso3code") or (r.get("country") or {}).get("id")
            country = (r.get("country") or {}).get("value")
            year = r.get("date")
            val = r.get("value")

            # skip empty values
            if iso3 in (None, "", "NA") or year is None:
                continue
            try:
                year_int = int(year)
            except Exception:
                continue

            rows.append({"iso3": iso3, "country": country, "year": year_int, "value": val})

    _consume(js[1])

    # pagination
    for p in range(2, pages + 1):
        params["page"] = p
        js_p = _wb_get(url, params)
        if isinstance(js_p, list) and len(js_p) >= 2:
            _consume(js_p[1])

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["iso3", "country", "year", "value"])

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["value"]).reset_index(drop=True)
    return df

@st.cache_data(ttl=24 * 3600, show_spinner=True)
def load_all_data(start_year: int = 1990, end_year: int | None = None) -> pd.DataFrame:
    if end_year is None:
        end_year = datetime.now().year

    countries = fetch_countries()

    frames = []
    for ind_name, meta in INDICATORS.items():
        d = fetch_indicator(meta["code"], start_year, end_year)
        if d.empty:
            continue
        d["indicator"] = ind_name
        d["indicator_code"] = meta["code"]
        d["unit"] = meta["unit"]
        frames.append(d)

    if not frames:
        return pd.DataFrame(columns=["iso3", "country", "year", "value", "indicator", "indicator_code", "unit"])

    df = pd.concat(frames, ignore_index=True)

    # --- HARDEN: ensure iso3 exists (single source of truth)
if "iso3" not in df.columns:
    if "countryiso3code" in df.columns:
        df = df.rename(columns={"countryiso3code": "iso3"})
    elif "Country Code" in df.columns:
        df = df.rename(columns={"Country Code": "iso3"})
    else:
        # fail early with clear message
        raise KeyError(
            f"'iso3' not found. Available columns: {list(df.columns)}"
        )


# merge pakai iso3 saja
df = df.merge(
    countries[["iso3", "region", "income", "lending"]],
    on="iso3",
    how="left"
)


    return df

def sidebar_nav():
    st.sidebar.markdown("## 💗 Women Dashboard")
    st.sidebar.page_link("app.py", label="💗 Description")
    st.sidebar.page_link("pages/1_Overview_of_Womens_Data.py", label="📚 Overview of Women's Data")
    st.sidebar.page_link("pages/2_Country_Profile.py", label="🧍‍♀️ Country Profile")
    st.sidebar.page_link("pages/3_Comparison_between_Nations.py", label="🌍 Comparison between Nations")
    st.sidebar.markdown("---")
    st.sidebar.caption("Data source: World Bank (WDI) via API")
