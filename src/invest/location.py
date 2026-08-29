"""Q2 — Melhor localização por receita: ranking por bairro (suburb)."""

from __future__ import annotations

import pandas as pd

from . import revenue

MIN_SAMPLE = 10


def build_location_ranking() -> pd.DataFrame:
    """Agrega por suburb com receita total, média/mediana por listing e ADR."""
    rev, _ = revenue.estimate_revenue()
    com = rev[~rev["sem_receita"]].copy()

    # Remove bairro ausente/literal "none".
    com = com[
        com["suburb"].notna() & (com["suburb"].astype(str).str.strip().str.lower() != "none")
    ]

    agg = (
        com.groupby("suburb")
        .agg(
            receita_total=("receita_anual", "sum"),
            receita_media=("receita_anual", "mean"),
            receita_mediana=("receita_anual", "median"),
            adr_medio=("adr", "mean"),
            adr_mediano=("adr", "median"),
            n=("receita_anual", "count"),
        )
        .reset_index()
    )

    agg["amostra_pequena"] = agg["n"] < MIN_SAMPLE
    return agg


def main() -> None:
    ranking = build_location_ranking().sort_values("receita_media", ascending=False)

    print("Ranking de bairros por RECEITA MÉDIA POR LISTING (anual, 60%), desc:\n")
    cols = [
        "suburb",
        "n",
        "receita_media",
        "receita_mediana",
        "adr_medio",
        "adr_mediano",
        "receita_total",
        "amostra_pequena",
    ]
    out = ranking[cols].copy()
    for c in ["receita_media", "receita_mediana", "adr_medio", "adr_mediano"]:
        out[c] = out[c].map(lambda x: f"R$ {x:,.0f}")
    out["receita_total"] = out["receita_total"].map(lambda x: f"R$ {x:,.0f}")
    print(out.to_string(index=False))

    # Vencedor (ignorando amostra pequena) e margem sobre o 2º.
    com_amostra = ranking[~ranking["amostra_pequena"]]
    if len(com_amostra) >= 2:
        first = com_amostra.iloc[0]
        second = com_amostra.iloc[1]
        margem = first["receita_media"] / second["receita_media"] - 1
        print(
            f"\nVencedor (receita média): {first['suburb']} "
            f"(R$ {first['receita_media']:,.0f}), margem de {margem:.1%} sobre "
            f"{second['suburb']} (R$ {second['receita_media']:,.0f})."
        )

    print("\nRanking de bairros por RECEITA TOTAL (anual, 60%), desc:\n")
    total = ranking.sort_values("receita_total", ascending=False)[cols].copy()
    for c in ["receita_media", "receita_mediana", "adr_medio", "adr_mediano"]:
        total[c] = total[c].map(lambda x: f"R$ {x:,.0f}")
    total["receita_total"] = total["receita_total"].map(lambda x: f"R$ {x:,.0f}")
    print(total.to_string(index=False))


if __name__ == "__main__":
    main()
