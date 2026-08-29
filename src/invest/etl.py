"""Consolidação: junta Details + Mesh + Hosts, deduplica capturas e gera relatório de cobertura."""

from __future__ import annotations

import pandas as pd

from . import load


def dedup_latest(df: pd.DataFrame, id_col: str, date_col: str) -> pd.DataFrame:
    """Mantém apenas a captura mais recente (por date_col) de cada id_col."""
    return df.sort_values(date_col).drop_duplicates(subset=id_col, keep="last")


def build_listings() -> tuple[pd.DataFrame, dict]:
    """Consolida listings Airbnb com bairro (Mesh) e atributos do host (Hosts).

    Retorna (listings, cobertura) onde cobertura é um dicionário com as contagens
    que alimentam o relatório de cobertura.
    """
    frames = load.load_all()
    det = frames["Details_Itapema.csv"]
    mesh = frames["Mesh_Ids_Data_Itapema.csv"]
    hosts = frames["Hosts_ids_Itapema.csv"]
    price = frames["Price_AV_Itapema.csv"]

    report = {}

    # Dedup de capturas repetidas.
    det_dedup = dedup_latest(det, "airbnb_listing_id", "aquisition_date")
    mesh_dedup = dedup_latest(mesh, "airbnb_listing_id", "aquisition_date")
    hosts_dedup = dedup_latest(hosts, "owner_id", "host_snapshot_date")
    report["dedup_details_descartadas"] = len(det) - len(det_dedup)
    report["dedup_mesh_descartadas"] = len(mesh) - len(mesh_dedup)
    report["dedup_hosts_descartadas"] = len(hosts) - len(hosts_dedup)

    # Junta Details + bairro (Mesh) por listing.
    # Nota: não há backfill cross-source de suburb — Details não tem coluna de bairro e o
    # VivaReal é do lado de venda (outro espaço de ids). A única ausência real é o literal
    # "none" do Mesh (contado como "sem bairro" abaixo).
    base = det_dedup.merge(
        mesh_dedup[["airbnb_listing_id", "suburb"]],
        on="airbnb_listing_id",
        how="left",
        suffixes=("", "_mesh"),
    )

    # Junta atributos do host por owner_id.
    base = base.merge(hosts_dedup, on="owner_id", how="left", suffixes=("", "_host"))

    # Bairro nulo ou literal "none" conta como "sem bairro".
    sem_bairro = base["suburb"].isna() | (base["suburb"].astype(str).str.strip().str.lower() == "none")
    report["sem_bairro"] = int(sem_bairro.sum())

    # Cobertura de preço (listings que aparecem em Price_AV).
    ids_com_preco = set(price["airbnb_listing_id"].unique())
    report["com_preco"] = int(base["airbnb_listing_id"].isin(ids_com_preco).sum())
    report["sem_preco"] = int((~base["airbnb_listing_id"].isin(ids_com_preco)).sum())
    report["preco_orfao"] = int(len(ids_com_preco - set(base["airbnb_listing_id"].unique())))

    # Hosts órfãos (owner em Hosts sem listing em Details).
    report["hosts_orfãos"] = int(
        hosts_dedup[~hosts_dedup["owner_id"].isin(det_dedup["owner_id"])].shape[0]
    )

    report["total_listings"] = int(len(base))
    report["total_hosts"] = int(hosts_dedup["owner_id"].nunique())

    return base, report


def main() -> None:
    listings, cov = build_listings()
    print("Consolidação concluída.\n")
    print("== Dedup (linhas descartadas por captura repetida) ==")
    print(f"  Details: {cov['dedup_details_descartadas']}")
    print(f"  Mesh:    {cov['dedup_mesh_descartadas']}")
    print(f"  Hosts:   {cov['dedup_hosts_descartadas']}")

    print("\n== Relatório de cobertura ==")
    print(f"  Listings totais:           {cov['total_listings']}")
    print(f"  Hosts únicos:              {cov['total_hosts']}")
    print(f"  Sem bairro (nulo/'none'):  {cov['sem_bairro']}")
    print(f"  Listings com preço:        {cov['com_preco']}")
    print(f"  Listings sem preço:        {cov['sem_preco']}")
    print(f"  Preços órfãos (sem listing): {cov['preco_orfao']}")
    print(f"  Hosts órfãos:              {cov['hosts_orfãos']}")

    print("\n== Colunas consolidadas ==")
    print(", ".join(listings.columns))


if __name__ == "__main__":
    main()
