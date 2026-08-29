"""Q4/Q5 — Recomendação de investimento: yield, payback e posição sobre a tese."""

from __future__ import annotations

import unicodedata

import pandas as pd

from . import market, revenue

OCCUPANCIES = (0.50, 0.60, 0.70)

_VARIANTS = {
    "jardim praia mar": "jardim praiamar",
    "castelo branco": "casa branca",
    "tabuleiro": "tabuleiro dos oliveiras",
    "taboleiro": "tabuleiro dos oliveiras",
}


def normalize_suburb(s: object) -> str | None:
    """Normaliza nome de bairro (minúsculas, sem acento, sem 'frente mar', variantes)."""
    if pd.isna(s):
        return None
    t = str(s).strip().lower()
    if "frente mar" in t:
        t = t.split("-")[0].strip()
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    t = " ".join(t.split())
    return _VARIANTS.get(t, t)


def _group_medians(res: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    keys = ["suburb_norm", "listing_type", "bedrooms"]
    sale = res.groupby(keys)["sale_price"].median().rename("sale_price_mediano")
    condo = res.groupby(keys)["monthly_condo_fee"].median().rename("condo_mediano")
    iptu = res.groupby(keys)["yearly_iptu"].median().rename("iptu_mediano")
    return sale, condo, iptu


def build_investment() -> pd.DataFrame:
    """Anexa preço de venda, custo, yield e payback a cada listing Airbnb com receita."""
    rev, _ = revenue.estimate_revenue()
    v = market.load_vivareal()

    res = v[v["listing_type"].isin(market.RESIDENTIAL_TYPES) & (v["sale_price"] > 0)].copy()
    res["suburb_norm"] = res["suburb"].map(normalize_suburb)

    sale, condo, iptu = _group_medians(res)

    df = rev[~rev["sem_receita"]].copy()
    df["suburb_norm"] = df["suburb"].map(normalize_suburb)
    key = ["suburb_norm", "listing_type", "number_of_bedrooms"]

    df = df.merge(sale, left_on=key, right_index=True, how="left")
    df = df.merge(condo, left_on=key, right_index=True, how="left")
    df = df.merge(iptu, left_on=key, right_index=True, how="left")

    df["custo_anual"] = df["condo_mediano"].fillna(0) * 12 + df["iptu_mediano"].fillna(0)
    df["receita_liquida"] = df["receita_anual"] - df["custo_anual"]
    df["yield_anual"] = df["receita_liquida"] / df["sale_price_mediano"]
    df["payback_anos"] = df["sale_price_mediano"] / df["receita_liquida"]

    return df


def yield_by_suburb(df: pd.DataFrame) -> pd.DataFrame:
    g = (
        df.groupby("suburb_norm")
        .agg(
            yield_mediano=("yield_anual", "median"),
            payback_mediano=("payback_anos", "median"),
            receita_liquida_mediana=("receita_liquida", "median"),
            preco_mediano=("sale_price_mediano", "median"),
            n=("yield_anual", "count"),
        )
        .reset_index()
        .sort_values("yield_mediano", ascending=False, na_position="last")
    )
    g["amostra_pequena"] = g["n"] < 10
    return g


def thesis_table(df: pd.DataFrame) -> pd.DataFrame:
    """Yield mediano de apartamento 1Q (e 2Q) por bairro — foco da tese dos compactos."""
    compactos = df[df["listing_type"].eq("apartamento") & df["number_of_bedrooms"].le(2)]
    return (
        compactos.groupby(["suburb_norm", "number_of_bedrooms"])
        .agg(
            yield_mediano=("yield_anual", "median"),
            payback_mediano=("payback_anos", "median"),
            preco_mediano=("sale_price_mediano", "median"),
            receita_liquida_mediana=("receita_liquida", "median"),
            n=("yield_anual", "count"),
        )
        .reset_index()
        .sort_values("yield_mediano", ascending=False, na_position="last")
    )


def main() -> None:
    df = build_investment()

    print("Yield anual por BAIRRO (mediana), desc (só bairros com n ≥ 10):\n")
    by_suburb = yield_by_suburb(df)
    sub = by_suburb[~by_suburb["amostra_pequena"]].copy()
    for c in ["yield_mediano"]:
        sub[c] = sub[c].map(lambda x: "—" if pd.isna(x) else f"{x:.1%}")
    for c in ["receita_liquida_mediana", "preco_mediano"]:
        sub[c] = sub[c].map(lambda x: f"R$ {x:,.0f}")
    sub["payback_mediano"] = sub["payback_mediano"].map(lambda x: "—" if pd.isna(x) else f"{x:.1f}a")
    print(sub.to_string(index=False))

    print("\n\nTESE — apartamento compacto (0–2 quartos) por bairro (n ≥ 10):\n")
    tt = thesis_table(df)
    tt = tt[tt["n"] >= 10].copy()
    for c in ["yield_mediano"]:
        tt[c] = tt[c].map(lambda x: "—" if pd.isna(x) else f"{x:.1%}")
    for c in ["receita_liquida_mediana", "preco_mediano"]:
        tt[c] = tt[c].map(lambda x: f"R$ {x:,.0f}")
    tt["payback_mediano"] = tt["payback_mediano"].map(lambda x: "—" if pd.isna(x) else f"{x:.1f}a")
    print(tt.to_string(index=False))

    _print_example(df)


def _print_example(df: pd.DataFrame) -> None:
    """Seleciona um anúncio real do VivaReal representativo da recomendação (Morretes, ap 2Q)."""
    v = market.load_vivareal()
    res = v[v["listing_type"].eq("apartamento") & (v["sale_price"] > 0)].copy()
    res["suburb_norm"] = res["suburb"].map(normalize_suburb)
    alvo = res[res["suburb_norm"].eq("morretes") & res["bedrooms"].eq(2)]

    pick = alvo.sort_values("sale_price").iloc[len(alvo) // 2]

    # Custos usam a mediana do perfil (condomínio/IPTU do anúncio individual são erráticos, ex.: R$ 12).
    dfc = df[
        (df["suburb_norm"].eq("morretes"))
        & (df["listing_type"].eq("apartamento"))
        & (df["number_of_bedrooms"].eq(2))
    ]
    rev_ref = dfc["receita_anual"].median()
    condo = dfc["condo_mediano"].median() or 0
    iptu = dfc["iptu_mediano"].median() or 0
    custo = condo * 12 + iptu

    print("\n\nEXEMPLO CONCRETO (anúncio mediano do VivaReal — Morretes, ap 2Q):\n")
    print(f"  Título: {pick.get('listing_title')}")
    print(f"  Preço de venda: R$ {pick.get('sale_price'):,.0f}")
    print(f"  Área útil: {pick.get('usable_area')} m² | Quartos: {pick.get('bedrooms')}")
    print(f"  Custos (mediana do perfil): condomínio R$ {condo:,.0f}/mês + IPTU R$ {iptu:,.0f}/ano")
    print(f"  Receita bruta anual (mediana do perfil, 60%): R$ {rev_ref:,.0f}")
    for occ in OCCUPANCIES:
        r = rev_ref * (occ / revenue.DEFAULT_OCCUPANCY)
        y = (r - custo) / pick["sale_price"]
        pb = pick["sale_price"] / (r - custo)
        print(f"  ocupação {int(occ*100)}%: yield {y:.1%} | payback {pb:.1f} anos")


if __name__ == "__main__":
    main()
