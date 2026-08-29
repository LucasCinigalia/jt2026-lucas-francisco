"""Robustez: outliers, missing e sensibilidade da análise."""

from __future__ import annotations

import pandas as pd

from . import investment, load, market, revenue


def _percentiles(s: pd.Series) -> tuple[float, float]:
    return s.quantile(0.01), s.quantile(0.99)


def outlier_report() -> pd.DataFrame:
    """Outliers (fora de [P1, P99]) em price (Airbnb) e sale_price (VivaReal)."""
    price = load.load_all()["Price_AV_Itapema.csv"]
    price["price"] = pd.to_numeric(price["price"], errors="coerce")

    v = market.load_vivareal()

    rows = []
    for nome, s in [("price (diária)", price["price"]), ("sale_price", v["sale_price"])]:
        p1, p99 = _percentiles(s)
        n_lo = int((s < p1).sum())
        n_hi = int((s > p99).sum())
        rows.append(
            {
                "variável": nome,
                "P1": p1,
                "P99": p99,
                "n abaixo P1": n_lo,
                "n acima P99": n_hi,
                "total": int(s.count()),
            }
        )
    return pd.DataFrame(rows)


def missing_report() -> pd.DataFrame:
    """Percentual de ausência por coluna-chave."""
    d = load.load_all()
    price = d["Price_AV_Itapema.csv"]
    price["price"] = pd.to_numeric(price["price"], errors="coerce")
    v = market.load_vivareal()
    mesh = d["Mesh_Ids_Data_Itapema.csv"]
    det = d["Details_Itapema.csv"]

    checks = {
        "Price_AV.price": price["price"],
        "Details.listing_type": det["listing_type"],
        "Details.number_of_bedrooms": det["number_of_bedrooms"],
        "Details.star_rating": det["star_rating"],
        "Mesh.suburb": mesh["suburb"],
        "VivaReal.sale_price": v["sale_price"],
        "VivaReal.monthly_condo_fee": v["monthly_condo_fee"],
        "VivaReal.yearly_iptu": v["yearly_iptu"],
        "VivaReal.usable_area": v["usable_area"],
        "VivaReal.bedrooms": v["bedrooms"],
    }
    rows = [
        {"coluna": nome, "ausentes (%)": round(s.isna().mean() * 100, 2), "total": int(len(s))}
        for nome, s in checks.items()
    ]
    return pd.DataFrame(rows)


def sensitivity_table() -> pd.DataFrame:
    """Yield e payback medianos por bairro (top 5) em cada cenário de ocupação."""
    df = investment.build_investment()
    for occ in (50, 60, 70):
        col = f"receita_occ_{occ}"
        df[f"yield_{occ}"] = (df[col] - df["custo_anual"]) / df["sale_price_mediano"]
        df[f"payback_{occ}"] = df["sale_price_mediano"] / (df[col] - df["custo_anual"])

    g = df.groupby("suburb_norm").agg(
        yield_50=("yield_50", "median"),
        yield_60=("yield_60", "median"),
        yield_70=("yield_70", "median"),
        payback_60=("payback_60", "median"),
        n=("yield_60", "count"),
    )
    g = g[g["n"] >= 10].sort_values("yield_60", ascending=False, na_position="last")
    return g.reset_index()


def winner_stability() -> None:
    """Confirma se o bairro vencedor (yield) muda ao remover outliers de ADR e sale_price."""
    df = investment.build_investment()

    adr_p99 = df["adr"].quantile(0.99)
    price_p99 = df["sale_price_mediano"].quantile(0.99)

    clean = df[(df["adr"] <= adr_p99) & (df["sale_price_mediano"] <= price_p99)]

    def top3(d):
        g = (
            d.groupby("suburb_norm")
            .agg(yield_mediano=("yield_anual", "median"), n=("yield_anual", "count"))
            .reset_index()
        )
        g = g[g["n"] >= 10].sort_values("yield_mediano", ascending=False)
        return list(g.head(3)["suburb_norm"])

    print(f"Top 3 bairros por yield (completo):    {top3(df)}")
    print(f"Top 3 bairros por yield (sem outliers): {top3(clean)}")
    print(
        f"ADR excluído (> P99 = R$ {adr_p99:,.0f}): "
        f"{int((df['adr'] > adr_p99).sum())} listings | "
        f"sale_price excluído (> P99 = R$ {price_p99:,.0f}): "
        f"{int((df['sale_price_mediano'] > price_p99).sum())} listings"
    )


def main() -> None:
    print("== 1. Outliers (fora de [P1, P99]) ==\n")
    out = outlier_report().copy()
    out[["P1", "P99"]] = out[["P1", "P99"]].map(lambda x: f"R$ {x:,.0f}")
    print(out.to_string(index=False))

    print("\n\n== 2. Missing por coluna-chave ==\n")
    print(missing_report().to_string(index=False))
    print(
        "\nEstratégia: condomínio/IPTU ausentes (~30%) entram como 0 só quando o grupo inteiro"
        "\n(bairro+tipo+quartos) não tem dado; caso contrário usa-se a mediana dos valores presentes."
    )

    print("\n\n== 3. Sensibilidade (yield/payback por cenário de ocupação, top 5 bairros) ==\n")
    sens = sensitivity_table().head(5).copy()
    for c in ["yield_50", "yield_60", "yield_70"]:
        sens[c] = sens[c].map(lambda x: "—" if pd.isna(x) else f"{x:.1%}")
    sens["payback_60"] = sens["payback_60"].map(lambda x: "—" if pd.isna(x) else f"{x:.1f}a")
    print(sens.to_string(index=False))

    print("\n\n== 4. Estabilidade do vencedor sem outliers ==\n")
    winner_stability()


if __name__ == "__main__":
    main()
