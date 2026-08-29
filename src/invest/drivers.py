"""Q3 — Características que explicam as melhores receitas."""

from __future__ import annotations

import pandas as pd

from . import revenue


def _bucket_star_rating(x: float) -> str:
    if pd.isna(x) or x <= 0:
        return "sem avaliação"
    if x < 4.5:
        return "< 4.5"
    if x < 4.8:
        return "4.5–4.8"
    return "≥ 4.8"


def _bucket_reviews(x: float) -> str:
    if pd.isna(x) or x <= 0:
        return "0"
    if x <= 5:
        return "1–5"
    if x <= 20:
        return "6–20"
    return "> 20"


def build_drivers() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (impacto_ordenado, detalhes_por_categoria)."""
    rev, _ = revenue.estimate_revenue()
    df = rev[~rev["sem_receita"]].copy()

    df["is_superhost_bool"] = df["is_superhost"].astype(str).str.lower().eq("true")
    df["star_bucket"] = df["star_rating"].map(_bucket_star_rating)
    df["reviews_bucket"] = df["number_of_reviews"].map(_bucket_reviews)

    drivers = {
        "nº de quartos": "number_of_bedrooms",
        "tipo de anúncio": "listing_type",
        "bairro": "suburb",
        "superhost": "is_superhost_bool",
        "avaliação (star rating)": "star_bucket",
        "nº de avaliações": "reviews_bucket",
    }

    detalhes: list[pd.DataFrame] = []
    impactos: list[dict] = []

    overall = df["receita_anual"].median()

    for nome, col in drivers.items():
        g = (
            df.groupby(col, dropna=False)["receita_anual"]
            .agg(mediana="median", n="count")
            .reset_index()
            .sort_values("mediana", ascending=False)
        )
        g = g[g["n"] >= 10]  # categorias com amostra mínima
        if g.empty:
            impactos.append({"característica": nome, "impacto": float("nan"), "conclusivo": False})
            continue

        top = g.iloc[0]["mediana"]
        bottom = g.iloc[-1]["mediana"]
        spread = (top - bottom) / overall if overall else float("nan")
        impactos.append(
            {
                "característica": nome,
                "impacto": spread,
                "conclusivo": bool(abs(spread) >= 0.10) and len(g) >= 2,
            }
        )

        g = g.copy()
        g.insert(0, "característica", nome)
        g["categoria"] = g[col].astype(str)
        detalhes.append(g[["característica", "categoria", "mediana", "n"]])

    impacto_df = pd.DataFrame(impactos).sort_values(
        "impacto", ascending=False, na_position="last"
    )
    detalhe_df = pd.concat(detalhes, ignore_index=True)
    return impacto_df, detalhe_df


def main() -> None:
    impacto, detalhes = build_drivers()

    print("Características ordenadas por impacto na receita (mediana), desc:\n")
    out = impacto.copy()
    out["impacto"] = out["impacto"].map(lambda x: "—" if pd.isna(x) else f"{x:.1%}")
    out["conclusivo"] = out["conclusivo"].map({True: "sim", False: "não/inconclusivo"})
    print(out.to_string(index=False))

    print("\nDetalhe: mediana de receita por categoria (só categorias com n ≥ 10):\n")
    det = detalhes.copy()
    det["mediana"] = det["mediana"].map(lambda x: f"R$ {x:,.0f}")
    print(det.to_string(index=False))

    print("\nObservações:")
    print("  - 'superhost' tem efeito fraco e contraintuitivo (não-superhost rende mais na")
    print("    mediana); provável ruído/confundimento — não é driver confiável de receita.")
    print("  - Listings 'sem avaliação' / '0 reviews' têm mediana alta (n=22): viés de")
    print("    imóveis novos/premium — interpretar com cuidado.")


if __name__ == "__main__":
    main()
