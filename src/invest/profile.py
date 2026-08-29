"""Q1 — Melhor perfil de imóvel: ranking por yield e por receita por (listing_type, quartos)."""

from __future__ import annotations

import pandas as pd

from . import market, revenue

MIN_SAMPLE = 10


def build_profile_ranking() -> pd.DataFrame:
    """Agrega por (listing_type, number_of_bedrooms) com ranking de yield e receita."""
    rev, _ = revenue.estimate_revenue()
    com = rev[~rev["sem_receita"]].copy()

    med_price = market.median_sale_price_by_profile(market.load_vivareal())

    # Referência de custo por perfil (tipologia + nº de quartos).
    com = com.merge(
        med_price,
        left_on=["listing_type", "number_of_bedrooms"],
        right_index=True,
        how="left",
    )
    com["yield_anual"] = com["receita_anual"] / com["sale_price_mediano"]

    agg = (
        com.groupby(["listing_type", "number_of_bedrooms"], dropna=False)
        .agg(
            receita_mediana=("receita_anual", "median"),
            receita_media=("receita_anual", "mean"),
            yield_mediano=("yield_anual", "median"),
            yield_medio=("yield_anual", "mean"),
            adr_mediana=("adr", "median"),
            n=("receita_anual", "count"),
        )
        .reset_index()
    )

    agg["amostra_pequena"] = agg["n"] < MIN_SAMPLE
    agg["compacto"] = agg["number_of_bedrooms"].le(1)

    return agg


def _fmt(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in ["receita_mediana", "receita_media", "adr_mediana"]:
        if c in out.columns:
            out[c] = out[c].map(lambda x: f"R$ {x:,.0f}")
    for c in ["yield_mediano", "yield_medio"]:
        if c in out.columns:
            out[c] = out[c].map(lambda x: "—" if pd.isna(x) else f"{x:.1%}")
    return out


def main() -> None:
    ranking = build_profile_ranking()

    print("Ranking por RENTABILIDADE (yield anual), desc:\n")
    cols = [
        "listing_type",
        "number_of_bedrooms",
        "n",
        "yield_mediano",
        "yield_medio",
        "receita_mediana",
        "receita_media",
        "adr_mediana",
        "amostra_pequena",
        "compacto",
    ]
    yield_rank = ranking.sort_values("yield_mediano", ascending=False, na_position="last")
    print(_fmt(yield_rank[cols]).to_string(index=False))

    print("\n\nRanking por RECEITA BRUTA ANUAL (mediana), desc:\n")
    rev_rank = ranking.sort_values("receita_mediana", ascending=False)
    print(_fmt(rev_rank[cols]).to_string(index=False))


if __name__ == "__main__":
    main()
