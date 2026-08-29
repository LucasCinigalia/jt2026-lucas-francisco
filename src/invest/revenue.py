"""Métrica de receita: ADR (mediana do preço) e receita anual estimada por listing."""

from __future__ import annotations

import pandas as pd

from . import etl, load

DEFAULT_OCCUPANCY = 0.60
OCCUPANCIES = (0.50, 0.60, 0.70)


def compute_adr(price_df: pd.DataFrame) -> tuple[pd.Series, int]:
    """Calcula a ADR (mediana do preço diário) por listing.

    Regras:
    - preço inválido (não-numérico, 0 ou negativo) é excluído e contado;
    - para o mesmo (listing, data), mantém o preço da captura mais recente,
      evitando dupla contagem de snapshots.

    Retorna (Series adr indexada por airbnb_listing_id, nº de preços inválidos).
    """
    df = price_df[["airbnb_listing_id", "date", "price", "aquisition_date"]].copy()
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    invalid = df["price"].isna() | (df["price"] <= 0)
    n_invalid = int(invalid.sum())
    df = df[~invalid]

    df = df.sort_values("aquisition_date").drop_duplicates(
        subset=["airbnb_listing_id", "date"], keep="last"
    )

    adr = df.groupby("airbnb_listing_id")["price"].median().rename("adr")
    return adr, n_invalid


def annual_revenue_at(adr: pd.Series, occupancy: float) -> pd.Series:
    """Receita anual estimada = ADR × 365 × ocupação."""
    return adr * 365 * occupancy


def estimate_revenue(listings: pd.DataFrame | None = None) -> pd.DataFrame:
    """Anexa ADR e receita anual (cenário default) aos listings.

    Listings sem preço ficam marcados como `sem_receita=True` e com adr/receita nulos.
    """
    if listings is None:
        listings, _ = etl.build_listings()

    price_df = load.load_all()["Price_AV_Itapema.csv"]
    adr, n_invalid = compute_adr(price_df)

    out = listings.copy()
    out["adr"] = out["airbnb_listing_id"].map(adr)
    out["sem_receita"] = out["adr"].isna()
    out["receita_anual"] = annual_revenue_at(out["adr"], DEFAULT_OCCUPANCY)

    for occ in OCCUPANCIES:
        out[f"receita_occ_{int(occ * 100)}"] = annual_revenue_at(out["adr"], occ)

    return out, n_invalid


def main() -> None:
    rev, n_invalid = estimate_revenue()
    com_receita = rev[~rev["sem_receita"]]
    print("Receita estimada (ocupação default 60%).\n")
    print(f"  Preços inválidos (<=0/NaN) excluídos: {n_invalid}")
    print(f"  Listings com receita:   {len(com_receita)}")
    print(f"  Listings sem receita:   {int(rev['sem_receita'].sum())}")
    print("\n== ADR (diária) ==")
    print(com_receita["adr"].describe().round(2).to_string())
    print("\n== Receita anual (60%) ==")
    print(com_receita["receita_anual"].describe().round(2).to_string())
    print("\n== Receita anual por cenário de ocupação (total do portfólio com preço) ==")
    for occ in OCCUPANCIES:
        col = f"receita_occ_{int(occ * 100)}"
        print(f"  ocupação {int(occ * 100)}%: R$ {com_receita[col].sum():,.0f}")


if __name__ == "__main__":
    main()
