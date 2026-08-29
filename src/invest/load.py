"""Carregamento dos CSVs do desafio com detecção automática de encoding e delimitador."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

FILES = [
    "Details_Itapema.csv",
    "Hosts_ids_Itapema.csv",
    "Mesh_Ids_Data_Itapema.csv",
    "Price_AV_Itapema.csv",
    "VivaReal_Itapema.csv",
]

# Colunas-chave que devem ser lidas como texto para joins exatos.
ID_COLUMNS = {
    "Details_Itapema.csv": ["airbnb_listing_id", "owner_id"],
    "Hosts_ids_Itapema.csv": ["owner_id"],
    "Mesh_Ids_Data_Itapema.csv": ["airbnb_listing_id"],
    "Price_AV_Itapema.csv": ["airbnb_listing_id"],
    "VivaReal_Itapema.csv": ["listing_id"],
}

_ENCODINGS = ("utf-8-sig", "utf-8", "latin-1", "cp1252")


def detect_encoding(path: Path) -> str:
    """Tenta decodificar o arquivo com encodings comuns e retorna o primeiro que funciona."""
    raw = path.read_bytes()
    for enc in _ENCODINGS:
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível detectar o encoding de {path.name}")


def detect_delimiter(path: Path, encoding: str) -> str:
    """Detecta o delimitador via csv.Sniffer; fallback para vírgula."""
    with path.open(encoding=encoding, newline="") as fh:
        sample = fh.read(65536)
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def load_file(name: str) -> pd.DataFrame:
    """Carrega um CSV, aplicando detecção de encoding/delimitador e tratando <NA> como nulo."""
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Arquivo vazio (0 bytes): {name}")

    encoding = detect_encoding(path)
    delimiter = detect_delimiter(path, encoding)

    try:
        df = pd.read_csv(
            path,
            encoding=encoding,
            sep=delimiter,
            dtype={c: str for c in ID_COLUMNS.get(name, [])},
            na_values=["<NA>"],
            keep_default_na=True,
            low_memory=False,
        )
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Arquivo sem dados ou com header corrompido: {name}") from exc

    if len(df.columns) == 0:
        raise ValueError(f"Header não interpretável (0 colunas): {name}")

    return df


def load_all() -> dict[str, pd.DataFrame]:
    """Carrega todos os CSVs e retorna um dicionário nome -> DataFrame."""
    return {name: load_file(name) for name in FILES}


def main() -> None:
    frames = load_all()
    print("Carregamento concluído.\n")
    print(f"{'arquivo':<28} {'linhas':>8} {'colunas':>8}")
    print("-" * 46)
    for name, df in frames.items():
        print(f"{name:<28} {len(df):>8,} {df.shape[1]:>8}")
    print("-" * 46)
    print(f"{'TOTAL':<28} {sum(len(d) for d in frames.values()):>8,}")


if __name__ == "__main__":
    main()
