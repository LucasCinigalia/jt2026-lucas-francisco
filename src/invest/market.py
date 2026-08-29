"""Acesso ao mercado de compra (VivaReal)."""

from __future__ import annotations

import pandas as pd

from . import load

# Tipologias residenciais do VivaReal que têm análogo no Airbnb (para comparação de yield).
RESIDENTIAL_TYPES = ("apartamento", "casa")


def load_vivareal() -> pd.DataFrame:
    """Carrega o VivaReal com colunas numéricas convertidas."""
    v = load.load_all()["VivaReal_Itapema.csv"].copy()
    v["sale_price"] = pd.to_numeric(v["sale_price"], errors="coerce")
    v["monthly_condo_fee"] = pd.to_numeric(v["monthly_condo_fee"], errors="coerce")
    v["yearly_iptu"] = pd.to_numeric(v["yearly_iptu"], errors="coerce")
    v["bedrooms"] = pd.to_numeric(v["bedrooms"], errors="coerce")
    v["usable_area"] = pd.to_numeric(v["usable_area"], errors="coerce")
    return v


def median_sale_price_by_profile(vivareal: pd.DataFrame) -> pd.Series:
    """Preço de venda mediano por (listing_type, bedrooms), só residencial e preço válido."""
    res = vivareal[
        vivareal["listing_type"].isin(RESIDENTIAL_TYPES) & (vivareal["sale_price"] > 0)
    ]
    return res.groupby(["listing_type", "bedrooms"])["sale_price"].median().rename(
        "sale_price_mediano"
    )
